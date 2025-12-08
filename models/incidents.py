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
