from datetime import datetime
import mariadb
import sys

current_time = datetime.now()

test_temperature = 26.5
test_humidity = 60.2

try:
    conn = mariadb.connect(
        user="adli",
        password="adli",
        host="localhost",
        port=3306,
        database="sensor_adli" 
    )
    print("Connected successfully!")

except mariadb.Error as e:
    print(f"Error connecting: {e}")
    sys.exit(1)

cursor = conn.cursor()

try:
    cursor.execute("INSERT INTO sensor (recorded_at, temperature, humidity) VALUES (%s, %s, %s)", (datetime.now(), test_temperature, test_humidity))
    conn.commit()
    print(f"Logged data successfully at {current_time}!")

except mariadb.Error as e:
    print(f"Failed to insert data: {e}")

cursor.close()
conn.close()
