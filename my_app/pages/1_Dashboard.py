import streamlit as st
import sys
import os
import time
import matplotlib.pyplot as plt

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
    get_incidents_by_type_count,
    get_incidents_by_status,
    get_incidents_by_severity)

#Webpage title and icon
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

if "username" not in st.session_state:
    #Initialise username
    st.session_state.username = ""

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

#Sidebar for domain selection
with st.sidebar:

    st.subheader("Navigation")

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
    #Connect to the shared intelligence platform database
    conn = connect_database()

    #Verify if domain is Cyber Security
    if domain == "Cyber Security":
        st.subheader("Cyber Security")

        st.divider()

        st.markdown("##### Overview of Incidents")
        #Fetch all incidents from database
        incidents = get_all_incidents()

        #Display incidents in a table
        st.dataframe(incidents, use_container_width=True)

        st.markdown("#### Trends")

        col1, col2 = st.columns(2)

        with col1:
            #Take number of incidents by type
            incidents_by_type = get_incidents_by_type_count(conn)
            
            #Verify if function successfully returned data
            if incidents_by_type.empty == False:
                st.markdown("##### Incidents by Type")

                #Generate bar chart for incident types
                incident_type_data = incidents_by_type.set_index("incident_type")
                st.bar_chart(incident_type_data, use_container_width=True)

            else:
                #Inform user that no data is available
                st.info("No cyber incident data available.")

            #Take number of incidents by status
            incidents_by_status = get_incidents_by_status(conn)

            #Verify if function successfully returned data
            if incidents_by_status.empty == False:
                st.markdown("##### Incidents by Status")

                #Generate bar chart for incident status
                incident_status_data = incidents_by_status.set_index("status")
                st.bar_chart(incident_status_data, use_container_width=True)
            
            else:
                #Inform user that no data is available
                st.info("No cyber incident data available.")

        with col2:
            #Take number of incidents by severity
            incidents_by_severity = get_incidents_by_severity(conn)

            #Verify if function successfully returned data
            if incidents_by_severity.empty == False:
                st.markdown("##### Incidents by Severity")

                #Generate pie chart for incident severity
                fig, ax = plt.subplots(figsize=(2.2, 2.2))
                ax.pie(
                    incidents_by_severity["count"],
                    labels=incidents_by_severity["severity"],
                    autopct="%1.0f%%",
                    startangle=90,
                    textprops={"fontsize": 5},
                )
                ax.axis("equal")
                st.pyplot(fig, use_container_width=False)

            else:
                #Inform user that no data is available
                st.info("No cyber incident severity data available.")

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
                    time.sleep(1)
                    #Rerun whole script
                    st.rerun()

    conn.commit()
