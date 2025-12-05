import pandas as pd
from datetime import datetime
from app.data.db import connect_database

def insert_dataset(dataset_name, category, source, last_updated,
                   record_count, column_count, file_size_mb="Unknown"):
    """Insert new dataset metadata."""
    #Connect to database
    conn = connect_database()

    #Create cursor
    cursor = conn.cursor()

    #Execute insert statement
    cursor.execute("""
        INSERT INTO datasets_metadata
        (dataset_name, category, source, last_updated,
         record_count, column_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (dataset_name, category, source, last_updated,
              record_count, column_count, file_size_mb))

    #Save changes
    conn.commit()

    #Get id of inserted dataset
    dataset_id = cursor.lastrowid

    #Close connection
    conn.close()

    #Return dataset id
    return dataset_id

def get_all_datasets():
    """Get all datasets as DataFrame."""
    #Connect to database
    conn = connect_database()

    #Read data into DataFrame
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata ORDER BY id DESC",
        conn
    )

    #Close connection
    conn.close()

    #Return DataFrame
    return df

def update_dataset_record(conn, dataset_id, new_record_count):
    """Update record count of a dataset and refresh the last_updated date."""
    #Connect to database
    conn = connect_database()

    #Create cursor
    cursor = conn.cursor()

    #Generate today's date
    current_date = datetime.now().strftime("%Y-%m-%d")

    #Execute update statement
    cursor.execute("""
        UPDATE datasets_metadata
        SET record_count = ?, last_updated = ?
        WHERE id = ?
        """, 
        (new_record_count, current_date, dataset_id))

    #Save changes
    conn.commit()

    #Get number of updated rows
    row_count = cursor.rowcount

    #Close connection
    conn.close()

    #Return number of updated rows
    return row_count

def delete_dataset(dataset_id):
    """Delete dataset by ID."""
    # Connect to database
    conn = connect_database()

    #Create cursor
    cursor = conn.cursor()

    #Execute delete statement
    cursor.execute("""
            DELETE FROM datasets_metadata WHERE id = ?
            """, (dataset_id,))

    #Save changes
    conn.commit()

    #Get number of deleted rows
    row_count = cursor.rowcount

    #Close connection
    conn.close()

    #Return number of deleted rows
    return row_count

def get_datasets_by_category_count(conn):
    """
    Count datasets by category.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    #Execute select statement
    query = """
    SELECT category, COUNT(*) as count
    FROM datasets_metadata
    GROUP BY category
    ORDER BY count DESC
    """
    #Create dataframe
    df = pd.read_sql_query(query, conn)
    #Return dataframe
    return df

def get_large_datasets_by_source(conn):
    """
    Count large datasets by source.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    #Execute select statement
    query = """
    SELECT source, COUNT(*) as count
    FROM datasets_metadata
    WHERE record_count >= 10000
    GROUP BY source
    ORDER BY count DESC
    """
    #Create dataframe
    df = pd.read_sql_query(query, conn)
    #Return dataframe
    return df

def get_large_columns_datasets(conn):
    """
    Count datasets where column count is greater than 10.
    Uses: SELECT, FROM, WHERE, ORDER BY
    """
    #Execute select statement
    query = """
    SELECT dataset_name, column_count
    FROM datasets_metadata
    WHERE column_count > 10
    ORDER BY column_count DESC
    """
    #Create dataframe
    df = pd.read_sql_query(query, conn)
    #Return dataframe
    return df

# Test: Run analytical queries
conn = connect_database()

print("\n Datasets by Category:")
df_by_category = get_datasets_by_category_count(conn)
print(df_by_category)

print("\n Large Datasets by Source (>=10000 records):")
df_large = get_large_datasets_by_source(conn)
print(df_large)

print("\n Datasets with >10 Columns:")
df_many_columns = get_large_columns_datasets(conn)
print(df_many_columns)

conn.close()
