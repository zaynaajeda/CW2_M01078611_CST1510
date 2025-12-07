import bcrypt

#Define class
class User:
    """Represents a user in the Multi-Domain Intelligence Platform."""

    #Initialise attributes
    def __init__(self, username: str, password_hash: str):
        #Private attributes
        self.__username = username
        self.__password_hash = password_hash

    #Method that returns username
    def get_username(self) -> str:
        return self.__username

    #Method to verify plain text password with hashed password
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Check if plain-text password matches hashed password
        Encode plain-text password using bcrypt

        """
        #Encode plain text password into bytes
        password_bytes = plain_password.encode("utf-8")
        #isinstance checks if the hashed_password is already in byte
        if isinstance(hashed_password, bytes):
            #hashed_password is used as it is if it is already in byte format       
            hashed_password_bytes = hashed_password
        else:
            #If not in byte, password is encoded into bytes
            hashed_password_bytes = hashed_password.encode("utf-8")

        #Both encoded passwords are compared and Trye/False is returned 
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
