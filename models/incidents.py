import os
import sys

import pandas as pd

from app.data.db import connect_database

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

#Define base class for incident cybersecurity
class Cybersecurity:
    """Base class for cybersecurity incidents."""

    def get_all_incidents(self) -> pd.DataFrame:
        conn = connect_database()
        df = pd.read_sql_query(
            "SELECT * FROM cyber_incidents ORDER BY id DESC",
            conn,
        )
        conn.close()
        return df


class Cyberincident(Cybersecurity):
    """Represents a single cybersecurity incident."""

    #Initialise attributes
    def __init__(self, date, incident_type, severity, status, description, reported_by=None):
        #Private attributes
        self.__date = date
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by

    def insert_incident(self) -> int:
        """Insert new incident into database."""
        #Connect to database
        conn = connect_database()
        #Create cursor object
        cursor = conn.cursor()

        #Execute insert statement
        cursor.execute("""
                        INSERT INTO cyber_incidents
                        (date, incident_type, severity, status, description, reported_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                       """,(self.__date,self.__incident_type,self.__severity,self.__status,
                            self.__description,self.__reported_by))
        
        #Save changes
        conn.commit()

        #Get id of inserted incident
        incident_id = cursor.lastrowid

        #Close connection
        conn.close()

        #Return id of incident
        return incident_id

    #Method to change status of incident
    def update_incident(self, incident_id: int, new_status: str) -> int:
        """Update incident status of an incident"""
        #Connect to database
        conn = connect_database()

        #Create cursor
        cursor = conn.cursor()

        #Execute update statement
        cursor.execute("""
            UPDATE cyber_incidents SET status = ? WHERE id = ?
            """, (new_status, incident_id))
        
        #Save changes
        conn.commit()

        #Get number of updated rows
        row_count = cursor.rowcount

        #Close connection
        conn.close()

        #Return number of updated rows
        return row_count 