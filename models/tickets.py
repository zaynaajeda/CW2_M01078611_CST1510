from app.data.db import connect_database

#Define class for IT Ticket
class ITTicket:
    """Represents an IT ticket."""

    #Initialise attributes
    def __init__(self, ticket_id):
        self.__ticket_id = ticket_id

    #Method to update status of IT ticket in database
    def update_ticket(self, new_status) -> int:
        """Update status of a ticket."""
        #Connect to database
        conn = connect_database()

        #Create cursor
        cursor = conn.cursor()

        #Execute update statement
        cursor.execute("""
                        UPDATE it_tickets SET status = ? WHERE id = ?
                        """,
                        (new_status, self.__ticket_id),
                    )
        
        #Save changes
        conn.commit()

        #Get number of updated rows
        row_count = cursor.rowcount

        #Close connection
        conn.close()

        #Return number of updated rows
        return row_count
