import pandas as pd
from app.data.db import connect_database

def insert_incident(date, incident_type, severity, status, description, reported_by=None):
    """Insert new incident."""
    #Connect to database
    conn = connect_database()

    #Create cursor
    cursor = conn.cursor()

    #Execute insert statement
    cursor.execute("""
        INSERT INTO cyber_incidents
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (date, incident_type, severity, status, description, reported_by))
    
    #Save changes
    conn.commit()

    #Get id of inserted incident
    incident_id = cursor.lastrowid

    #Close connection
    conn.close()

    #Return incident id
    return incident_id

def get_all_incidents():
    """Get all incidents as DataFrame."""
    #Connect to database
    conn = connect_database()

    #Read data into DataFrame
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )

    #Close connection
    conn.close()

    #Return DataFrame
    return df

def update_incident(conn, incident_id, new_status):
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

def delete_incident(incident_id):
    """Delete incident by ID."""
    # Connect to database
    conn = connect_database()

    #Create cursor
    cursor = conn.cursor()

    #Execute delete statement
    cursor.execute("""
            DELETE FROM cyber_incidents WHERE id = ?
            """, (incident_id,))
    
    #Save changes
    conn.commit()

    #Get number of deleted rows
    row_count = cursor.rowcount

    #Close connection
    conn.close()

    #Return number of deleted rows
    return row_count

def get_incidents_by_type_count(conn):
    """
    Count incidents by type.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_incidents_by_status(conn):
    """
    Count incidents by status.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_incidents_by_severity(conn):
    """
    Count incidents by severity.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT severity, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY severity
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_severity_by_status(conn):
    """
    Count high severity incidents by status.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_incident_types_with_many_cases(conn, min_count=5):
    """
    Find incident types with more than min_count cases.
    Uses: SELECT, FROM, GROUP BY, HAVING, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df

def get_open_incidents(conn):
    """
    Retrieve all incidents that are currently open.
    Uses: SELECT, FROM, WHERE, ORDER BY
    """
    query = """
    SELECT *
    FROM cyber_incidents
    WHERE LOWER(status) = 'open'
    ORDER BY date DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_or_critical_incidents(conn):
    """
    Retrieve incidents with High or Critical severity.
    Uses: SELECT, FROM, WHERE, ORDER BY
    """
    query = """
    SELECT *
    FROM cyber_incidents
    WHERE LOWER(severity) IN ('high', 'critical')
    ORDER BY date DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

# Test: Run analytical queries
conn = connect_database()

print("\n Incidents by Type:")
df_by_type = get_incidents_by_type_count(conn)
print(df_by_type)

print("\n Incidents by Status:")
df_by_status = get_incidents_by_status(conn)
print(df_by_status)

print("\n Incidents by Severity:")
df_by_severity = get_incidents_by_severity(conn)
print(df_by_severity)

print("\n High Severity Incidents by Status:")
df_high_severity = get_high_severity_by_status(conn)
print(df_high_severity)

print("\n Incident Types with Many Cases (>5):")
df_many_cases = get_incident_types_with_many_cases(conn, min_count=5)
print(df_many_cases)

print("\n Open Incidents:")
df_open = get_open_incidents(conn)
print(df_open)

print("\n High or Critical Incidents:")
df_high_critical = get_high_or_critical_incidents(conn)
print(df_high_critical)

conn.close()
