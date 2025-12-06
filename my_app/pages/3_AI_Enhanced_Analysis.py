import streamlit as st
from openai import OpenAI
import sys
import os

#Import incident management function
from app.data.incidents import get_all_incidents  

#Import database connection function
from app.data.db import connect_database

#Import logout function
from my_app.components.sidebar import logout_section



#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

#Initialise OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

#Webpage title and icon
st.set_page_config(page_title="AI-Enhanced Analysis", page_icon="🧠", layout="wide")

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

if "selected_domain" not in st.session_state:
    #Track the domain chosen on the dashboard
    st.session_state.selected_domain = None

# Check if user is logged in
if not st.session_state.logged_in:
    st.error("You must be logged in to view the AI Analyser page.")

    #Button to go back to login/register page
    if st.button("Go to Login/Register page"):
        #Use the official navigation API to switch pages
        st.switch_page("Home.py")
        st.stop()

    #Stop further execution of the script
    st.stop()

#Verify if user is logged in
if st.session_state.logged_in:
    #Generate sidebar
    with st.sidebar:
        #Add a divider and logout section
        st.divider()
        logout_section()

#AI Analyser content for logged-in users
st.title("AI-Enhanced Analysis")

#Retrieve domain from session state
domain = st.session_state.selected_domain

#Verify if user selected a domain
if not domain:
    #Error message for no domain selected
    st.error("Please select a domain on the sidebar of Dashboard before viewing AI Analysis.")

    #Button to navigate back to dashboard
    if st.button("Go to Dashboard"):
        st.switch_page("pages/1_Dashboard.py")

    #Stop execution of the whole script
    st.stop()

#Inform user about domain selected
st.info(f"Selected domain: **{domain}**")
st.divider()

#Fetch incidents from database
conn = connect_database()
incidents = get_all_incidents()

#Verify if function returned data
if incidents.empty == False:
    #Convert dataframe to dictionaries
    #Each inc becomes a dictionary
    incident_records = incidents.to_dict(orient="records")

    #Make each incident into a format (ID: type - severity)
    incident_options = [
        f"{inc['id']}: {inc['incident_type']} - {inc['severity']}" 
        for inc in incident_records]

    #Allow user to select incident by showing its ID, type and severity
    selected_idx = st.selectbox(
        "Select incident to analyse:",
        options=range(len(incident_records)),
        format_func=lambda i: incident_options[i],
    )

    #Get incident selected from dropdown
    incident = incident_records[selected_idx]

    # Display incident details
    st.subheader("Incident Details")
    st.write("**Type:**", incident["incident_type"])
    st.write("**Severity:**", incident["severity"])
    st.write("**Description:**", incident["description"])
    st.write("**Status:**", incident["status"])