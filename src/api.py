import datetime
import hashlib
import logging
import os
import uuid
from functools import wraps
from typing import Any, Dict, List, Optional

import jwt
import mysql.connector
from flask import Flask, g, jsonify, request

from encryption_utils import aes_decrypt, aes_encrypt, hash_password, verify_password

# Basic config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))

PII_FIELDS = {"email", "full_name", "password"}

app = Flask(__name__)


# ------------------------------
# Helpers
# ------------------------------
def mask_email(email: Optional[str]) -> str:
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[:1]}***@{domain}"


def mask_name(name: Optional[str]) -> str:
    if not name:
        return "***"
    parts = name.split()
    masked_parts = [p[0] + "***" if p else "***" for p in parts]
    return " ".join(masked_parts)


def hash_for_log(value: Optional[str]) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode()).hexdigest()[:10]


def safe_decrypt(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    try:
        return aes_decrypt(value)
    except Exception:
        return None


def get_db():
    if not all(DB_CONFIG.values()):
        raise RuntimeError("Database credentials missing (DB_USER, DB_PASSWORD, DB_NAME required).")
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


@app.before_request
def add_request_id():
    g.request_id = str(uuid.uuid4())


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def generate_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXP_MINUTES),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def require_auth(roles: Optional[List[str]] = None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            token = auth_header.split(" ", 1)[1] if auth_header.startswith("Bearer ") else None
            if not token:
                return jsonify({"error": "missing or invalid Authorization header", "request_id": g.request_id}), 401
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "token expired", "request_id": g.request_id}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "invalid token", "request_id": g.request_id}), 401

            role = payload.get("role", "user")
            if roles and role not in roles:
                return jsonify({"error": "forbidden for role", "request_id": g.request_id}), 403

            g.current_user = payload
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def sanitized_user_row(row: Dict[str, Any]) -> Dict[str, Any]:
    email_plain = safe_decrypt(row.get("email"))
    full_name_plain = safe_decrypt(row.get("full_name"))
    return {
        "id": row.get("id"),
        "email": mask_email(email_plain),
        "full_name": mask_name(full_name_plain),
        "role": row.get("role", "user"),
    }


def bad_request(message: str):
    return jsonify({"error": message, "request_id": g.request_id}), 400


# ------------------------------
# Error handling
# ------------------------------
@app.errorhandler(Exception)
def handle_exception(err):
    logging.exception("Request %s failed: %s", g.get("request_id"), err)
    return jsonify({"error": "Internal server error", "request_id": g.get("request_id")}), 500


# ------------------------------
# Auth endpoints
# ------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "request_id": g.request_id})


@app.route("/auth/login", methods=["POST"])
def login():
    body = request.get_json(force=True, silent=True) or {}
    user_id = body.get("user_id")
    password = body.get("password")

    if not user_id or not password:
        return bad_request("user_id and password are required")

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, password_hash, role, email, full_name FROM users WHERE id = %s",
        (user_id,),
    )
    row = cursor.fetchone()
    cursor.close()

    if not row or not verify_password(password, row["password_hash"]):
        logging.warning("Invalid login for user %s (hash=%s)", user_id, hash_for_log(user_id))
        return jsonify({"error": "invalid credentials", "request_id": g.request_id}), 401

    role = row.get("role") or "user"
    token = generate_token(user_id=row["id"], role=role)

    logging.info("User %s logged in (role=%s)", hash_for_log(user_id), role)
    return jsonify(
        {
            "token": token,
            "role": role,
            "user": sanitized_user_row(row),
            "request_id": g.request_id,
        }
    )


# ------------------------------
# Users
# ------------------------------
@app.route("/users", methods=["GET"])
@require_auth(roles=["admin", "user"])
def get_users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, email, full_name, role FROM users")
    rows = cursor.fetchall()
    cursor.close()

    users = [sanitized_user_row(row) for row in rows]
    return jsonify({"users": users, "request_id": g.request_id})


@app.route("/users", methods=["POST"])
@require_auth(roles=["admin"])
def create_user():
    body = request.get_json(force=True, silent=True) or {}
    required_fields = {"id", "email", "password", "full_name"}
    missing = required_fields - body.keys()
    if missing:
        return bad_request(f"Missing fields: {', '.join(sorted(missing))}")

    email_encrypted = aes_encrypt(body["email"])
    full_name_encrypted = aes_encrypt(body["full_name"])
    password_hash = hash_password(body["password"])
    role = body.get("role", "user")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO users (id, email, password_hash, full_name, role)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (body["id"], email_encrypted, password_hash, full_name_encrypted, role),
    )
    db.commit()
    cursor.close()

    logging.info("Created user id=%s email_hash=%s", body["id"], hash_for_log(body["email"]))
    return jsonify(
        {
            "user": sanitized_user_row(
                {
                    "id": body["id"],
                    "email": email_encrypted,
                    "full_name": full_name_encrypted,
                    "role": role,
                }
            ),
            "request_id": g.request_id,
        }
    ), 201


@app.route("/users/<user_id>", methods=["PUT"])
@require_auth(roles=["admin"])
def update_user(user_id):
    body = request.get_json(force=True, silent=True) or {}
    allowed = {"email", "password", "full_name", "role"}
    updates = []
    params = []

    for field in allowed:
        if field not in body:
            continue
        if field == "email":
            updates.append("email = %s")
            params.append(aes_encrypt(body[field]))
        elif field == "full_name":
            updates.append("full_name = %s")
            params.append(aes_encrypt(body[field]))
        elif field == "password":
            updates.append("password_hash = %s")
            params.append(hash_password(body[field]))
        elif field == "role":
            updates.append("role = %s")
            params.append(body[field])

    if not updates:
        return bad_request("No valid fields to update.")

    params.append(user_id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", params)
    db.commit()
    cursor.close()

    logging.info("Updated user %s", hash_for_log(user_id))
    return jsonify({"status": "updated", "request_id": g.request_id})


@app.route("/users/<user_id>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()

    logging.info("Deleted user %s", hash_for_log(user_id))
    return jsonify({"status": "deleted", "request_id": g.request_id})


# ------------------------------
# Feature Requests
# ------------------------------
@app.route("/feature_requests", methods=["GET"])
@require_auth(roles=["admin", "user"])
def list_feature_requests():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, title, content, user_id FROM feature_requests")
    rows = cursor.fetchall()
    cursor.close()

    return jsonify({"feature_requests": rows, "request_id": g.request_id})


@app.route("/feature_requests", methods=["POST"])
@require_auth(roles=["admin"])
def create_feature_request():
    body = request.get_json(force=True, silent=True) or {}
    required = {"id", "title", "content", "user_id"}
    missing = required - body.keys()
    if missing:
        return bad_request(f"Missing fields: {', '.join(sorted(missing))}")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO feature_requests (id, title, content, user_id)
        VALUES (%s, %s, %s, %s)
        """,
        (body["id"], body["title"], body["content"], body["user_id"]),
    )
    db.commit()
    cursor.close()

    logging.info("Feature request %s created by %s", body["id"], hash_for_log(body["user_id"]))
    return jsonify({"status": "created", "id": body["id"], "request_id": g.request_id}), 201


@app.route("/feature_requests/<fr_id>", methods=["PUT"])
@require_auth(roles=["admin"])
def update_feature_request(fr_id):
    body = request.get_json(force=True, silent=True) or {}
    allowed = {"title", "content", "user_id"}
    updates = []
    params = []

    for field in allowed:
        if field in body:
            updates.append(f"{field} = %s")
            params.append(body[field])

    if not updates:
        return bad_request("No valid fields to update.")

    params.append(fr_id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"UPDATE feature_requests SET {', '.join(updates)} WHERE id = %s", params)
    db.commit()
    cursor.close()

    logging.info("Feature request %s updated", fr_id)
    return jsonify({"status": "updated", "request_id": g.request_id})


@app.route("/feature_requests/<fr_id>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_feature_request(fr_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM feature_requests WHERE id = %s", (fr_id,))
    db.commit()
    cursor.close()

    logging.info("Feature request %s deleted", fr_id)
    return jsonify({"status": "deleted", "request_id": g.request_id})


# ------------------------------
# Comments
# ------------------------------
@app.route("/comments", methods=["GET"])
@require_auth(roles=["admin", "user"])
def list_comments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, content, user_id, feature_request_id FROM comments")
    rows = cursor.fetchall()
    cursor.close()

    return jsonify({"comments": rows, "request_id": g.request_id})


@app.route("/comments", methods=["POST"])
@require_auth(roles=["admin"])
def create_comment():
    body = request.get_json(force=True, silent=True) or {}
    required = {"id", "content", "user_id", "feature_request_id"}
    missing = required - body.keys()
    if missing:
        return bad_request(f"Missing fields: {', '.join(sorted(missing))}")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO comments (id, content, user_id, feature_request_id)
        VALUES (%s, %s, %s, %s)
        """,
        (body["id"], body["content"], body["user_id"], body["feature_request_id"]),
    )
    db.commit()
    cursor.close()

    logging.info("Comment %s created by %s", body["id"], hash_for_log(body["user_id"]))
    return jsonify({"status": "created", "id": body["id"], "request_id": g.request_id}), 201


@app.route("/comments/<comment_id>", methods=["PUT"])
@require_auth(roles=["admin"])
def update_comment(comment_id):
    body = request.get_json(force=True, silent=True) or {}
    allowed = {"content", "user_id", "feature_request_id"}
    updates = []
    params = []

    for field in allowed:
        if field in body:
            updates.append(f"{field} = %s")
            params.append(body[field])

    if not updates:
        return bad_request("No valid fields to update.")

    params.append(comment_id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"UPDATE comments SET {', '.join(updates)} WHERE id = %s", params)
    db.commit()
    cursor.close()

    logging.info("Comment %s updated", comment_id)
    return jsonify({"status": "updated", "request_id": g.request_id})


@app.route("/comments/<comment_id>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_comment(comment_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
    db.commit()
    cursor.close()

    logging.info("Comment %s deleted", comment_id)
    return jsonify({"status": "deleted", "request_id": g.request_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
