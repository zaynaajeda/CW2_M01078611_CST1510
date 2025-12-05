import streamlit as st
import sys
import os
import time

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
    delete_incident,
    get_open_incidents,
    get_high_or_critical_incidents)

from app.data.datasets import (
    get_all_datasets,
    insert_dataset,
    update_dataset,
    delete_dataset,
    get_large_datasets_by_source,
    get_large_columns_datasets)

from my_app.components.sidebar import logout_section

#Webpage title and icon
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

if "username" not in st.session_state:
    #Initialise username
    st.session_state.username = ""

#Track the currently selected domain so other pages can reuse it
if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = None

#Ensure previous threats are initialised
if "previous_threats" not in st.session_state:
    st.session_state.previous_threats = None

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

#List to store values in domain
domain_options = ["-- Select a Domain --", "Cyber Security", "Data Science", "IT Operations"]
#Fetch any data from domain if previously selected
stored_domain = st.session_state.get("selected_domain")
#Derive selectbox default index so dropdown shows the stored domain
default_index = domain_options.index(stored_domain) if stored_domain in domain_options else 0

#Sidebar for domain selection
with st.sidebar:

    st.subheader("Navigation")

    #Domain selection dropdown (pre-populated if user already picked one)
    domain = st.selectbox("Choose a Domain", domain_options, index=default_index, key="select_domain")

    #Line separator
    st.divider()
    #Implement logout
    logout_section()

#Verify if domain is selected
if domain == "-- Select a Domain --":
    #Display warning message
    st.warning("Please select a domain from the sidebar to continue.")
    st.session_state.selected_domain = None
    #Stop whole execution of script
    st.stop()

else:
    st.session_state.selected_domain = domain
    #Connect to the shared intelligence platform database
    conn = connect_database()

    #Verify if domain is Cyber Security
    if domain == "Cyber Security":
        st.subheader("Cyber Security")

        st.divider()

        st.markdown("##### Overview of Incidents")

        #Fetch all incidents from database
        incidents = get_all_incidents()
        total_incidents = len(incidents)

        #Get maximum incident id from incidents number
        max_incident_id = int(incidents["id"].max())

        #Get minimum incident id from incidents number
        min_incident_id = int(incidents["id"].min())

        #Fetches all Open incidents from database
        open_incidents = get_open_incidents(conn)
        total_open_incidents = len(open_incidents)

        #Fetches all high or critical incidents from database
        high_critical_incidents = get_high_or_critical_incidents(conn)
        total_high_critical_incidents = len(high_critical_incidents)

        #Split webpage into columns
        col1, col2, col3 = st.columns(3)

        with col1:
            #Generate metric for total incidents
            st.metric("Total incidents", total_incidents, border = True)

        with col2:
            #Generate metric for open incidents
            st.metric("Open Incidents", total_open_incidents, border = True)

        with col3:
            #Generate metric for high or critical incidents
            st.metric("High/Critical incidents", total_high_critical_incidents, border = True)

        #Display incidents in a table
        st.dataframe(incidents, use_container_width = True)

        st.markdown("##### Add New Incident")

        #Form to add new incident
        with st.form("new_incident"):
            #Prompt user to enter incident details
            incident_type = st.text_input("Incident Type")
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            date = st.date_input("Date Reported")
            description = st.text_area("Description")
                
            #Submit button for the form
            submitted = st.form_submit_button("Add Incident")

            #Verify if form is submitted
            if submitted:
                #Verify if all fields are filled
                if not incident_type or not description or not date or not severity or not status:
                    #Inform user to fill all fields
                    st.warning("Please fill in all fields.")
                else:
                    #Insert new incident into database
                    insert_incident(
                        date.strftime("%Y-%m-%d"),  #Convert date into year-month-day format
                        incident_type,
                        severity,
                        status,
                        description,
                        reported_by=st.session_state.username)
                    
                    #Success message
                    st.success("New incident added successfully.")
                    #Pause program for 1s
                    time.sleep(1)
                    #Rerun whole script
                    st.rerun()

        st.markdown("##### Delete Incident")

        #Form to delete incident
        with st.form("delete_incident"):
            #Prompt user to select incident ID
            incident_id_delete = st.number_input("Incident ID", min_value=min_incident_id, max_value=max_incident_id)
            
            #Checkbox to confirm deletion of incident
            confirm_delete = st.checkbox("Yes, delete incident")
            #Button for form
            submit_delete = st.form_submit_button("Delete Incident")

        #verify if form is submitted
        if submit_delete:
            #Verify if checkbox is ticked
            if not confirm_delete:
                #Inform user to tick checkbox
                st.warning("Please confirm deletion before proceeding.")
            else:
                #Proceed with deletion of incident
                if delete_incident(int(incident_id_delete)):
                    #Inform user that incident was deleted
                    st.success(f"Incident #{incident_id_delete} deleted.")

                    #Pause program for 1s
                    time.sleep(1)
                    #Rerun whole script
                    st.rerun()
                else:
                    #Error message
                    st.error("No incident found with that ID.")

        st.markdown("##### Update Incident")

        #Form to update incident
        with st.form("update_incident"):
            #Prompt user to select incident ID
            incident_id_update = st.number_input("Incident ID", min_value=min_incident_id, max_value=max_incident_id)
            
            #Prompt user to select new status of incident
            new_incident_status = st.selectbox("New Status", ["-- Select New Status --", "Open", "In Progress", "Resolved", "Closed"], key="update_status")
            #Button to submit form
            submit_update = st.form_submit_button("Update Incident")

        #Verify if form is submitted
        if submit_update:
            #Verify if new status is selected
            if new_incident_status == "-- Select New Status --":
                #Warning message
                st.warning("Please select new status of incident.")
                #Stop whole execution of script
                st.stop()

            #Proceed with updating incident status
            if update_incident(conn, int(incident_id_update), new_incident_status):
                #Success message
                st.success(f"Incident #{incident_id_update} updated to {new_incident_status}.")

                #Pause program for 1s
                time.sleep(1)
                #Rerun whole script
                st.rerun()
            else:
                #Error message
                st.error("No incident found with that ID.")

    #Verify if domain is Data Science
    if domain == "Data Science":
        st.subheader("Data Science")

        st.divider()

        st.markdown("##### Overview of Datasets")

        #Fetch all datasets from database
        datasets = get_all_datasets()
        total_datasets = len(datasets)

        large_datasets = get_large_datasets_by_source(conn)
        total_large_datasets = len(large_datasets)

        large_col_datasets = get_large_columns_datasets(conn)
        total_large_col_datasets = len(large_col_datasets)

        #Split webpage into columns
        col1, col2, col3 = st.columns(3)

        with col1:
            #Generate metric for total datasets
            st.metric("Total Datasets", total_datasets, border = True)

        with col2:
            st.metric("More than 10,000 records", total_large_datasets, border = True)           

        with col3:
            st.metric("More than 10 columns", total_large_col_datasets, border = True)

        #Display datasets in a table
        st.dataframe(datasets, use_container_width = True)
        

    conn.commit()
