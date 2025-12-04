import streamlit as st
import sys
import os

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

from my_app.components.sidebar import logout_section

#Webpage title and icon
st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

if "selected_domain" not in st.session_state:
    #Track the domain chosen on the dashboard
    st.session_state.selected_domain = None

# Check if user is logged in
if not st.session_state.logged_in:
    st.error("You must be logged in to view analytics.")

    #Button to go back to login/register page
    if st.button("Go to Login/Register page"):
        #Use the official navigation API to switch pages
        st.switch_page("Home.py")
        st.stop()

    #Stop further execution of the script
    st.stop()

#Analytics content for logged-in users
st.title("Analytics")

#Retrieve domain from session state
domain = st.session_state.selected_domain

#Verify if user selected a domain
if not domain:
    #Error message for no domain selected
    st.error("Please select a domain on the sidebar of Dashboard before viewing analytics.")

    #Button to navigate back to dashboard
    if st.button("Go to Dashboard"):
        st.switch_page("pages/1_Dashboard.py")

    #Stop execution of the whole script
    st.stop()

#Inform user about domain selected
st.info(f"Selected domain: **{domain}**")

#Verify if user is logged in
if st.session_state.logged_in:
    #Generate sidebar
    with st.sidebar:
        #Add a divider and logout section
        st.divider()
        #Implement logout
        logout_section()