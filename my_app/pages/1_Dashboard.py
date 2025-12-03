import streamlit as st
import sys
import os

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

#Import database connection function
from app.data.db import connect_database

#Import incident management functions
from app.data.incidents import (
    get_all_incidents,
    insert_incident,
    update_incident,
    delete_incident)

#Webpage title and icon
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

if "username" not in st.session_state:
    #Initialise username
    st.session_state.username = ""

# Check if user is logged in
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")

    #Button to go back to login/register page
    if st.button("Go to Login/Register page"):
        #Use the official navigation API to switch pages
        st.switch_page("Home.py")
        st.stop()

    #Stop further execution of the script
    st.stop()

# Dashboard content for logged-in users
st.title("Dashboard")

st.divider()

#Sidebar for domain selection
with st.sidebar:
    #Domain selection dropdown
    domain = st.selectbox("Choose a Domain", ["-- Select a Domain --", "Cyber Security", "Data Science", "IT Operations"], key="select_domain")

    #Line separator
    st.divider()

    if st.button("Log out"):
        # Clear session state variables related to login
        st.session_state.logged_in = False
        st.session_state.username = ""

        #Inform user of successful logout
        st.info("Logged out successfully.")

        # Redirect immediately to the login/register page
        st.switch_page("Home.py")

        #Stop further execution of the script
        st.stop()

#Verify if domain is selected
if domain == "-- Select a Domain --":
    #Display warning message
    st.warning("Please select a domain from the sidebar to continue.")
    #Stop whole execution of script
    st.stop()

else:
    #Connect to intelligence database
    conn = connect_database("DATA/intelligence.db")

    #Verify if domain is Cyber Security
    if domain == "Cyber Security":
        st.subheader("Cyber Security")

        #Fetch all incidents from database
        incidents = get_all_incidents()

        #Display incidents in a table
        st.dataframe(incidents, use_container_width=True)

        with st.form("new_incident"):
            type = st.text_input("Incident Type")
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            date = st.date_input("Date Reported")
            description = st.text_area("Description")
            
            submitted = st.form_submit_button("Add Incident")

            if submitted:
                insert_incident(date.strftime("%Y-%m-%d"), type, severity, status, description)
                st.success("New incident added successfully.")
                st.rerun

        conn.commit()
