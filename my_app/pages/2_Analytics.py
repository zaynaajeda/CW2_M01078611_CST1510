import streamlit as st
import sys
import os
import matplotlib.pyplot as plt

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

from my_app.components.sidebar import logout_section

#Import database connection function
from app.data.db import connect_database

#Import incident management functions
from app.data.incidents import (
    get_incidents_by_status,
    get_incidents_by_severity,
    get_incidents_by_type_count,
    get_incidents_over_time)

#Import dataset management functions
from app.data.datasets import (
    get_datasets_by_category,
    get_datasets_by_source)

#Connect to the shared intelligence platform database
conn = connect_database()

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

if domain == "Cyber Security":
    #Take number of incidents per day
    incidents_over_time = get_incidents_over_time(conn)

    #Display time-series for cyberincidents
    if incidents_over_time.empty == False:
        st.markdown("##### Incidents over Time")

        #Create line chart for number of incidents over time
        st.line_chart(incidents_over_time, x = "date", y = "count")
    else:
        #Inform user that no data is available to plot
        st.info("No time-series data of incidents available.")

    #Divide page into columns
    col1, col2 = st.columns(2)

    with col1:
        #Take incidents by type
        incidents_by_type = get_incidents_by_type_count(conn)
            
        #Verify if function successfully returned data
        if incidents_by_type.empty == False:
            st.markdown("##### Incidents by Type")

            #Generate bar chart for incident types
            st.bar_chart(incidents_by_type, x = "incident_type", y = "count")

        else:
            #Inform user that no data is available
            st.info("No cyber incident data available.")

        #Take incidents by status
        incidents_by_status = get_incidents_by_status(conn)

        #Verify if function successfully returned data
        if incidents_by_status.empty == False:
            st.markdown("##### Incidents by Status")

            #Generate bar chart for incident status
            st.bar_chart(incidents_by_status, x = "status", y = "count")
            
        else:
            #Inform user that no data is available
            st.info("No cyber incident data available.")

    with col2:
        #Take incidents by severity
        incidents_by_severity = get_incidents_by_severity(conn)

        #Verify if function successfully returned data
        if incidents_by_severity.empty == False:
            st.markdown("##### Incidents by Severity")

            #Generate pie chart for incident severity
            fig, ax = plt.subplots(figsize = (2.2, 2.2))
            ax.pie(incidents_by_severity["count"],
                    labels = incidents_by_severity["severity"],
                    autopct = "%1.0f%%",
                    startangle = 90,
                    textprops = {"fontsize": 5})
            ax.axis("equal")
            st.pyplot(fig, use_container_width=False)

        else:
            #Inform user that no data is available
            st.info("No cyber incident severity data available.")

if domain == "Data Science":
    #Take datasets by category 
    datasets_by_category = get_datasets_by_category(conn)

    #Verify if function successfully returned data
    if datasets_by_category.empty == False:
        st.markdown("##### Datasets by Category")

        #Generate bar chart for dataset categories
        st.bar_chart(datasets_by_category, x = "category", y = "count")
    else:
        #Inform user that no data is available
        st.info("No datasets available.")

    #Take datasets by source
    datasets_by_source = get_datasets_by_source(conn)

    #Verify if function successfully returned data
    if datasets_by_source.empty == False:
        st.markdown("##### Datasets by Source")

        #Generate bar chart for dataset sources
        st.bar_chart(datasets_by_source, x = "source", y = "count")
    else:
        #Inform user that no data is available
        st.info("No dataset source information available.")

    #Verify if function successfully returned data
    if datasets_by_source.empty == False:
        st.markdown("##### Datasets by Source")

        #Generate pie chart for dataset categories
        fig, ax = plt.subplots(figsize = (2.2, 2.2))
        ax.pie(datasets_by_source["count"],
                labels = datasets_by_source["source"],
                autopct = "%1.0f%%",
                startangle = 90,
                textprops = {"fontsize": 5})
        ax.axis("equal")
        st.pyplot(fig, use_container_width = False)        


