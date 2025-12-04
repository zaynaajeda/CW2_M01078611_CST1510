import streamlit as st
import sys
import os

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

from app.services.auth import validate_password, change_password
from my_app.components.sidebar import logout_section

#Webpage title and icon
st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

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


st.markdown("##### Change Password")

#Form to change password
with st.form("change_password_form"):
    #Prompt user to enter current password and new password
    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

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
        #Validate new password
        is_valid, validation_message = validate_password(new_password)

        #Error message if password is not valid
        if not is_valid:
            st.error(validation_message)

        else:
            #Success message and update password
            success, message = change_password(
                st.session_state.username, current_password, new_password
            )
            if success:
                st.success(message)
            else:
                st.error(message)
