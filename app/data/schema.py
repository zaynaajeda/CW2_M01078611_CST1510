def create_users_table(conn):
    """Create users table."""
    #Create cursor
    cursor = conn.cursor()

    #SQL statement to create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    #Save changes
    conn.commit()
    #Success message
    print("✅ Users table created successfully!")

def create_cyber_incidents_table(conn):
    """Create cyber_incidents table."""
    #Create cursor
    cursor = conn.cursor()

    #SQL statement to create cyber_incidents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            reported_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    #Save changes 
    conn.commit()
    #Success message
    print("✅ cyber_incidents table created successfully!")

def create_all_tables(conn):
    """Create all tables."""
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)