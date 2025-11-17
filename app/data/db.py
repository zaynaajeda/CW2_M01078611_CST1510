import sqlite3
from pathlib import Path
import os
import pandas as pd

DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.

    Args:
        db_path: Path to the database file

    Returns:
        sqlite3.Connection: Database connection object
    """
    return sqlite3.connect(str(db_path))

#CSV loading function
def load_csv_to_table(conn, csv_path, table_name):
  #Checks if CSV file exists
  if os.path.exists(csv_path):
    #Print success message
    print(f"Success: CSV file was found at {csv_path}")
  else:
    #Print error message
    print(f"Error: No CSV file was found at {csv_path}")
    #No rows were loaded into SQL table
    return 0

  #Read CSV file using pandas
  df = pd.read_csv(csv_path)

  #Error handling
  try:
    #Insert data into sql table
    rows_count = df.to_sql(name = table_name, con = conn, if_exists = 'append', index = False)
    #Print success message
    print(f"{rows_count} added from {csv_path} to {table_name}")
  except Exception as e:
    #Print error message
    print(e)
    #No rows added since Exception is raised
    return 0

  #Number of rows loaded into sql table is returned
  return rows_count