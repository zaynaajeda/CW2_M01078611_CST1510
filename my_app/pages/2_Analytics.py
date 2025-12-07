import streamlit as st
import sys
import os
import matplotlib.pyplot as plt
import pandas as pd

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
    get_datasets_by_source,
    get_datasets_over_time,
    get_dataset_record_counts,
    get_dataset_column_counts)

from app.data.tickets import (
    get_tickets_over_time,
    get_tickets_by_status_count,
    get_tickets_by_priority,
    get_tickets_by_assigned_to)

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
st.divider()

#Verify if user is logged in
if st.session_state.logged_in:
    #Generate sidebar
    with st.sidebar:
        #Add a divider and logout section
        st.divider()
        #Implement logout
        logout_section()

#Verify if domain is cyber security
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

    st.divider()

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

        st.divider()

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

#Verify if domain is data science
if domain == "Data Science":
    #Take number of datasets per day
    datasets_over_time = get_datasets_over_time(conn)

    #Display time-series for datasets
    if datasets_over_time.empty == False:
        st.markdown("##### Datasets over Time")

        #Create line chart for number of datasets over time
        st.line_chart(datasets_over_time, x = "last_updated", y = "count")
    else:
        #Inform user that no data is available to plot
        st.info("No time-series data of datasets available.")

    st.divider()

    #Divide page into columns
    col1, col2 = st.columns(2)

    with col1:
        #Display record counts per dataset
        dataset_record_counts = get_dataset_record_counts(conn)

        if dataset_record_counts.empty == False:
            st.markdown("##### Record Count per Dataset")

            #Generate bar chart for dataset record sizes
            st.bar_chart(dataset_record_counts, x = "dataset_name", y = "record_count", use_container_width = True)
        else:
            #Inform user that no dataset-level metrics are available
            st.info("No dataset record count information available.")       
        
        st.divider()

        #Take datasets by category 
        datasets_by_category = get_datasets_by_category(conn)

        #Verify if function successfully returned data
        if datasets_by_category.empty == False:
            st.markdown("##### Datasets by Category")

            #Generate pie chart for dataset categories
            fig, ax = plt.subplots(figsize = (2.2, 2.2))
            ax.pie(datasets_by_category["count"],
                    labels = datasets_by_category["category"],
                    autopct = "%1.0f%%",
                    startangle = 90,
                    textprops = {"fontsize": 5})        
            ax.axis("equal")
            st.pyplot(fig, use_container_width = False) 

    with col2:
        #Display column counts per dataset
        dataset_column_counts = get_dataset_column_counts(conn)

        if dataset_column_counts.empty == False:
            st.markdown("##### Column Count per Dataset")

            #Generate bar chart for dataset column sizes
            st.bar_chart(dataset_column_counts, x = "dataset_name", y = "column_count", use_container_width = True)
        else:
            #Inform user that no column counts of dataset are available
            st.info("No dataset column count information available.")       

        st.divider()

        #Take datasets by source
        datasets_by_source = get_datasets_by_source(conn)

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

#Verify if domain is IT operations
if domain == "IT Operations":   
    #Take number of tickets created per day
    tickets_over_time = get_tickets_over_time(conn)

    #Display time-series for IT tickets
    if tickets_over_time.empty == False:
        st.markdown("##### Tickets over Time")

        #Create line chart for number of tickets over time
        st.line_chart(tickets_over_time, x = "created_date", y = "count")

    else:
        #Inform user that no data is available to plot
        st.info("No time-series data of tickets available.")

    st.divider()

    #Take tickets by assignees
    tickets_by_assigned_to = get_tickets_by_assigned_to(conn)

    #Verify if function successfully returned data
    if tickets_by_assigned_to.empty == False:
        st.markdown("##### Tickets by Assignees")

        #Generate pie chart for ticket assignees
        fig, ax = plt.subplots(figsize = (6.5, 2.5))
        ax.pie(tickets_by_assigned_to["count"],
                labels = tickets_by_assigned_to["assigned_to"],
                autopct = "%1.0f%%",
                startangle = 90,
                textprops = {"fontsize": 5})
        ax.axis("equal")
        st.pyplot(fig, use_container_width = False) 

    st.divider()

    #Divide page into 2 columns
    col1, col2 = st.columns(2)

    with col1: 
        #Take number of tickets by priority
        tickets_by_priority = get_tickets_by_priority(conn)

        #Verify if function returned data
        if tickets_by_priority.empty == False:
            st.markdown("##### Tickets by Priority")

            #Generate bar chart for ticket priorities
            st.bar_chart(tickets_by_priority, x = "priority", y = "count", use_container_width = True)

        else:
            #Inform user that no ticket priorities are found
            st.info("No ticket priority information available.")

    with col2:
        #Take number of tickets by status
        tickets_by_status = get_tickets_by_status_count(conn)

        #Verify if function returned data
        if tickets_by_status.empty == False:
            st.markdown("##### Tickets by Status")

            #Generate bar chart for ticket status
            st.bar_chart(tickets_by_status, x = "status", y = "count", use_container_width = True)

        else:
            #Inform user that no ticket status is found
            st.info("No ticket status information available.")