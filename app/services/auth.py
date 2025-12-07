import bcrypt
import re
import time
import secrets
from pathlib import Path

from app.data.db import connect_database

#Variables to store file paths
DATA_DIR = Path("DATA")
DATA_DIR.mkdir(parents=True, exist_ok=True)

#File to store username and hashed password
USER_DATA_FILE = DATA_DIR / "users.txt"
#File to store failed attempts and lockout of users
LOCKOUT_FILE = DATA_DIR / "lockouts.txt"
#File to store tokens and expiration time
SESSION_FILE = DATA_DIR / "sessions.txt"
#Number of attempts before lockout
MAX_ATTEMPTS = 3
#Lockout time of 5 minutes
LOCKOUT_DURATION_SECONDS = 300
#Session of 1 hour
SESSION_DURATION_SECONDS = 3600
#List to store available roles of user
valid_roles = ["user", "admin", "analyst"]

#Password hashing function
def hash_password(plain_text_password):
    #Encode password to bytes, required by bcrypt
    password_bytes = plain_text_password.encode('utf-8')
    #Generate a salt 
    salt = bcrypt.gensalt()
    #Hash password
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    #Return hashed password
    return hashed_password

#Password verification function
def verify_password(plain_text_password, hashed_password):
    #Encode both plaintext password and stored hash to bytes
    password_bytes = plain_text_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    #Compare both passwords
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

#Registration function
def register_user(username, password, role):
    #Verify if role is valid
    if role not in valid_roles:
        #Return False and error message for invalid role
        return False, f"Invalid role '{role}'."

    #Check if username already exists
    if user_exists(username):
        #Return False and error message for existing username
        return False, f"Username '{username}' already exists."

    #Hash password
    hashed_password = hash_password(password).decode("utf-8")

    #Store username, hashed password and role in file
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{hashed_password},{role}\n")

    #Mirror user into database so admin panel stays in sync
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed_password, role)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    #Return True and success message
    return True, f"Username '{username}' registered successfully as {role}!"

#User existence check
def user_exists(username):
    #Try-Except to verify existence of users.txt
    try:
        #Verify presence of username in file users.txt
        with open(USER_DATA_FILE, "r") as f:
            #Iterating over each line in file
            for line in f:
                #Check if username is present
                #Line starts with 'username'
                if line.startswith(f"{username},"):
                    return True
    except FileNotFoundError:
       return False

#Login function
def login_user(username, password):
    #Check lockout status of user
    is_unlocked, remaining_time = manage_lockout_status(username, 'check')

    #Handle case where account is locked
    if not is_unlocked:
        return False, f"Account is locked. Try again in {remaining_time} seconds."

    #Error handling for existence of users.txt
    try:
        with open(USER_DATA_FILE, "r") as f:
            #Iterate through each line in file
            for line in f:
                #Remove leading/trailing whitespace
                line = line.strip()
                #Skip empty lines
                if not line:
                    continue

                #Split line into username, hashed password and role
                user, hash_value, role = line.split(',', 2)
                #Clean up hash value
                hash_pass = hash_value.strip()

                #Remove b prefix and ending ' in hashed password if present
                if hash_pass.startswith("b'") and hash_pass.endswith("'"):
                    hash_pass = hash_pass[2:-1]

                #Check if username matches
                if user == username:
                    #Verify password
                    if verify_password(password, hash_pass):
                        #Reset lockout status on successful login
                        manage_lockout_status(username, 'reset')
                        return True, role

                    #Handle invalid password
                    else:
                        #Increment failed attempts
                        manage_lockout_status(username, 'increment_fail')
                        #Return False and error message
                        return False, "Invalid password."

        #Username not found
        return False, f"Username '{username}' not found."
    except FileNotFoundError:
        return False, "No users have been registered yet."

#Function to change user password
def change_password(username, current_password, new_password):
    """
    Update an existing user's password after validating the current password.
    """
    #Verify if users.txt exists
    try:
        #Open users.txt to read existing user data
        with open(USER_DATA_FILE, "r") as f:
            #Read all lines from file
            lines = f.readlines()

    except FileNotFoundError:
        #Return False if file does not exist
        return False, "No users have been registered yet."

    #List to store updated lines
    updated_lines = []
    #Flag to check if user is found
    user_found = False

    #Iterate through each line in file
    for raw_line in lines:
        #Remove spaces
        line = raw_line.strip()

        #Skip empty lines
        if not line:
            updated_lines.append(raw_line)
            continue

        #Split line into username, hashed password and role
        parts = line.split(",", 2)
        if len(parts) < 3:
            updated_lines.append(raw_line)
            continue

        #Store username, hashed password and role in variables
        user, hash_value, role = parts

        #Check if username matches
        if user != username:
            updated_lines.append(raw_line)
            continue
        
        #Return True if user is found
        user_found = True

        #Remove space in hashed password
        hash_pass = hash_value.strip()

        #Remove b prefix and ending ' from hashed password
        if hash_pass.startswith("b'") and hash_pass.endswith("'"):
            hash_pass = hash_pass[2:-1]

        #Case when password does not match
        if not verify_password(current_password, hash_pass):
            return False, "Current password is incorrect."

        #Change hashed password into new one
        new_hash = hash_password(new_password).decode("utf-8")
        updated_lines.append(f"{username},{new_hash},{role.strip()}\n")

    #Case for user not found
    if not user_found:
        return False, f"Username '{username}' not found."

    #Update users.txt
    with open(USER_DATA_FILE, "w") as f:
        f.writelines(updated_lines)

    #Return success message
    return True, "Password updated successfully."

#Username validation function
def validate_username(username):
    #Check length of username
    if not 3 <= len(username) <= 20:
        #Tuple return with False and error message
        return False, "Username must contain between 3 and 20 characters"

    #Check for allowed characters in username
    if not re.fullmatch(r"^[a-zA-Z0-9_]+$", username):
        return (False, "Username can only contain letters, numbers, and underscores(_)")
    return True, ""

#Password validation function
def validate_password(password):
    #Check length of password
    if not 6 < len(password) < 50:
        return False, "Password must contain between 6 and 50 characters"

    #Check for at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter (A-Z)"

    #Check for at least one lowercase letter
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter (a-z)"

    #Check for at least one digit
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit (0-9)"

    #Check for at least one special character
    if not re.search(r"[a-zA-Z0-9\s]", password):
        return False, "Password must contain at least one special character"
    
    #If all checks pass, return True
    return True, ""

#Function to determine strength of password
def check_password_strength(password):
    #Use of score to evaluate password strength
    score = 0

    #Length check
    if len(password) >= 12:
        #Gives more weight to a good length
        score += 2
    else:
        #Password of length 6-11 is not strong
        score += 1

    #Check if password contains at least one uppercase letter
    if re.search("[A-Z]", password):
        score += 1

    #Check if password contains at least one lowercase letter
    if re.search("[a-z]", password):
        score += 1

    #Check if password contains at least one digit
    if re.search("[0-9]", password):
        score += 1

    #Check if password contains at least one special character
    if re.search(r"[^a-zA-Z0-9\s]", password):
        score += 1

    #Conditional statements to determine password strength 
    #Max score = 6
    if score >= 5:
        return "Strong"
    elif score >= 3:
        return "Medium"
    else:
        return "Weak"

#Function to manage lockout status of user
def manage_lockout_status(username, action):
    #Empty dictionary to store lockout data
    lockouts = {}

    #Read lockout data from file
    try:
        with open(LOCKOUT_FILE,"r") as f:
            #Iterate through each line in file
            for line in f:
                #Store user, attempts and timestamp in variables
                user, attempts, timestamp = line.strip().split(',')
                #Add data to dictionary
                lockouts[user] = {'attempts': int(attempts), 'timestamp': float(timestamp)}
    #Exception handling in case file does not exist
    except FileNotFoundError:
        pass

    #Get current time
    current_time = time.time()
    #Get user status from dictionary, defaulting to 0 attempts and 0 timestamp
    user_status = lockouts.get(username, {'attempts': 0, 'timestamp': 0.0})

    #Check if user is currently locked out
    if user_status['timestamp'] > current_time:
        #Calculate remaining lockout time
        remaining_time = int(user_status['timestamp'] - current_time)
        #Tuple return with False and remaining time
        return (False, remaining_time)
    
    #Perform action based on input
    if action == 'increment_fail':
        #Increment failed attempts
        user_status['attempts'] += 1

        #Check if maximum attempts reached
        if user_status['attempts'] >= MAX_ATTEMPTS:
            #Set lockout timestamp
            user_status['timestamp'] = current_time + LOCKOUT_DURATION_SECONDS
            #Reset attempts after lockout
            user_status['attempts'] = 0

            #Inform user about lockout
            print(f"Account for user {username} is locked for 5 minutes.")

    #Reset attempts and timestamp after successful login
    elif action == 'reset':
        #Reset attempts and timestamp
        user_status['attempts'] = 0
        user_status['timestamp'] = 0.0

    #Save updated lockout data back to file
    lockouts[username] = user_status
    with open(LOCKOUT_FILE, "w") as f:
        for user, status in lockouts.items():
            f.write(f"{user}, {status['attempts']},{status['timestamp']}\n")

    #Return tuple indicating user is not locked out
    return (True, 0)

#Function to generate unique token and save to a new file
def create_session(username):
    token = secrets.token_hex(16)
    #Calculate expiry time by adding current time with 1 hour
    expiry_time = time.time() + SESSION_DURATION_SECONDS

    try:
        #Store token and expiry time of user in file
        with open(SESSION_FILE, "a") as f:
            f.write(f"{token},{username},{expiry_time}\n")

        #Inform user about his successfully created session
        print(f"Session successfully created for user '{username}'. Token: {token[:8]}")
        return token
    
    #Exception handling in case file could not be created
    except Exception as e:
        print(f"Error creating file: {e}")
        return None

#Function to check for an existing function and its expiration status
def validate_session(token):
    #Generate current time
    current_time = time.time()
    #Creation of empty list
    valid_sessions = []
    #Initialise variables to avoid errors in case no token for user exists
    found_user = None
    is_valid = False

    #Exception handling in case file does not exist
    try:
        with open(SESSION_FILE, "r") as f:
            #Iterating through each line in file
            for line in f:
                #Store token and expiry time of user in variables
                tkn, user, expiry = line.strip().split(',')
                #Convert expiry time to float data type
                expiry = float(expiry)

                #Check for expiration
                if expiry > current_time:
                    #Verify if token matches
                    if tkn == token:
                        #Return True and username
                        is_valid = True
                        found_user = user
                    #Adding current line in file to list
                    valid_sessions.append(line)

        #Rewrite sessions file to remove any expired tokens
        with open(SESSION_FILE, "w") as f:
            f.writelines(valid_sessions)

        #Return boolean value and username
        return is_valid, found_user
    except FileNotFoundError:
        return False, None

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
            #Display error message if username is invalid
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            #User role selection
            print("\n--- USER ROLE SELECTION ---")
            user_role = input("Enter user role (user/admin/analyst): ")
            #Convert role to lowercase
            user_role = user_role.lower()

            #Validate user role
            while user_role not in valid_roles:
                print("Warning: Invalid role.")
                #Prompt user to enter a valid role
                user_role = input("Enter user role (user/admin/analyst): ")

            #Prompt user to enter password
            password = input("\nEnter a password: ").strip()

            # Validate password
            is_valid, error_msg = validate_password(password)

            #Display error message if password is invalid
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
                
            #Output password strength    
            print("\n--- PASSWORD STRENGTH CHECK ---")
            print(f"Password Strength: {check_password_strength(password)}")

            #Prompt user to enter a stronger password if password is weak
            while check_password_strength(password) == 'Weak':
                print('Warning: Password is not strong enough. It must contain one uppercase letter, lowercase letter, digit, special character.')

                #Prompt user to enter a new password
                password = input("Enter a password: ").strip()

                # Validate password
                is_valid, error_msg = validate_password(password)
                #Display error message if password is invalid
                if not is_valid:
                    print(f"Error: {error_msg}")
                    continue

            # Confirm password
            password_confirm = input("\nConfirm password: ").strip()
            #Error message for non-matching passwords
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            success, message = register_user(username, password, user_role)
            print(message)

        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            is_logged_in, role_or_message = login_user(username, password)

            #Successful login
            if is_logged_in:
                #Inform user about successful login and his role
                print("\nYou are now logged in.")
                print(f"Success: Welcome, {username}!")
                print(f"Role: {role_or_message}")

                #Create a session token
                session_token = create_session(username)

                #Verify if session token was created
                if session_token:
                    #Informs user about his session token
                    print("\n--- Session Token Created ---")
                    print(f"Your temporary session token is **{session_token}**")
                    print("This token could be used for authenticated access.")
                    print("-"*50)

                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")
            else:
                print(role_or_message)

        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break
        
        else:
            # Invalid option
            print("\nError: Invalid option. Please select 1, 2, or 3.")

#Run the main function
if __name__ == "__main__":
    main()
