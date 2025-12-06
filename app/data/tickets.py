import pandas as pd
from app.data.db import connect_database

def insert_ticket(priority, status, category, subject,
                  description, created_date, resolved_date=None,
                  assigned_to=None):
    """Insert new IT ticket."""
    #Connect to database
    conn = connect_database()

    #Create cursor
    cursor = conn.cursor()

    #Execute insert statement
    cursor.execute("""
        INSERT INTO it_tickets
        (priority, status, category, subject, description,
         created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (priority, status,
              category if category else "General",
              subject if subject else "No Subject",
              description,
              created_date, resolved_date, assigned_to))

    #Save changes
    conn.commit()

    #Get id of inserted ticket
    ticket_id = cursor.lastrowid

    #Close connection
    conn.close()

    #Return ticket id
    return ticket_id

def get_all_tickets():
    """Get all tickets as DataFrame."""
    #Connect to database
    conn = connect_database()

    #Read data into DataFrame
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )

    #Close connection
    conn.close()

    #Return DataFrame
    return df

def update_ticket(conn, ticket_id, new_status):
    """Update status of a ticket."""
    #Connect to database
    conn = connect_database()

    #Create cursor
    cursor = conn.cursor()

    #Execute update statement
    cursor.execute("""
        UPDATE it_tickets SET status = ? WHERE id = ?
        """, (new_status, ticket_id))

    #Save changes
    conn.commit()

    #Get number of updated rows
    row_count = cursor.rowcount

    #Close connection
    conn.close()

    #Return number of updated rows
    return row_count

def delete_ticket(ticket_id):
    """Delete ticket by ID."""
    # Connect to database
    conn = connect_database()

    #Create cursor
    cursor = conn.cursor()

    #Execute delete statement
    cursor.execute("""
            DELETE FROM it_tickets WHERE id = ?
            """, (ticket_id,))

    #Save changes
    conn.commit()

    #Get number of deleted rows
    row_count = cursor.rowcount

    #Close connection
    conn.close()

    #Return number of deleted rows
    return row_count

def get_tickets_by_status_count(conn):
    """
    Count tickets by status.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM it_tickets
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_priority_by_assignee(conn):
    """
    Count high priority tickets by assigned person.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    query = """
    SELECT assigned_to, COUNT(*) as count
    FROM it_tickets
    WHERE priority = 'High'
    GROUP BY assigned_to
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_tickets_by_assigned_to(conn):
    """
    Count tickets grouped by the assigned engineer.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT assigned_to, COUNT(*) as count
    FROM it_tickets
    GROUP BY assigned_to
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_categories_with_many_tickets(conn, min_count=5):
    """
    Find ticket categories with more than min_count cases.
    Uses: SELECT, FROM, GROUP BY, HAVING, ORDER BY
    """
    query = """
    SELECT category, COUNT(*) as count
    FROM it_tickets
    GROUP BY category
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df

def get_tickets_by_priority(conn):
    """
    Count tickets grouped by priority.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT priority, COUNT(*) as count
    FROM it_tickets
    GROUP BY priority
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_tickets_over_time(conn):
    """
    Count tickets created per day.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT created_date, COUNT(*) as count
    FROM it_tickets
    GROUP BY created_date
    ORDER BY created_date ASC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_open_tickets(conn):
    """
    Retrieve all tickets that are currently open.
    Uses: SELECT, FROM, WHERE, ORDER BY
    """
    query = """
    SELECT *
    FROM it_tickets
    WHERE LOWER(status) = 'open'
    ORDER BY created_date DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_or_critical_tickets(conn):
    """
    Retrieve tickets with High or Critical priority.
    Uses: SELECT, FROM, WHERE, ORDER BY
    """
    query = """
    SELECT *
    FROM it_tickets
    WHERE LOWER(priority) IN ('high', 'critical')
    ORDER BY created_date DESC
    """
    df = pd.read_sql_query(query, conn)
    return df


# Test: Run analytical queries
conn = connect_database()

print("\n Tickets by Status:")
df_by_status = get_tickets_by_status_count(conn)
print(df_by_status)

print("\n High Priority Tickets by Assignee:")
df_high_priority = get_high_priority_by_assignee(conn)
print(df_high_priority)

print("\n Categories with Many Tickets (>5):")
df_many_tickets = get_categories_with_many_tickets(conn, min_count=5)
print(df_many_tickets)

print("\n Open Tickets:")
df_open_tickets = get_open_tickets(conn)
print(df_open_tickets)

print("\n High or Critical Tickets:")
df_high_critical_tickets = get_high_or_critical_tickets(conn)
print(df_high_critical_tickets)

conn.close()
