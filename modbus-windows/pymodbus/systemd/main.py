from pymodbus.client import ModbusSerialClient #type: ignore
import mariadb #type: ignore
from datetime import datetime
import time
import csv
# from ftp import 

#setup
client = ModbusSerialClient(port="/dev/ttyUSB0", stopbits = 1, bytesize = 8, parity = "N", baudrate = 9600)
connection = mariadb.connect(user="adli", password="adli", host="localhost", port=3306, database="sensor_adli")


while True:
    # connect to sensor
    try:
        client.connect()
        
        # read input register
        temperature_response = client.read_input_registers(address = 0x0001, count = 1, device_id = 1)
        humidity_response = client.read_input_registers(address = 0x0002, count = 1, device_id = 1)

        # read keep register
        device_address_response = client.read_holding_registers(address = 0x0101, count = 1, device_id = 1)
        baudrate_response = client.read_holding_registers(address = 0x0102, count = 1, device_id = 1)
        temp_correction_response = client.read_holding_registers(address = 0x0103, count = 1, device_id = 1)
        hum_correction_response = client.read_holding_registers(address = 0x0104, count = 1, device_id = 1)

        temperature = temperature_response.registers[0]/10
        humidity = humidity_response.registers[0]/10
        device_address = device_address_response.registers[0]
        baudrate = baudrate_response.registers[0]
        temp_correction = temp_correction_response.registers[0]/10
        hum_correction = hum_correction_response.registers[0]/10
        
        client.close()
        sensor_valid = True
        
    except Exception as e :
        print("modbus fail\n")
        client.close()
        sensor_valid = False
    
    
    # connect to database
    
    
    try:
        if sensor_valid:
            mycursor = connection.cursor()
            mycursor.execute("INSERT INTO sensor (time, temperature, humidity) VALUES (%s, %s, %s)", (datetime.now(), temperature, humidity))
            connection.commit()
            mycursor.close()
            connection.close()
        else:
            pass
        
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    
    finally:
        if mycursor:
            mycursor.close()
        if connection:
            connection.close()
            
    # try:
    #     if sensor_valid:
    #         now = datetime.now()
    #         with open("log.csv", "a") as csv_file:
    #             csv_writer = csv.writer(csv_file)
    #             csv_writer.writerow([now, temperature, humidity, device_address, baudrate, temp_correction, hum_correction])
    #     else:
    #         pass
    # except:
    #     print("FTP failed")