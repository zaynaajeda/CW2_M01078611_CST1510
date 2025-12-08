import streamlit as st
from openai import OpenAI
import os
import sys

#Import all incidents from database
from app.data.incidents import (
    get_incidents_by_severity,
    get_incidents_by_status,
    get_incidents_by_type_count,
    get_incidents_over_time)

#Import class Cyberincident
from models.incidents import Cyberincident

#Import all datasets from database
from app.data.datasets import (
    get_all_datasets,
    get_dataset_column_counts,
    get_dataset_record_counts,
    get_datasets_by_category,
    get_datasets_by_source,
    get_datasets_over_time,
)

#Import all tickets from database
from app.data.tickets import (
    get_all_tickets,
    get_tickets_by_assigned_to,
    get_tickets_by_priority,
    get_tickets_by_status_count,
    get_tickets_over_time,
)

#Import database connection function
from app.data.db import connect_database

#Import logout function
from my_app.components.sidebar import logout_section

#Import system prompt generation for a specific domain
from my_app.components.ai_functions import get_ai_prompt, get_chart_prompt, get_system_prompt

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

#Initialise OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

#Retrieve role of user from session state
role_user = st.session_state.role

#Webpage title and icon
st.set_page_config(page_title="AI-Enhanced Analysis", page_icon="🧠", layout="wide")

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

if "selected_domain" not in st.session_state:
    #Track the domain chosen on the dashboard
    st.session_state.selected_domain = None

if "chart_ai_analysis" not in st.session_state:
    #Initialise AI response
    st.session_state.chart_ai_analysis = {}

if "role" not in st.session_state:
    #Initialise role
    st.session_state.role = ""

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

st.markdown("#### AI Analysis of Charts")

#Store chart data for selected domain from dashboard
domain_insights = {}

#Verify if domain is cyber security
if domain == "Cyber Security":
    #Create dictionary to store all records in cyber security
    #Each key contains a dashboard chart with its data as its value

    #Create object/instance for class Cyberincident
    incident_oop = Cyberincident()
    charts = {
        "incidents_over_time": get_incidents_over_time(conn),
        "incidents_by_type": get_incidents_by_type_count(conn),
        "incidents_by_status": get_incidents_by_status(conn),
        "incidents_by_severity": get_incidents_by_severity(conn),
        "all_incidents": incident_oop.get_all_incidents(),  #Fetches all incidents from database using method from class
    }

    #Iterate through dictionary charts
    #name represents key and df the value(dataframe)
    for name, df in charts.items():
        #Skip empty any dataframe
        if df is None or df.empty:
            continue

        #Convert dataframe to list of dictionaries
        domain_insights[name] = df.to_dict(orient="records")

#Verify if domain is data science
elif domain == "Data Science":
    #Create dictionaries to store all records in data science
    #Each key contains a dashboard chart with its data as its value as dataframe    
    charts = {
        "datasets_over_time": get_datasets_over_time(conn),
        "dataset_record_counts": get_dataset_record_counts(conn),
        "dataset_column_counts": get_dataset_column_counts(conn),
        "datasets_by_category": get_datasets_by_category(conn),
        "datasets_by_source": get_datasets_by_source(conn)}

    #Iterate through dictionary charts
    #name represents key and df the value(dataframe)
    for name, df in charts.items():
        #Skip empty any dataframe
        if df is None or df.empty:
            continue

        #Convert dataframe to list of dictionaries
        domain_insights[name] = df.to_dict(orient="records")

#Verify if domain is it operations
elif domain == "IT Operations":
    #Create dictionary to store all records in it operations
    #Each key contains a dashboard chart with its data as its value
    charts = {
        "tickets_over_time": get_tickets_over_time(conn),
        "tickets_by_assigned_to": get_tickets_by_assigned_to(conn),
        "tickets_by_priority": get_tickets_by_priority(conn),
        "tickets_by_status": get_tickets_by_status_count(conn)}

    #Iterate through dictionary charts
    #name represents key and df the value(dataframe)
    for name, df in charts.items():
        #Skip empty any dataframe
        if df is None or df.empty:
            continue

        #Convert dataframe to list of dictionaries
        domain_insights[name] = df.to_dict(orient="records")

#Close databse connection after all data has been retrieved
conn.close()

#Verify if chart data exists for AI analysis
if not domain_insights:
    #Inform user about unavailable chart data
    st.info("No chart data available for AI analysis.")
else:
    #Create button to generate AI analysis of charts
    if st.button("Generate AI Chart Analysis"):
        #Inform user that data is loading
        with st.spinner("Generating AI insights from dashboard charts..."):
            #Retrieve message prompt for user for AI chat
            chart_prompt = get_chart_prompt(domain, domain_insights)

            #Send request to OpenAI
            response = client.chat.completions.create(model="gpt-4o",
                                                        messages=[
                                                            {"role": "system", "content": system_prompt},
                                                            {"role": "user", "content": chart_prompt}])

            #Retrieve AI output
            st.session_state.chart_ai_analysis[domain] = response.choices[0].message.content

    #Use of variable to store response of AI
    analysis_text = st.session_state.chart_ai_analysis.get(domain)

    #Verify if response of AI exists
    if analysis_text:
        #Display AI analysis of selected dashboard charts
        st.write(analysis_text)

st.divider()

st.markdown("### AI-Enhanced Analysis of Record")

#Ensure that this section is only available to analysts and admins
if role_user == "analyst" or role_user == "admin":

    #Verify if domain is cyber security
    if domain == "Cyber Security":
        #Fetches all incidents from database using method from class
        incidents = incident_oop.get_all_incidents()


        #In case selectbox is skipped, there is no creation of records
        #Verify if function returned data
        if incidents.empty == False:
            #Convert dataframe to dictionaries
            #Each inc becomes a dictionary
            incident_records = incidents.to_dict(orient="records")

            #   Make each incident into a format (ID: type - severity) so that user can get
            #   more details about each incident for ai analysis
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
            record = incident_records[selected_idx]

            
            # Display incident details
            st.markdown("#### Overview of Incident Details")
            st.write(f"**ID:** {record['id']}")
            st.write(f"**Type:** {record['incident_type']}")
            st.write(f"**Status:** {record['status']}")
            st.write(f"**Severity:** {record['severity']}")
            st.write(f"**Description:** {record['description']}")

            st.divider()


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
            record = dataset_records[selected_idx]

            #Display dataset details
            st.markdown("#### Overview of Dataset Details")
            st.write(f"**ID:** {record['id']}")
            st.write(f"**Name:** {record['dataset_name']}")
            st.write(f"**Category:** {record['category']}")
            st.write(f"**Source:** {record['source']}")
            st.write(f"**Record Count:** {record['record_count']}")
            st.write(f"**Column Count:** {record['column_count']}")
            st.write(f"**File Size (MB):** {record['file_size_mb']}")
            st.write(f"**Last Updated:** {record['last_updated']}")

            st.divider()


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
            record = ticket_records[selected_idx]

            #Display ticket details
            st.markdown("#### Overview of Ticket Details")
            st.write(f"**ID:** {record['id']}")
            st.write(f"**Subject:** {record['subject']}")
            st.write(f"**Priority:** {record['priority']}")
            st.write(f"**Status:** {record['status']}")
            st.write(f"**Category:** {record['category']}")
            st.write(f"**Resolved Date:** {record['resolved_date']}")
            st.write(f"**Assigned To:** {record['assigned_to']}")
            st.write(f"**Description:** {record['description']}")
            st.write(f"**Created Date:** {record['created_date']}")

            st.divider()

    st.markdown("#### AI Analysis")
    #Button to enable AI analysis
    if st.button("Allow AI Analysis"):

        with st.spinner("Generating AI analysis for selected record..."):
            #Get message prompt about record details for AI analysis
            prompt = get_ai_prompt(domain, record)

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
        st.write(ai_response)

#If user is not admin(analyst/user)
else:
    #Inform user that he has to be admin to access this section
    st.warning(f"You must be **analyst** or **admin** to have access to this section")
