Overview
This project is a command-line interface (CLI) that securely interacts with a MySQL database. It includes:

AES encryption for sensitive fields

Bcrypt hashing for passwords

Hybrid encrypted backups (AES + RSA)

Integrity verification using SHA-256

Basic CRUD operations for Users, Feature Requests, and Comments

The goal is to demonstrate secure data handling, encryption at rest, and safe database interaction.

Features

Encryption
AES-256 encrypts PII (email, full name) before database storage.
Bcrypt hashes passwords; they are never stored in plaintext.

Secure Backup System
Uses hybrid encryption: AES encrypts the SQL dump, RSA encrypts the AES key.
Backup integrity is verified using a SHA-256 checksum.

CRUD Operations
The CLI supports:

Create and list users

Create and list feature requests

Create and list comments

Login System
MySQL credentials are entered once at startup and reused for all operations.

Project Structure
connect.py Main CLI application
encryption_utils.py AES, RSA, and bcrypt implementations
backup_utils.py Backup, restore, and integrity functions
aes.key AES key file (auto-generated)
rsa_keys/ RSA key pair used for backup encryption
backup_hash.txt SHA-256 hash for verifying backup integrity

Requirements
Install dependencies:

pip install mysql-connector-python cryptography bcrypt

Make sure MySQL tools (mysqldump and mysql) are installed and accessible.
If they are not in your PATH, update their paths in the code.

Running the Application
Run the CLI:

python connect.py

You will be asked for:

MySQL username

MySQL password

Database name

Once logged in, the main menu appears.

Backup and Restore

Backup (Encrypted)
Creates:

A plain SQL dump

An encrypted backup file (backup_encrypted.bin)

A hash file for integrity verification

Select menu option 8: Backup Database (Encrypted)

Restore
Decrypts and restores the encrypted backup:

Menu option 8: Restore Encrypted Backup

Verify Backup Integrity
Menu option 9: Verify Backup Integrity
Checks if the encrypted backup matches its stored SHA-256 hash.

Security Notes
Full names and emails are always AES-encrypted before storage.
Passwords are stored using bcrypt and cannot be decrypted.
No sensitive values (passwords, keys, PII) are logged.
AES key is stored in aes.key and reused to ensure proper decryption.
RSA keys are stored in rsa_keys/ and used to secure backup encryption.

Purpose
This program was created for an academic assignment focused on:

Data encryption and secure storage

Backup encryption

Integrity verification

Basic secure database operations
