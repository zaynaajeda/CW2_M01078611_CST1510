import streamlit as st
import sys
import os
import time
from datetime import timedelta

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

#Import datasets management functions
from app.data.datasets import (
    get_all_datasets,
    insert_dataset,
    update_dataset_record,
    delete_dataset,
    get_large_datasets_by_source,
    get_large_columns_datasets)

#Import tickets management functions
from app.data.tickets import (
    get_all_tickets,
    insert_ticket,
    delete_ticket,
    update_ticket,
    get_open_tickets,
    get_high_or_critical_tickets)

from my_app.components.sidebar import logout_section

#Retrieve role of user from session state
role_user = st.session_state.role

#Webpage title and icon
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

if "username" not in st.session_state:
    #Initialise username
    st.session_state.username = ""

if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = None

if "role" not in st.session_state:
    #Initialise role
    st.session_state.role = ""

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

    #Inform user about domain selected
    st.info(f"Selected domain: **{domain}**")
    st.divider()


    # Each domain is started by basic summarised metrics(Total incidents/datasets/tickets)
    # followed by table showing details about each domain.

    # CRUD Features of each domain is then displayed(Incidents/Datasets/Tickets management)
    # whereby user can add/delete/update any incident/dataset/ticket depending on domain selected.


    #Verify if domain is Cyber Security
    if domain == "Cyber Security":

        st.markdown("##### Overview of Incidents")

        #Fetch all incidents from database
        incidents = get_all_incidents()
        total_incidents = len(incidents)

        #Get maximum and minimum incident id from database
        max_incident_id = int(incidents["id"].max()) if total_incidents else None
        min_incident_id = int(incidents["id"].min()) if total_incidents else None

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
            st.metric("Total Incidents", total_incidents, border = True)

        with col2:
            #Generate metric for open incidents
            st.metric("Open Incidents", total_open_incidents, border = True)

        with col3:
            #Generate metric for high or critical incidents
            st.metric("High/Critical incidents", total_high_critical_incidents, border = True)

        #Verify if incidents database was found
        if incidents.empty:
            st.info("No incidents recorded yet. Add a new one below.")
        else:
            #Display incidents in a table
            st.dataframe(incidents, use_container_width = True)
    
        st.divider()
        st.markdown("#### Incidents Management")

        #Ensure that this section is only available to admins
        if role_user == "admin":

            st.markdown("##### Add New Incident")

            #Form to add new incident
            with st.form("new_incident"):
                #Prompt user to enter incident details
                incident_type = st.text_input("Incident Type")
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
                date = st.date_input("Date Reported")
                description = st.text_area("Description")

                #Checkbox to confirm new incident
                confirm_add_incident = st.checkbox("Yes, add incident.")
                    
                #Submit button for the form
                submitted = st.form_submit_button("Add Incident")

                #Verify if form is submitted
                if submitted:
                    #Verify confirmation checkbox
                    if not confirm_add_incident:
                        st.warning("Please confirm addition before proceeding.")
                    #Verify if all fields are filled
                    elif not incident_type or not description or not date or not severity or not status:
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

            #This prevents any error from table of incidents not being displayed
            if incidents.empty:
                st.info("No incidents available for deletion or updates yet.")
            else:
                #Form to delete incident
                with st.form("delete_incident"):
                    #Prompt user to select incident ID
                    incident_id_delete = st.number_input("Incident ID", min_value = min_incident_id, max_value = max_incident_id)
                    
                    #Checkbox to confirm deletion of incident
                    confirm_delete_incident = st.checkbox("Yes, delete incident")
                    #Button for form
                    submit_delete_incident = st.form_submit_button("Delete Incident")

                #verify if form is submitted
                if submit_delete_incident:
                    #Verify if checkbox is ticked
                    if not confirm_delete_incident:
                        #Inform user to tick checkbox
                        st.warning("Please confirm deletion before proceeding.")
                    else:
                        #Proceed with deletion of incident
                        if delete_incident(int(incident_id_delete)):
                            #Inform user that incident was deleted
                            st.success(f"Incident of ID {incident_id_delete} deleted.")

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
                    incident_id_update = st.number_input("Incident ID", min_value = min_incident_id, max_value = max_incident_id)
                    
                    #Prompt user to select new status of incident
                    new_incident_status = st.selectbox("New Status", ["-- Select New Status --", "Open", "In Progress", "Resolved", "Closed"], key="update_status")
                    confirm_update_incident = st.checkbox("Yes, update incident.")
                    #Button to submit form
                    submit_update = st.form_submit_button("Update Incident")

                #Verify if form is submitted
                if submit_update:
                    #Verify confirmation checkbox
                    if not confirm_update_incident:
                        st.warning("Please confirm update before proceeding.")
                    #Verify if new status is selected
                    elif new_incident_status == "-- Select New Status --":
                        #Warning message
                        st.warning("Please select new status of incident.")
                        #Stop whole execution of script
                        st.stop()

                    #Proceed with updating incident status
                    if update_incident(conn, int(incident_id_update), new_incident_status):
                        #Success message
                        st.success(f"Incident of ID {incident_id_update} updated to {new_incident_status}.")

                        #Pause program for 1s
                        time.sleep(1)
                        #Rerun whole script
                        st.rerun()
                    else:
                        #Error message
                        st.error("No incident found with that ID.")
        #If user is not admin(analyst/user)
        else:
            #Inform user that he has to be admin to access this section
            st.warning(f"You must be **admin** to have access to this section")

    #Verify if domain is Data Science
    if domain == "Data Science":

        st.markdown("##### Overview of Datasets")

        #Fetch all datasets from database
        datasets = get_all_datasets()
        total_datasets = len(datasets)

        #Get maximum and minimum dataset id from database
        min_dataset_id = int(datasets["id"].min()) if total_datasets else None
        max_dataset_id = int(datasets["id"].max()) if total_datasets else None

        #Fetches all datasets with >10000 record counts
        large_datasets = get_large_datasets_by_source(conn)
        total_large_datasets = len(large_datasets)

        #Fetches all datasets with >10 column counts
        large_col_datasets = get_large_columns_datasets(conn)
        total_large_col_datasets = len(large_col_datasets)

        #Split webpage into columns
        col1, col2, col3 = st.columns(3)

        with col1:
            #Generate metric for total datasets
            st.metric("Total Datasets", total_datasets, border = True)

        with col2:
            #Generate metric for total datasets with >10000 records
            st.metric("More than 10,000 records", total_large_datasets, border = True)           

        with col3:
            #Generate metric for total datasets with >10 columns
            st.metric("More than 10 columns", total_large_col_datasets, border = True)

        #Display datasets in a table
        if datasets.empty:
            st.info("No datasets recorded yet. Add a new one below.")
        else:
            st.dataframe(datasets, use_container_width = True)

        st.divider()
        st.markdown("#### Datasets Management")

        #Ensure that this section is only available to admins
        if role_user == "admin":

            st.markdown("##### Add New Dataset")

            #Form to add new dataset
            with st.form("new_dataset"):
                #Prompt user to enter dataset details
                dataset_name = st.text_input("Dataset Name")
                category = st.text_input("Category")
                source = st.text_input("Source")
                last_updated = st.date_input("Last Updated")
                record_count = st.number_input("Record Count", min_value = 1000, step = 1000)
                column_count = st.number_input("Column Count", min_value = 1, step = 1)
                file_size = st.number_input("File Size (MB)", min_value = 0.1, step = 0.1)
                confirm_add_dataset = st.checkbox("Yes, add dataset.")

                #Submit button for the form
                dataset_submit = st.form_submit_button("Add Dataset")

            #Verify if form is submitted
            if dataset_submit:
                #Verify confirmation checkbox
                if not confirm_add_dataset:
                    st.warning("Please confirm addition before proceeding.")
                #Verify if all fields are filled
                elif not dataset_name or not category or not source or not last_updated:
                    #Inform user to fill all fields
                    st.warning("Please fill in all fields.")
                else:
                    #Insert new dataset into database
                    insert_dataset(
                            dataset_name,
                            category,
                            source,
                            last_updated.strftime("%Y-%m-%d"),
                            int(record_count),
                            int(column_count),
                            file_size)
                    
                    #Success message
                    st.success("New dataset added successfully.")

                    #Pause program for 1s
                    time.sleep(1)
                    #Rerun whole script
                    st.rerun()
            
            st.markdown("##### Delete Dataset")

            #This prevents any error from table of datasets not being displayed
            if datasets.empty:
                st.info("No datasets available for deletion or updates yet.")
            else:
                #Form to delete dataset
                with st.form("delete_dataset"):
                    #Prompt user to select dataset ID
                    dataset_id_delete = st.number_input("Dataset ID", min_value = min_dataset_id, max_value = max_dataset_id)

                    #Checkbox to confirm deletion of dataset
                    confirm_delete_dataset = st.checkbox("Yes, delete dataset.")
                    #Button for form
                    submit_delete_dataset = st.form_submit_button("Delete Dataset")

                #Verify if form is submitted
                if submit_delete_dataset:
                    #Verify if checkbox is ticked
                    if not confirm_delete_dataset:
                        #Inform user to tick checkbox
                        st.warning("Please confirm deletion before proceeding.")
                    else:
                        #Proceed with deletion of dataset
                        if delete_dataset(int(dataset_id_delete)):
                            #Success message
                            st.success(f"Dataset of ID {dataset_id_delete} deleted.")

                            #Pause program for 1s
                            time.sleep(1)
                            #Rerun whole script
                            st.rerun()
                        else:
                            #Error message
                            st.error("No dataset found with that ID")


                st.markdown("##### Update Dataset")

                #Form to update incident
                with st.form("update_dataset"):
                    #Prompt user to select dataset ID
                    dataset_id_update = st.number_input("Dataset ID", min_value = min_dataset_id, max_value = max_dataset_id)
                    
                    #Prompt user to select new record count of dataset
                    new_record_count = st.number_input("New Record Count", min_value = 1000, step = 1000)
                    confirm_update_dataset = st.checkbox("Yes, update dataset.")
                    
                    #Button to submit form
                    submit_dataset_update = st.form_submit_button("Update Dataset")

                #verify if form is submitted
                if submit_dataset_update:
                    #Verify confirmation checkbox
                    if not confirm_update_dataset:
                        st.warning("Please confirm update before proceeding.")
                    #Proceeds with updating record of dataset
                    elif update_dataset_record(conn, int(dataset_id_update), int(new_record_count)):
                        #Success message
                        st.success(f"Dataset of ID {dataset_id_update} updated to {new_record_count} records.")
                        #Pause program for 1s
                        time.sleep(1)
                        #Rerun whole script
                        st.rerun()
                    else:
                        #Error message
                        st.error("No dataset found with that ID.")
        
        #If user is not admin(analyst/user)
        else:
            #Inform user that he has to be admin to access this section
            st.warning(f"You must be **admin** to have access to this section")

    #Verify if domain is IT Operations
    if domain == "IT Operations":
        
        st.markdown("##### Overview of Tickets")

        #Fetch all tickets from database
        tickets = get_all_tickets()
        total_tickets = len(tickets)

        #Get maximum and minimum ticket id from database
        max_ticket_id = int(tickets["id"].max()) if total_tickets else None
        min_ticket_id = int(tickets["id"].min()) if total_tickets else None

        #Fetch open tickets count
        open_tickets = get_open_tickets(conn)
        total_open_tickets = len(open_tickets)

        #Fetch high or critical priority tickets count
        high_critical_tickets = get_high_or_critical_tickets(conn)
        total_high_critical_tickets = len(high_critical_tickets)

        #Split page into columns
        col1, col2, col3 = st.columns(3)

        with col1:
            #Generate metric for total tickets
            st.metric("Total Tickets", total_tickets, border = True)

        with col2:
            #Generate metric for open tickets
            st.metric("Open Tickets", total_open_tickets, border = True)

        with col3:
            #Generate high or critical tickets
            st.metric("High/Critical Tickets", total_high_critical_tickets, border = True)

        #Display tickets in a table
        if tickets.empty:
            st.info("No tickets recorded yet. Add a new one below.")
        else:
            st.dataframe(tickets, use_container_width = True)    

        st.divider()
        st.markdown("#### Tickets Management")

        #Ensure that this section is only available to admins
        if role_user == "admin":

            st.markdown("##### Add New Ticket")

            #Form to add new ticket
            with st.form("new_ticket"):
                #Prompt user to enter ticket details
                ticket_subject = st.text_input("Ticket Subject")
                ticket_category = st.text_input("Category")
                assigned_to = st.text_input("Assigned To")
                ticket_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                ticket_status = st.selectbox("Status", ["Open", "In Progress", "Waiting for User", "Resolved", "Closed"])
                ticket_created_date = st.date_input("Created Date")
                resolved_days = st.number_input("Days required to resolve", min_value=1, step=1)
                ticket_description = st.text_area("Description")
                confirm_add_ticket = st.checkbox("Yes, add ticket.")

                #Submit button for form
                submit_ticket = st.form_submit_button("Add Ticket")

            #Verify if form is submitted
            if submit_ticket:
                #Verify confirmation checkbox
                if not confirm_add_ticket:
                    st.warning("Please confirm addition before proceeding.")
                #Verify is user has entered all fields
                elif not ticket_subject or not ticket_category or not ticket_description or not assigned_to:
                    #Inform user to fill all fields
                    st.warning("Please fill in all fields.")
                else:
                    #Convert resolved days into string
                    resolved_days = str(resolved_days)

                    #Insert new ticket into database
                    insert_ticket(
                        ticket_priority,
                        ticket_status,
                        ticket_category,
                        ticket_subject,
                        ticket_description,
                        ticket_created_date.strftime("%Y-%m-%d"),
                        resolved_days,
                        assigned_to)
                    
                    #Success message
                    st.success("New ticket added successfully.")

                    #Pause program for 1s
                    time.sleep(1)
                    #Rerun whole program
                    st.rerun()


            st.markdown("##### Delete Ticket")

            #This prevents any error from table of tickets not being displayed
            if tickets.empty:
                st.info("No tickets available for deletion or updates yet.")
            else:
                #Form to delete ticket
                with st.form("delete_ticket"):
                    #Prompt user to select ticket ID
                    ticket_id_delete = st.number_input("Ticket ID", min_value = min_ticket_id, max_value = max_ticket_id)

                    #Checkbox to confirm deletion of ticket
                    confirm_delete_ticket = st.checkbox("Yes, delete ticket.")
                    #Button for form
                    submit_delete_ticket = st.form_submit_button("Delete Ticket")

                #Verify if form is submitted
                if submit_delete_ticket:
                    #Verify if checkbox is ticked
                    if not confirm_delete_ticket:
                        #Inform user to tick checkbox
                        st.warning("Please confirm deletion before proceeding.")
                    else:
                        #Proceed with deletion of ticket
                        if delete_ticket(int(ticket_id_delete)):
                            #Inform user that ticket was deleted
                            st.success(f"Ticket of ID {ticket_id_delete} deleted.")

                            #Pause program for 1s
                            time.sleep(1)
                            #Rerun whole script
                            st.rerun()
                        else:
                            #Error message
                            st.error("No ticket found with that ID")


                st.markdown("##### Update Ticket")

                #Form to update ticket
                with st.form("update_ticket"):
                    #Prompt user to select ticket ID
                    ticket_id_update = st.number_input("Incident ID", min_value = min_ticket_id, max_value = max_ticket_id)
                    
                    #Prompt user to select new status of ticket
                    new_ticket_status = st.selectbox("New Status", ["-- Select New Status --", "Open", "In Progress", "Waiting for User", "Resolved", "Closed"], key="update_status")
                    confirm_update_ticket = st.checkbox("Yes, update ticket.")
                    #Button to submit form
                    submit_ticket_update = st.form_submit_button("Update Ticket")

                #Verify if form is submitted
                if submit_ticket_update:
                    #Verify confirmation checkbox
                    if not confirm_update_ticket:
                        st.warning("Please confirm update before proceeding.")
                    #Verify if new status is selected
                    elif new_ticket_status == "-- Select New Status --":
                        #Warning message
                        st.warning("Please select new status of ticket.")
                        #Stop whole execution of script
                        st.stop()

                    #Proceed with updating ticket status
                    if update_ticket(conn, int(ticket_id_update), new_ticket_status):
                        #Success message
                        st.success(f"Ticket of ID {ticket_id_update} updated to {new_ticket_status}.")

                        #Pause program for 1s
                        time.sleep(1.2)
                        #Rerun whole script
                        st.rerun()
                    else:
                        #Error message
                        st.error("No ticket found with that ID.")
        #If user is not admin(analyst/user)
        else:
            #Inform user that he has to be admin to access this section
            st.warning(f"You must be **admin** to have access to this section")

    #Save changes
    conn.commit()
