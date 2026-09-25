import mysql.connector # type: ignore
from datetime import datetime

class Db():
    def __init__(self):
        self.connection = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = "root",
            database = "testdatabase"
        )

        self.mycursor = self.connection.cursor()
        # self.mycursor.execute("ALTER TABLE Sensor MODIFY COLUMN temperature FLOAT")
        # self.mycursor.execute("ALTER TABLE Sensor MODIFY COLUMN humidity FLOAT")
        
    def insert_log(self, temperature, humidity):
        self.mycursor.execute("INSERT INTO Sensor (time, temperature, humidity) VALUES (%s, %s, %s)", (datetime.now(), temperature, humidity))
        self.connection.commit()
        
    def close_db(self):
        self.mycursor.close()
        self.connection.close()