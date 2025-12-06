import streamlit as st
from openai import OpenAI
import sys
import os

#Import all incidents from database
from app.data.incidents import get_all_incidents  

#Import all datasets from database
from app.data.datasets import get_all_datasets

#Import all tickets from database
from app.data.tickets import get_all_tickets

#Import database connection function
from app.data.db import connect_database

#Import logout function
from my_app.components.sidebar import logout_section

#Import system prompt generation for a specific domain
from my_app.components.ai_functions import get_ai_prompt, get_system_prompt

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
    st.error("You must be logged in to view the AI-Enhanced Analysis page.")

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

#Generate system prompt for selected domain
system_prompt = get_system_prompt(domain)

#Connect to database
conn = connect_database()

#Verify if domain is cyber security
if domain == "Cyber Security":
    #Fetch incidents from database
    incidents = get_all_incidents()

    #Verify if function returned data
    if incidents.empty == False:
        #Convert dataframe to dictionaries
        #Each inc becomes a dictionary
        incident_records = incidents.to_dict(orient="records")

        #Make each incident into a format (ID: type - severity)
        incident_options = [
            f"{inc['id']} : {inc['incident_type']} - {inc['severity']} - {inc['status']}" 
            for inc in incident_records]

        #Allow user to select incident by showing its ID, type and severity
        selected_idx = st.selectbox(
            "Select incident to analyse (ID : type - severity - status):",
            options=range(len(incident_records)),
            format_func=lambda i: incident_options[i],
        )

        #Get incident selected from dropdown
        incident = incident_records[selected_idx]

        
        # Display incident details
        st.markdown("#### Overview of Incident Details")
        st.write(f"**ID:** {incident['id']}")
        st.write(f"**Type:** {incident['incident_type']}")
        st.write(f"**Status:** {incident['status']}")
        st.write(f"**Severity:** {incident['severity']}")
        st.write(f"**Description:** {incident['description']}")

        st.divider()

        #Button to enable AI analysis
        if st.button("Allow AI Analysis", key="cyber-ai-analysis"):

            st.divider()

            #Get message prompt about incident details for AI analysis
            prompt = get_ai_prompt(domain, incident)

            #Send request to OpenAI
            response = client.chat.completions.create(
                model = "gpt-4o",
                messages = [
                    {"role":"system", "content":system_prompt},
                    {"role":"user", "content":prompt}]
                )
            
            #Retrieve AI output
            ai_response = response.choices[0].message.content

            #Display AI analysis
            st.markdown("#### AI-Enhanced Analysis")
            st.write(ai_response)

#Verify if domain is data science
if domain == "Data Science":
    #Fetch datasets from database
    datasets = get_all_datasets()

    #Verify if function returned data
    if datasets.empty == False:
        #Convert dataframe to dictionaries
        dataset_records = datasets.to_dict(orient="records")

        #Format dataset options for dropdown
        dataset_options = [
            f"{ds['id']} : {ds['dataset_name']} - {ds['category']} - {ds['record_count']} rows - {ds['column_count']} coulmns"
            for ds in dataset_records
        ]

        #Allow user to select dataset
        selected_idx = st.selectbox(
            "Select dataset to analyse (ID : name - category - rows - columns):",
            options=range(len(dataset_records)),
            format_func=lambda i: dataset_options[i],
        )

        #Get dataset selected from dropdown
        dataset = dataset_records[selected_idx]

        #Display dataset details
        st.markdown("#### Overview of Dataset Details")
        st.write(f"**ID:** {dataset['id']}")
        st.write(f"**Name:** {dataset['dataset_name']}")
        st.write(f"**Category:** {dataset['category']}")
        st.write(f"**Source:** {dataset['source']}")
        st.write(f"**Record Count:** {dataset['record_count']}")
        st.write(f"**Column Count:** {dataset['column_count']}")
        st.write(f"**File Size (MB):** {dataset['file_size_mb']}")
        st.write(f"**Last Updated:** {dataset['last_updated']}")

        st.divider()

        #Button to enable AI analysis
        if st.button("Allow AI Analysis", key="data-science-ai-analysis"):

            st.divider()

            #Get message prompt about dataset details for AI analysis
            prompt = get_ai_prompt(domain, dataset)

            #Send request to OpenAI
            response = client.chat.completions.create(
                model = "gpt-4o",
                messages = [
                    {"role":"system", "content":system_prompt},
                    {"role":"user", "content":prompt}]
                )

            #Retrieve AI output
            ai_response = response.choices[0].message.content

            #Display AI analysis
            st.markdown("#### AI-Enhanced Analysis")
            st.write(ai_response)

    else:
        #Inform user that no datasets are available
        st.info("No datasets available for analysis.")

#Verify if domain is IT operations
if domain == "IT Operations":
    #Fetch tickets from database
    tickets = get_all_tickets()

    #Verify if any tickets exist
    if tickets.empty == False:
        #Convert dataframe to dictionaries
        ticket_records = tickets.to_dict(orient="records")

        #Format ticket options for dropdown
        ticket_options = [
            f"{ticket['id']} : {ticket['subject']} - {ticket['priority']} - {ticket['status']}"
            for ticket in ticket_records
        ]

        #Allow user to select ticket
        selected_idx = st.selectbox(
            "Select ticket to analyse (ID: subject - priority - status):",
            options=range(len(ticket_records)),
            format_func=lambda i: ticket_options[i],
        )

        #Get ticket selected from dropdown
        ticket = ticket_records[selected_idx]

        #Display ticket details
        st.markdown("#### Overview of Ticket Details")
        st.write(f"**ID:** {ticket['id']}")
        st.write(f"**Subject:** {ticket['subject']}")
        st.write(f"**Priority:** {ticket['priority']}")
        st.write(f"**Status:** {ticket['status']}")
        st.write(f"**Category:** {ticket['category']}")
        st.write(f"**Resolved Date:** {ticket['resolved_date']}")
        st.write(f"**Assigned To:** {ticket['assigned_to']}")
        st.write(f"**Description:** {ticket['description']}")
        st.write(f"**Created Date:** {ticket['created_date']}")

        st.divider()

        #Button to enable AI analysis
        if st.button("Allow AI Analysis", key="it-ops-ai-analysis"):

            st.divider()

            #Get message prompt about ticket details for AI analysis
            prompt = get_ai_prompt(domain, ticket)

            #Send request to OpenAI
            response = client.chat.completions.create(
                model = "gpt-4o",
                messages = [
                    {"role":"system", "content":system_prompt},
                    {"role":"user", "content":prompt}]
                )

            #Retrieve AI output
            ai_response = response.choices[0].message.content

            #Display AI analysis
            st.markdown("#### AI-Enhanced Analysis")
            st.write(ai_response)

    else:
        #Inform user that no tickets are available
        st.info("No tickets available for analysis.")
