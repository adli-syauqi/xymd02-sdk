import time
import threading
import csv
from datetime import datetime
from pymodbus.client import ModbusSerialClient #type: ignore
 
client = ModbusSerialClient(port="COM16", stopbits = 1, bytesize = 8, parity = "N", baudrate = 9600)
client.connect()

reading = False
running = True    

def read_sensor():
    print("Reading sensor data ... \n")
    
    counter = 1
    
    while reading:
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
        
        print("Press ENTER to Exit")
        print("Data No-" + str(counter))
        counter += 1
    
        print("Temperature =", temperature)
        print("Humidity =", humidity)
        print("Device Address =", device_address)
        print("Baudrate =", baudrate)
        print("Temperature Correction =", temp_correction)
        print("Humidity Correction =", hum_correction)
        print("")
        
        now = datetime.now()
        
        with open("log.csv", "a") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([now, temperature, humidity, device_address, baudrate, temp_correction, hum_correction])
        time.sleep(5)
    
def write_sensor():
    print("=== Write Sensor Register ===")
    print("1. Change Address")
    print("2. Change Baud Rate")
    print("3. Change Temperature Correction")
    print("4. Change Humidity Correction\n")    

    write = int(input())
    print("")

    if write == 1:
        change = int(input("Change Address (1-247): "))
        client.write_register(address = 0x0101, value = change, device_id = 1)
        print("\nChanged device address to", change, "\n")
        
    elif write == 2:
        change = int(input("Change Baud Rate (9600, 14400, 19200): "))
        client.write_register(address = 0x0102, value = change, device_id = 1)
        print("\nChanged baud rate to", change, "\n")
        
    elif write == 3:
        change = int(input("Change Temperature Correction (-10 to 10): "))
        client.write_register(address = 0x0103, value = 10*change, device_id = 1)
        print("\nChanged temperature correction to", change, "\n")
        
    elif write == 4:
        change = int(input("Change Humidity Correction (-10 to 10): "))
        client.write_register(address = 0x0104, value = 10*change, device_id = 1)
        print("\nChanged humidity correction to", change, "\n")
        
    else:
        print("Invalid Input")
        

while running:
    print("=== XY-MD02 Sensor Driver (Pymodbus) ===")
    print("1. Read Registers")
    print("2. Write Registers")
    print("3. Exit\n")
    
    menu = int(input())
    if menu == 1:
        reading = True
        threading.Thread(target=read_sensor).start()
        input("")
        reading = False

    elif menu == 2:
        print("")
        write_sensor()

    elif menu == 3:
        print("\nProgram Closed")
        running = False

    else:
        print("\nInvalid Input")

client.close()
print("")
print("Ports Now Closed")