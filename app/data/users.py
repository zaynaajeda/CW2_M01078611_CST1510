from app.data.db import connect_database
from app.services.auth import USER_DATA_FILE


def get_user_by_username(username):
    """Retrieve user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def insert_user(username, password_hash, role="user"):
    """Insert new user."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    conn.close()


def get_all_users():
    """Return all users as a list of dictionaries."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users ORDER BY username ASC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"username": row[0], "role": row[1]}
        for row in rows
    ]


def update_user_role(username, new_role):
    """Update role for a given user."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET role = ? WHERE username = ?",
        (new_role, username)
    )
    conn.commit()
    updated = cursor.rowcount

    password_hash = ""
    if updated:
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            password_hash = row[0]
    conn.close()

    if not updated:
        return False, f"Username '{username}' not found."

    #Mirror change into users.txt
    try:
        with open(USER_DATA_FILE, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    updated_lines = []
    user_found_in_file = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            updated_lines.append(raw_line)
            continue

        parts = stripped.split(",", 2)
        if len(parts) < 3:
            updated_lines.append(raw_line)
            continue

        file_user, hash_value, _role = parts
        if file_user == username:
            user_found_in_file = True
            updated_lines.append(f"{username},{hash_value},{new_role}\n")
        else:
            updated_lines.append(raw_line)

    if not user_found_in_file:
        updated_lines.append(f"{username},{password_hash},{new_role}\n")

    with open(USER_DATA_FILE, "w") as f:
        f.writelines(updated_lines)

    return True, f"Updated role for {username} to {new_role}."


def delete_user(username):
    """Delete user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if not deleted:
        return False, f"Username '{username}' not found."

    #Remove from users.txt
    try:
        with open(USER_DATA_FILE, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    updated_lines = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        parts = stripped.split(",", 2)
        if len(parts) < 3:
            updated_lines.append(raw_line)
            continue
        file_user = parts[0]
        if file_user == username:
            continue
        updated_lines.append(raw_line)

    with open(USER_DATA_FILE, "w") as f:
        f.writelines(updated_lines)

    return True, f"User '{username}' deleted successfully."
