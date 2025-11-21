from app.data.schema import create_all_tables
from app.data.db import connect_database
from app.services.user_service import register_user

conn = connect_database()
create_all_tables(conn)
conn.close()


