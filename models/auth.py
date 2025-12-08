import bcrypt
import re

#Define class
class User:
    """Represents a user in the Multi-Domain Intelligence Platform."""

    #Initialise attributes
    # 'username: str' informs that username is of string data type
    def __init__(self, username: str, password_hash: str):
        #Private attributes
        self.__username = username
        self.__password_hash = password_hash
        self.__password = ""

    #Method that returns username
    # '-> str' informs user that a string is expected to return
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

    #Password validation function
    # '-> tuple[bool, str]' shows that a tuple should be returned by function
    def validate_password(self, password: str) -> tuple[bool, str]:
        """
            Password validation

            Ensure that password contains: 
            -between 6 to 50 characters
            -at least one uppercase letter
            -at least one lowercase letter
            -at least one digit
            -at least one special character
        
        """

        #Initialise attribute
        self.__password = password

        #Check length of password
        #Use __len__ dunder method
        if not 6 < password.__len__() < 50:
            return False, "Password must contain between 6 and 50 characters"

        #Check for at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter (A-Z)"

        #Check for at least one lowercase letter
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter (a-z)"

        #Check for at least one digit
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit (0-9)"

        #Check for at least one special character
        if not re.search(r"[a-zA-Z0-9\s]", password):
            return False, "Password must contain at least one special character"

        #If all checks pass, return True (Correct password)
        return True, ""
