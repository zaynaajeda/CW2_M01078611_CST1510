import os
import sys
from pathlib import Path
import time

import streamlit as st

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

#Import functions from other folders
from app.data.db import connect_database
from my_app.components.sidebar import logout_section
from app.services.user_service import migrate_users_from_file
from app.services.auth import change_password, valid_roles, valid_analyst_domains, USER_DATA_FILE
from models.auth import User
from app.data.users import (get_all_users,
                            update_user_role,
                            delete_user,
                            reset_user_password)

#Webpage title and icon
st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

#Retrieve role of user from session state
role_user = st.session_state.role

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

if "username" not in st.session_state:
    #Initialise username
    st.session_state.username = ""

if "role" not in st.session_state:
    #Initialise role
    st.session_state.role = ""

if "analyst_domain" not in st.session_state:
    st.session_state.analyst_domain = ""

# Check if user is logged in
if not st.session_state.logged_in:
    st.error("You must be logged in to view the settings page.")

    #Button to go back to login/register page
    if st.button("Go to Login/Register page"):
        #Use the official navigation API to switch pages
        st.switch_page("Home.py")
        st.stop()

    #Stop further execution of the script
    st.stop()

#Settings content for logged-in users
st.title("Settings")
st.divider()

#Create database connection
conn = connect_database()

#Reload users table
migrate_users_from_file(conn, Path("DATA/users.txt"))

#Close database connection
conn.close()


#Verify if user is logged in
if st.session_state.logged_in:
    #Generate sidebar
    with st.sidebar:
        #Add a divider and logout section
        st.divider()
        logout_section()

st.markdown("#### Profile Information")

#Display login username and role
st.write(f"**Username:** {st.session_state.username or 'Unknown'}")
st.write(f"**Role:** {st.session_state.role or 'Unknown'}")
if st.session_state.role == "analyst":
    st.write(f"**Domain:** {st.session_state.analyst_domain or 'Unassigned'}")


st.markdown("##### Change Password")

#Form to change password
with st.form("change_password_form"):
    #Prompt user to enter current password and new password
    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    #Inform user what password should contain
    st.info("Passwords must contain 7-50 characters and include at least one uppercase letter, "
             "one lowercase letter, one number, and one special character.")

    #Button to update password
    submitted = st.form_submit_button("Update Password")
    
#Verify if form is submitted
if submitted:
    #Verify is all fields were filled
    if not current_password or not new_password or not confirm_password:
        #Warning message to inform user to enter all fields
        st.warning("Please fill in all password fields.")

    #Verify if current password were entered twice correctly
    elif new_password != confirm_password:
        st.error("New passwords do not match.")

    #Verify if new password matches old password
    elif new_password == current_password:
        st.warning("New password must be different from the current password.")

    #Continue execution if new password is correct
    else:
        #Create object/instance for class User
        user_oop = User(st.session_state.username, "")
        #Validate password using method validate_password from class User
        is_valid, validation_message = user_oop.validate_password(new_password)

        #Error message if password is not valid
        if not is_valid:
            st.error(validation_message)

        else:
            #Success message and update password
            success, message = change_password(st.session_state.username, current_password, new_password)

            if success:
                st.success(message)
                #Pause program for 1s
                time.sleep(1)
            else:
                st.error(message)

st.divider()
st.markdown("#### Users Management")

#Ensure that this section is only available to admins
if role_user == "admin":

    st.markdown("##### Overview of Users")

    #Fetch all users from database
    users = get_all_users()

    #Store all usernames in variable
    usernames = sorted({user["username"] for user in users})

    #Verify if database users exists
    if not users:
        #Inform user
        st.info("No registered users found.")
    else:
        #Display users in a table using placeholder for dynamic updates
        users_table = st.empty()
        users_table.dataframe(users, use_container_width=True)

        st.markdown("##### Update User Role")

        #Form to change role of user
        with st.form("admin_update_role"):
            #Prompt user to select username and new role
            selected_user = st.selectbox("Select user", usernames)
            new_role = st.selectbox("New role", valid_roles)

            #Choose domain if user clicked "analyst"
            domain_choice = st.selectbox("Analyst domain", valid_analyst_domains, key="settings_analyst_domain_select",
                                        help="Choose domain for analyst account.", disabled=new_role != "analyst")    # disabled part prevents user from accessing
                                                                                                                      # unless analyst is chosem
            selected_domain = domain_choice if new_role == "analyst" else None

            #Checkbox to confirm role update
            confirm_update = st.checkbox("Yes, update this user's role")

            #Submit button for form
            submit_role_update = st.form_submit_button("Update Role")

        #Verify if form is submitted
        if submit_role_update:
            #Verify is checkbox is ticked
            if not confirm_update:
                #Inform user to tick checkbox
                st.warning("Please confirm the role update before proceeding.")
            else:
                #Proceed with update of role
                success, msg = update_user_role(selected_user, new_role, selected_domain)

                #Check boolean value of success
                if success:
                    #Inform user about update of role
                    st.success(msg)
                    #Refresh users table to reflect updated role
                    updated_users = get_all_users()
                    users_table.dataframe(updated_users, use_container_width=True)
                    #Pause program for 1s
                    time.sleep(1)
                    #Rerun whole program
                    st.rerun()
                else:
                    #Error message
                    st.error(msg)

        st.markdown("##### Delete User")
        #Form to delete user
        with st.form("admin_delete_user"):
            #Prompt user to select username to delete
            user_to_delete = st.selectbox("Choose user to delete", usernames, key="delete_user_select")

            #Checkbox to confirm deletion
            confirm_delete = st.checkbox("Yes, delete this user")

            #Submit button for form
            submit_delete = st.form_submit_button("Delete User")

        #Verify if form is submitted
        if submit_delete:
            #Verify is checkbox is ticked
            if not confirm_delete:
                #Inform user to tick checkbox
                st.warning("Please confirm deletion before proceeding.")
            else:
                #Proceed with deletion of user
                success, msg = delete_user(user_to_delete)

                #Check boolean value of success
                if success:
                    #Inform user that username was deleted
                    st.success(msg)

                    #Verify if selected username corresponds to current login username
                    if user_to_delete == st.session_state.username:
                        #Inform user that his account was deleted
                        st.info("Your account was deleted. Please log in again with a different user.")

                        #Reset session state variables
                        st.session_state.logged_in = False
                        st.session_state.username = ""
                        st.session_state.role = ""
                        st.session_state.selected_domain = None

                    #Pause program for 1s
                    time.sleep(1)
                    #Rerun whole program
                    st.rerun()
                else:
                    #Error message
                    st.error(msg)

        st.markdown("##### Reset User Password")

        #Form to reset password
        with st.form("admin_reset_password"):
            #Prompt user to select username and enter new password
            reset_user = st.selectbox("Choose user", usernames)
            admin_new_password = st.text_input("New Password", type="password")
            admin_confirm_password = st.text_input("Confirm New Password", type="password")

            #Checkbox to confirm password reset
            confirm_reset = st.checkbox("Yes, reset this user's password")

            #Submit button for form
            submit_reset = st.form_submit_button("Reset Password")

            #Inform user what password should contain
            st.info("Passwords must contain 7-50 characters and include at least one uppercase letter, "
                    "one lowercase letter, one number, and one special character.")

        #Verify if form is submitted
        if submit_reset:
            #Verify is checkbox is ticked
            if not confirm_reset:
                #Inform user to tick checkbox
                st.warning("Please confirm the password reset before proceeding.")
            
            #Verify if all fields were entered
            elif not admin_new_password or not admin_confirm_password:
                #Inform user to fill in all fields
                st.warning("Please fill in the new password fields.")

            #Verify if both passwords entered match
            elif admin_new_password != admin_confirm_password:
                #Inform user about passwords not matching
                st.error("New passwords do not match.")
            else:
                #Create object/instance for class User
                admin_user = User(reset_user, "")
                #Validate password using method validate_password from class User
                is_valid, validation_message = admin_user.validate_password(admin_new_password)

                #Check if password is valid
                if not is_valid:
                    #Display error message
                    st.error(validation_message)
                else:
                    #Proceed with reset of password
                    success, msg = reset_user_password(reset_user, admin_new_password)

                    #Check boolean value of success
                    if success:
                        #Inform user that password reset was successful
                        st.success(msg)
                    else:
                        #Error message
                        st.error(msg)

#If user is not admin(analyst/user)
else:
    #Inform user that he has to be admin to access this section
    st.warning(f"You must be **admin** to have access to this section")
