from app.data.db import connect_database


class ITTicket:
    """Represents an existing IT ticket and allows status updates."""

    #Initialise attributes
    def __init__(self, ticket_id: int):
        #Private attributes
        self._ticket_id = ticket_id

    def update_ticket(self, new_status: str) -> int:
        """Update status of a ticket."""
        #Connect to database
        conn = connect_database()

        #Create cursor object
        cursor = conn.cursor()

        #Execute update statement
        cursor.execute("""
                        UPDATE it_tickets SET status = ? WHERE id = ?
                        """, (new_status, self._ticket_id))
        
        #Save changes
        conn.commit()
        #Get number of updated rows
        row_count = cursor.rowcount

        #Close database connection
        conn.close()
        #Return number of updated rows
        return row_count


class NewITTicket(ITTicket):
    """Child class to insert new tickets in database"""

    #Initialise attributes
    def __init__(self, priority, status, category, subject, description, created_date, resolved_date, assigned_to):
        #Relate to parent class attribute
        super().__init__(ticket_id=0)

        #Private attributes
        self.__priority = priority
        self.__status = status
        self.__category = category 
        self.__subject = subject 
        self.__description = description
        self.__created_date = created_date
        self.__resolved_date = resolved_date
        self.__assigned_to = assigned_to

    def insert_ticket(self) -> int:
        #Connect to database
        conn = connect_database()
        #Create cursor object
        cursor = conn.cursor()

        #Execute insert statement
        cursor.execute("""
                        INSERT INTO it_tickets
                        (priority, status, category, subject, description,
                        created_date, resolved_date, assigned_to)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,(self.__priority, self.__status, self.__category, self.__subject,
                            self.__description, self.__created_date, self.__resolved_date, self.__assigned_to))
        
        #Save changes
        conn.commit()

        #Get id of inserted ticket
        self._ticket_id = cursor.lastrowid

        #Close database connection
        conn.close()
        #Return ticket id
        return self._ticket_id
