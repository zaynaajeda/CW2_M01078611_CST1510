from app.data.db import connect_database
from app.services.auth import USER_DATA_FILE, hash_password


def get_user_by_username(username):
    """Retrieve user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, role, domain FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def insert_user(username, password_hash, role="user", domain=None):
    """Insert new user."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role, domain) VALUES (?, ?, ?, ?)",
        (username, password_hash, role, domain)
    )
    conn.commit()
    conn.close()


def get_all_users():
    """Return all users as a list of dictionaries."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, domain FROM users ORDER BY username ASC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"username": row[0], "role": row[1], "domain": row[2]}
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
    domain_value = ""
    if updated:
        cursor.execute(
            "SELECT password_hash, domain FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            password_hash = row[0]
            domain_value = row[1] or ""
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

        parts = stripped.split(",", 3)
        if len(parts) < 3:
            updated_lines.append(raw_line)
            continue

        file_user, hash_value, _role = parts[:3]
        domain = parts[3] if len(parts) > 3 else ""
        if file_user == username:
            user_found_in_file = True
            current_domain = domain.strip() or domain_value
            updated_lines.append(f"{username},{hash_value},{new_role},{current_domain}\n")
        else:
            updated_lines.append(raw_line)

    if not user_found_in_file:
        updated_lines.append(f"{username},{password_hash},{new_role},{domain_value}\n")

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
        parts = stripped.split(",", 3)
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


def reset_user_password(username, new_password):
    """Reset a user's password and keep the database and users.txt in sync."""
    hashed_password = hash_password(new_password).decode("utf-8")

    #Create database connection and cursor object
    conn = connect_database()
    cursor = conn.cursor()


    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (hashed_password, username)
    )

    #Save changes
    conn.commit()
    #Get number of updated rows
    db_rows_updated = cursor.rowcount
    #Close database connection
    conn.close()

    #Read users.txt file
    try:
        with open(USER_DATA_FILE, "r") as f:
            #Read all lines
            lines = f.readlines()
    except FileNotFoundError:
        #Empty dictionary for all lines
        lines = []

    #Empty dictionary to keep track of updated line
    updated_lines = []
    #Set a flag to keep status of update of file
    file_updated = False

    #Iterate through each line that was in users.txt
    for raw_line in lines:
        #Remove spaces in line
        stripped = raw_line.strip()

        #Store line in updated lines and continue loop
        if not stripped:
            updated_lines.append(raw_line)
            continue

        #Divide line into 2 parts
        parts = stripped.split(",", 3)

        #Verify if line contains less than 3 parts
        if len(parts) < 3:
            #Store in updated lines and continue loop
            updated_lines.append(raw_line)
            continue

        #Store parts of line in variables
        file_user, _hash_value, role = parts[:3]
        domain = parts[3] if len(parts) > 3 else ""

        #Skip line and store in updated line if selected user does not match
        if file_user != username:
            updated_lines.append(raw_line)
            continue

        #if user is found, password is updated and new line is written in file
        updated_lines.append(f"{username},{hashed_password},{role},{domain.strip()}\n")
        #Set flag to true
        file_updated = True

    #Verify if flag is false or no rows were updated
    if not (db_rows_updated or file_updated):
        #Return False and error message to user
        return False, f"Username '{username}' not found."

    #Overwrite users.txt file if username was found
    if file_updated:
        with open(USER_DATA_FILE, "w") as f:
            f.writelines(updated_lines)

    #Return True and success message
    return True, "Password reset successfully."
