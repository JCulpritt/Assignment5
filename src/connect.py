import os
import sys
import mysql.connector
from encryption_utils import aes_encrypt, aes_decrypt, hash_password
from backup_utils import encrypt_backup, decrypt_backup, sha256_file, verify_backup_hash

MYSQLDUMP = "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe"
MYSQL = "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe"



DB_USER = None
DB_PASSWORD = None
DB_NAME = None

def login():
    print("=== MySQL Login ===")
    db_user = input("MySQL Username: ")
    db_password = input("MySQL Password: ")
    db_name = input("Database Name: ")
    return db_user, db_password, db_name

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def backup_database():
    sql_file = "backup.sql"
    enc_file = "backup_encrypted.bin"

    print("Creating SQL dump...")
    os.system(f"\"{MYSQLDUMP}\" -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} > {sql_file}")

    print("Encrypting backup...")
    encrypt_backup(sql_file, enc_file)

    # Generate integrity hash
    backup_hash = sha256_file(enc_file)
    with open("backup_hash.txt", "w") as f:
        f.write(backup_hash)

    print("\nBackup complete:")
    print(f"Encrypted File: {enc_file}")
    print(f"Integrity Hash stored in backup_hash.txt\n")

def restore_backup():
    enc_file = "backup_encrypted.bin"
    restored_sql = "restored_backup.sql"

    print("Decrypting backup...")
    decrypt_backup(enc_file, restored_sql)

    print("Restoring DB...")
    os.system(f"\"{MYSQL}\" -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} < {restored_sql}")

    print("Database restored successfully.\n")

def verify_backup():
    enc_file = "backup_encrypted.bin"

    with open("backup_hash.txt", "r") as f:
        stored_hash = f.read().strip()

    if verify_backup_hash(enc_file, stored_hash):
        print("Backup integrity verified: OK")
    else:
        print("WARNING: Backup has been altered or corrupted!")



# -------------------------------
#  CREATE USER (WITH ENCRYPTION)
# -------------------------------
def create_user():
    db = connect_db()
    cursor = db.cursor()

    user_id = input("User ID: ")
    email = aes_encrypt(input("Email: "))
    full_name = aes_encrypt(input("Full Name: "))
    password_hash = hash_password(input("Password: "))

    cursor.execute("""
        INSERT INTO users (id, email, password_hash, full_name)
        VALUES (%s, %s, %s, %s)
    """, (user_id, email, password_hash, full_name))

    db.commit()
    cursor.close()
    db.close()

    print("User created with encrypted PII.\n")


def list_users():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, email, full_name FROM users")
    rows = cursor.fetchall()

    print("\n--- USERS (DECRYPTED VIEW) ---")
    for row in rows:
        try:
            email = aes_decrypt(row[1])
            name = aes_decrypt(row[2])
        except:
            email = "<decrypt error>"
            name = "<decrypt error>"

        print(row[0], email, name)

    cursor.close()
    db.close()
    print()



# -------------------------------
#  FEATURE REQUEST CRUD
# -------------------------------
def create_feature():
    db = connect_db()
    cursor = db.cursor()

    fr_id = input("Feature Request id: ")
    title = input("Title: ")
    content = input("Content: ")
    user_id = input("User ID: ")

    cursor.execute("""
        INSERT INTO feature_requests (id, title, content, user_id)
        VALUES (%s, %s, %s, %s)
    """, (fr_id, title, content, user_id))

    db.commit()
    cursor.close()
    db.close()

    print("Feature Request created.\n")


def list_features():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, title, user_id FROM feature_requests")
    rows = cursor.fetchall()

    print("\n--- FEATURE REQUESTS ---")
    for row in rows:
        print(row)

    cursor.close()
    db.close()
    print()


# -------------------------------
#  COMMENTS CRUD
# -------------------------------
def create_comment():
    db = connect_db()
    cursor = db.cursor()

    cid = input("Comment id: ")
    content = input("Content: ")
    user_id = input("User id: ")
    fr_id = input("Feature Request id: ")

    cursor.execute("""
        INSERT INTO comments (id, content, user_id, feature_request_id)
        VALUES (%s, %s, %s, %s)
    """, (cid, content, user_id, fr_id))

    db.commit()
    cursor.close()
    db.close()

    print("Comment created.\n")


def list_comments():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, content, user_id FROM comments")
    rows = cursor.fetchall()

    print("\n--- COMMENTS ---")
    for row in rows:
        print(row)

    cursor.close()
    db.close()
    print()


# -------------------------------
#  MENU SYSTEM
# -------------------------------
def main_menu():
    while True:
        print("""
==============================
 SIMPLE DATABASE CLI (MySQL)
==============================
1. Create User
2. List Users
3. Create Feature Request
4. List Feature Requests
5. Create Comment
6. List Comments
7. Backup Database (Encrypted)
8. Restore Encrypted Backup
9. Verify Backup Integrity
0. Exit
""")

        choice = input("Choose an option: ")

        if choice == "1":
            create_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            create_feature()
        elif choice == "4":
            list_features()
        elif choice == "5":
            create_comment()
        elif choice == "6":
            list_comments()
        elif choice == "7":
            backup_database()
        elif choice == "8":
            restore_backup()
        elif choice == "9":
            verify_backup()
        elif choice == "0":
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice, try again.\n")


if __name__ == "__main__":
    DB_USER, DB_PASSWORD, DB_NAME = login()
    main_menu()
