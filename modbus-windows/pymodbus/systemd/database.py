# Module Imports
import mariadb # type: ignore
import sys
from datetime import datetime

class Db():
    def __init__(self):
        # Connect to MariaDB Platform
        try:
            self.connection = mariadb.connect(
                user="db_user",
                password="db_user_passwd",
                host="localhost",
                port=3306,
                database="testdatabase"
            )
            
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        self.mycursor = self.connection.cursor()
        # self.mycursor.execute("ALTER TABLE Sensor MODIFY COLUMN temperature FLOAT")
        # self.mycursor.execute("ALTER TABLE Sensor MODIFY COLUMN humidity FLOAT")
        
    def insert_log(self, temperature, humidity):
        self.mycursor.execute("INSERT INTO Sensor (time, temperature, humidity) VALUES (%s, %s, %s)", (datetime.now(), temperature, humidity))
        self.connection.commit()
        
    def close_db(self):
        self.mycursor.close()
        self.connection.close()