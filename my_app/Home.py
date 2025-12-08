import streamlit as st
import os
import sys 

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from app.services.auth import (
    register_user,
    login_user,
    user_exists,
    validate_username,
    check_password_strength,
    valid_roles,)

from models.auth import User    #Import class User

from my_app.components.sidebar import logout_section

#Webpage title and icon
st.set_page_config(page_title="Login/Register", page_icon="🔐", layout="centered")

#Initialising session state variables
#Initialise login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#Initialise username
if "username" not in st.session_state:
    st.session_state.username = ""

#Initialise role
if "role" not in st.session_state:
    st.session_state.role = ""

#Verify if user is logged in
if st.session_state.logged_in:
    #Generate sidebar
    with st.sidebar:
        #Add a divider and logout section
        st.divider()
        logout_section()

st.title("Welcome")

# If already logged in, go straight to dashboard
if st.session_state.logged_in:
    #Inform user they are already logged in
    st.success(f"Already logged in as **{st.session_state.username}**.")
    #Button to go to dashboard
    if st.button("Go to dashboard"):
        # Use the official navigation API to switch pages
        st.switch_page("pages/1_Dashboard.py")
    #Stop further execution of the script
    st.stop()

# Tabs for Login and Register
tab_login, tab_register = st.tabs(["Login", "Register"])

#Login Tab
with tab_login:
    #Subheading
    st.subheader("Login to your account")

    #Prompt for username and password
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")


    # The login tab requires user to fill in both his username and password.
    # The program then reads all registered user in users.txt file and compares the password.

    #Login button
    if st.button("Login"):
        #Verify if fields are filled
        if not login_username or not login_password:
            #Display warning for incomplete fields
            st.warning("Please enter both username and password.")
        else:
            #Authenticate user
            is_authenticated, role_user = login_user(login_username, login_password)

            #Check authentication result
            if is_authenticated:
                #Set session state 
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.session_state.role = role_user

                #Success message for login
                st.success(f"Logged in as **{login_username}** ({role_user}).")

                #Button to go to dashboard
                if st.button("Go to dashboard"):
                    #Use official navigation API to switch pages
                    st.switch_page("pages/1_Dashboard.py")
            else:
                #Error message for login failure
                st.error(role_user or "Invalid username or password.")


#Register Tab
with tab_register:

    # The registration requires user to choose a username, role, password.

    # After writing of the credentials, the program validates the username and password to see if
    # they are in required format. 
    # The password strength is also checked.
    # Both passwords are compared to see if they match.


    #Subheading
    st.subheader("Create a new account")

    #Prompt user to enter new username and role
    new_username = st.text_input("Choose a username", key="register_username")
    user_role = st.selectbox("Select role", valid_roles, key="register_role")

    #Inform user about each role
    st.info(
        "Roles overview:\n"
        "- 'user' can access dashboards, analytics, and AI insights but cannot edit or delete any records.\n"
        "- 'analyst' manages data for their assigned domains (create/update/delete incidents, datasets, or tickets as needed).\n"
        "- 'admin' controls every domain plus platform settings (full CRUD, user governance, and configuration)."
    )

    #Prompt user to enter password
    new_password = st.text_input("Choose a password", type="password", key="register_password")

    #Prompt user to re-enter password
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
    
    #Inform user what password should contain
    st.info("Passwords must contain 7-50 characters and include at least one uppercase letter, "
             "one lowercase letter, one number, and one special character.")

    #Create account button
    if st.button("Create account"):
        #Input validation
        if not new_username or not new_password:
            #Incomplete fields
            st.warning("Please fill in all fields.")

        #Password confirmation
        elif new_password != confirm_password:
            #Password mismatch
            st.error("Passwords do not match. Please try again.")

        #Username and password validation
        else:
            #Validate username
            is_valid_username, username_error = validate_username(new_username)

            #Check if username is valid
            if not is_valid_username:
                #Display error message
                st.error(username_error)

            #Inform if username already exists
            elif user_exists(new_username):
                st.error("Username already exists. Choose a different one.")
            else:
                #Create object/instance for class User
                user_oop = User(new_username, "")
                #Validate password using method validate_password from class User
                is_valid_password, password_error = user_oop.validate_password(new_password)

                #Check if password is valid
                if not is_valid_password:
                    #Display error message
                    st.error(password_error)
                else:
                    #Check password strength
                    password_strength = check_password_strength(new_password)

                    #Verify if password is weak
                    if password_strength == "Weak":
                        #Display warning for weak password
                        st.warning("Password is too weak. Try using more varied characters.")
                    else:
                        #Register new username
                        success, message = register_user(new_username, new_password, user_role)

                        #Verify if user could be registered
                        if success:
                            #Success message
                            st.success(f"{message}")
                            st.info("Go to the Login tab to sign in.")
                        else:
                            #Error message
                            st.error(message or "Registration failed. Please try again.")