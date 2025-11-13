import bcrypt
import os
import re

USER_DATA_FILE = "users.txt"

def hash_password(plain_text_password):
    password_bytes = plain_text_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password

def verify_password(plain_text_password, hashed_password):
    password_bytes = plain_text_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

def register_user(username, password):
    if user_exists(username):
        print(f"Error: Username '{username}' already exists")
        return False
    
    hashed_password = hash_password(password)

    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{hashed_password}\n")

    print(f"Success: User '{username}' registered successfully!")
    return True

def user_exists(username):
    try:
        with open(USER_DATA_FILE, "r") as f:
            for line in f:
                if line.startswith(f"{username},"):
                    return True
    except FileNotFoundError:
       return False

def login_user(username, password):
    try:
        with open(USER_DATA_FILE, "r") as f:
            for line in f.readlines():
                user, hash = line.strip().split(',', 1)
                hash = hash.strip()[2:-1]
                
                if user == username:
                    return verify_password(password, hash)
                else:
                    print(f"Error: Username {username} not found")
        return False
    except FileNotFoundError:
        return False

def validate_username(username):
    if not 3 <= len(username) <= 20:
        return False, "Username must contain between 3 and 20 characters"

    if not re.fullmatch(r"^[a-zA-Z0-9_]+$", username):
        return (False, "Username can only contain letters, numbers, and underscores(_)")
    return True, ""

def validate_password(password):
    if not 6 < len(password) < 50:
        return False, "Password must contain between 6 and 50 characters"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter (A-Z)"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter (a-z)"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit (0-9)"

    if not re.search(r"[a-zA-Z0-9\s]", password):
        return False, "Password must contain at least one special character"
    
    return True, ""

def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")
    
    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()
        
        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()

            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            register_user(username, password)

        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            if login_user(username, password):
                print("\nYou are now logged in.")
                print(f"Success: Welcome, {username}!")

                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")
            else:
                print("Error: Invalid password.")

        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break
        
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()