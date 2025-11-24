Overview
This project demonstrates secure data handling for a MySQL-backed system. It now includes:

- CLI for encrypted CRUD and backups
- REST API with JWT Authentication (AuthN) and role-based Authorization (AuthZ)
- PII controls: AES encryption at rest, masked responses/logging, hashed passwords
- Secure backups (AES + RSA) with integrity verification

PII Handling
- PII fields: email, full_name, password.
- Storage: email/full_name encrypted with AES-256; passwords hashed with bcrypt.
- Logging: PII values are never logged directly (masked or hashed).
- Responses: user endpoints return masked PII only.

Project Structure
- connect.py CLI application
- api.py REST API (Flask) with JWT AuthN/AuthZ and PII-safe responses
- encryption_utils.py AES, RSA, and bcrypt helpers
- backup_utils.py Backup, restore, and integrity functions
- aes.key AES key file (auto-generated)
- rsa_keys/ RSA key pair used for backup encryption
- backup_hash.txt SHA-256 hash for verifying backup integrity

Requirements
Install dependencies:

```
pip install flask PyJWT mysql-connector-python cryptography bcrypt
```

Make sure MySQL tools (mysqldump and mysql) are installed and accessible for CLI backup/restore. If they are not in your PATH, update their paths in connect.py.

Running the CLI
```
python connect.py
```
You will be asked for MySQL username, password, and database name once. The menu then provides CRUD and encrypted backup options.

Running the REST API
```
export DB_USER=...
export DB_PASSWORD=...
export DB_NAME=...
export JWT_SECRET=super-secret-value   # required for signing tokens
python api.py
```

AuthN/AuthZ model
- Login: POST /auth/login with `user_id` and `password` returns a JWT.
- Roles: `admin` can POST/PUT/DELETE; `user` can only GET.
- Send `Authorization: Bearer <token>` on all sensitive routes (all CRUD except /health).

REST endpoints
- Health: GET /health
- Users: GET /users, POST /users (admin), PUT /users/<id> (admin), DELETE /users/<id> (admin)
- Feature Requests: GET/POST/PUT/DELETE on /feature_requests and /feature_requests/<id> (POST/PUT/DELETE require admin)
- Comments: GET/POST/PUT/DELETE on /comments and /comments/<id> (POST/PUT/DELETE require admin)

Backup and Restore (CLI)
- Backup: creates SQL dump, encrypts it, and writes a SHA-256 integrity hash.
- Restore: decrypts and restores the encrypted backup.
- Verify: checks the encrypted backup against the stored hash.

Security Notes
- API error responses are generic (no stack traces); server logs keep stack traces server-side only.
- Tokens expire after JWT_EXP_MINUTES (default 60).
- Ensure the users table contains a `role` column (e.g., VARCHAR) for AuthZ.
