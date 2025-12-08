import pandas as pd

from app.data.db import connect_database

#Define class
class Dataset:
    """Represents a data science dataset in the platform."""

    #Initialise attributes
    def __init__(self, dataset_name:str, category:str, source:str, 
                 last_updated, record_count:int, column_count:int, file_size_mb):
        #Private attributes
        self.__dataset_name = dataset_name
        self.__category = category
        self.__source = source
        self.__last_updated = last_updated
        self.__record_count = record_count
        self.__column_count = column_count
        self.__file_size_mb = round(float(file_size_mb), 1) #Round file size to 1 floating point

    #Method to insert new dataset into database
    def insert_dataset(self) -> int:
        """Insert new dataset metadata into database"""
        #Connect to database
        conn = connect_database()

        #Create cursor
        cursor = conn.cursor()
        
        cursor.execute("""
                            INSERT INTO datasets_metadata
                            (dataset_name, category, source, last_updated,
                            record_count, column_count, file_size_mb)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,(self.__dataset_name, self.__category, self.__source, self.__last_updated,
                            self.__record_count, self.__column_count, self.__file_size_mb),
                        )
        
        #Save changes
        conn.commit()

        #Get id of inserted dataset
        self.__dataset_id = cursor.lastrowid

        #Close connection
        conn.close()

        #Return dataset id
        return self.__dataset_id
