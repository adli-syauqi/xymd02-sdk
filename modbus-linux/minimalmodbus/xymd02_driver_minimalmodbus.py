# minimalmodbus to read the xy-md02 sensor

import minimalmodbus
import time
import threading

mb_address = 1

sensy_boi = minimalmodbus.Instrument('/dev/ttyS0', mb_address)

sensy_boi.serial.baudrate = 9600

sensy_boi.serial.bytesize = 8
sensy_boi.serial.parity = minimalmodbus.serial.PARITY_NONE
sensy_boi.serial.stopbits = 1
sensy_boi.serial.timeout = 1
sensy_boi.mode = minimalmodbus.MODE_RTU

refresh_rate = 1

sensy_boi.clear_buffers_before_each_transaction = True
sensy_boi.close_port_after_each_call = True
# sensy_boi.debug = True

print(sensy_boi)

print("")

done = False

def read_sensor():
        print("Requesting Data From Sensor ... \n")

        counter = 1

        while not done:
                print("Press ENTER to Exit")
                print("Data No-" + str(counter))
                counter += 1

                # read registers: (register address, number of decimals, function code, signed/unsigned)
                temperature = sensy_boi.read_register(1, 1, 4, False)
                time.sleep(0.1)
                humidity = sensy_boi.read_register(2, 1, 4, False)
                time.sleep(0.1)
                device_address = sensy_boi.read_register(257, 0, 3, False)
                time.sleep(0.1)
                baud_rate = sensy_boi.read_register(258, 0, 3, False)
                time.sleep(0.1)
                temperature_correction = sensy_boi.read_register(259, 1, 3, False)
                time.sleep(0.1)
                humidity_correction = sensy_boi.read_register(260, 1, 3, False)

                print("Temperature =", temperature, "C")
                print("Humidity =", humidity, "RH")
                print("Device Address =", device_address)
                print("BAUD Rate =", baud_rate)
                print("Temperature Correction =", temperature_correction)
                print("Humidity Correction =", humidity_correction)
                print("")

                time.sleep(refresh_rate)

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
                sensy_boi.write_register(257, change, 0, 6, False)
                print("\nChanged device address to", change, "\n")

        elif write == 2:
                change = int(input("Change Baud Rate (9600, 14400, 19200): "))
                sensy_boi.write_register(258, change, 0, 6, False)
                print("\nChanged baud rate to", change, "\n")

        elif write == 3:
                change = int(input("Change Temperature Correction (-10 to 10): "))
                sensy_boi.write_register(259, change, 1, 6, False)
                print("\nChanged temperature correction to", change, "\n")

        elif write == 4:
                change = int(input("Change Humidity Correction (-10 to 10): "))
                sensy_boi.write_register(260, change, 1, 6, False)
                print("\nChanged humidity correction to", change, "\n")

        else:
                print("Invalid Input")

running = True

while running:
        print("=== XY-MD02 Sensor Driver (Minimal Modbus) ===")
        print("1. Read Registers")
        print("2. Write Registers")
        print("3. Exit\n")

        menu = int(input())
        if menu == 1:
                threading.Thread(target=read_sensor).start()
                input("")
                done = True

        elif menu == 2:
                print("")
                write_sensor()

        elif menu == 3:
                print("\nProgram Closed")
                running = False

        else:
                print("\nInvalid Input")

sensy_boi.serial.close()
print("")
print("Ports Now Closed")
