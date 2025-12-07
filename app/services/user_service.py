import sqlite3
import bcrypt
from pathlib import Path

from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
from app.data.schema import create_users_table
from app.services.auth import USER_DATA_FILE

#Function to ensure that users table and database corresponds
def sync_user_to_file(username, password_hash, role):
    """Ensure DATA/users.txt contains user entry."""
    try:
        #Read whole file
        with open(USER_DATA_FILE, "r") as f:
            lines = f.readlines()
    
    #In case file not found, empty dictionary is created
    except FileNotFoundError:
        lines = []

    #Rewrite new line
    new_line = f"{username},{password_hash},{role}\n"
    #Initialise a flag to know about update
    updated = False

    #Iterate through each line
    for idx, line in enumerate(lines):
        #Verify if line starts with 'username,'
        if line.startswith(f"{username},"):
            #Add current line to dictionary
            lines[idx] = new_line
            #Change flag to True
            updated = True
            #Stop loop
            break

    #Add line to dictionary if flag is still False
    if not updated:
        lines.append(new_line)

    #Rewrite whole file
    with open(USER_DATA_FILE, "w") as f:
        f.writelines(lines)

def register_user(username, password, role="user"):
    """
    Register a new user in the database.

    This is a COMPLETE IMPLEMENTATION as an example.

    Args:
        username: User's login name
        password: Plain text password (will be hashed)
        role: User role (default: 'user')

    Returns:
        tuple: (success: bool, message: str)
    """

    #Create database connection and cursor object
    conn = connect_database()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."

    # Hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')

    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    conn.close()

    sync_user_to_file(username, password_hash, role)

    return True, f"User '{username}' registered successfully!"

def login_user(username, password):
    """
    Authenticate a user against the database.

    This is a COMPLETE IMPLEMENTATION as an example.

    Args:
        username: User's login name
        password: Plain text password to verify

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = connect_database()
    cursor = conn.cursor()

    # Find user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "Username not found."

    # Verify password (user[2] is password_hash column)
    stored_hash = user[2]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')

    if bcrypt.checkpw(password_bytes, hash_bytes):
        sync_user_to_file(username, stored_hash, user[3])
        return True, f"Welcome, {username}!"
    else:
        return False, "Invalid password."

def migrate_users_from_file(conn, filepath):
    """
    Migrate users from users.txt to the database.

    This is a COMPLETE IMPLEMENTATION as an example.

    Args:
        conn: Database connection
        filepath: Path to users.txt file
    """
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        print("   No users to migrate.")
        return

    cursor = conn.cursor()
    migrated_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse line: username,password_hash
            parts = line.split(",", 2)

            if len(parts) != 3:
                print(f"⚠️  Invalid line format: {line}")
                continue

            if len(parts) == 3:
                # Extract username, password_hash, and role
                username = parts[0]
                raw_hash = parts[1]
                role = parts[2]

                if raw_hash.startswith("b'") and raw_hash.endswith("'"):
                    password_hash = raw_hash[2:-1]
                else:
                    password_hash = raw_hash


                # Insert user (ignore if already exists)
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, role)
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")

    conn.commit()
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")

    # Verify users were migrated
    conn = connect_database()
    cursor = conn.cursor()

    # Query all users
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    print(" Users in database:")
    print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
    print("-" * 35)
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

    print(f"\nTotal users: {len(users)}")
    conn.close()
