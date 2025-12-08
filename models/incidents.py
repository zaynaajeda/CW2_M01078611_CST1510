import os
import sys

import pandas as pd

from app.data.db import connect_database

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

#Define class for incident cybersecurity
class Cyberincident:
    """Represents a cybersecurity incident in the platform."""

    #Method to retrieve incidents from table cyber_incidents
    def get_all_incidents(self) -> pd.DataFrame:
        #Connect to database
        conn = connect_database()

        #Read data into DataFrame
        df = pd.read_sql_query(
            "SELECT * FROM cyber_incidents ORDER BY id DESC",
            conn,
        )

        #Close connection
        conn.close()

        #Return DataFrame
        return df  

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
