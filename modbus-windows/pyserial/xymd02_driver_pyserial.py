import serial
import time
import threading

# crc generator
def modbus_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

# read keep and input register - function code 0x03 and 0x04
def read_register(device_address: int, function_code: int, register_address: int) -> int:
    device_address_bytes = device_address.to_bytes(1, "big")
    function_code_bytes = function_code.to_bytes(1, "big")
    register_address_bytes = register_address.to_bytes(2, "big")
    quantity_hi = b'\x00'
    quantity_li = b'\x01'
    
    # request_message
    request_message = (device_address_bytes + 
                       function_code_bytes + 
                       register_address_bytes +
                       quantity_hi +
                       quantity_li)    
        
    # generate crc
    request_crc = modbus_crc16(request_message)
    request_crc_bytes = request_crc.to_bytes(2, 'little')
    
    # build frame
    request_frame = request_message + request_crc_bytes
    
    # debug
    # print(request_frame.hex(" ").upper())
    # request frame ok
    
    # send frame
    ser.write(request_frame)  
    
    # read response
    response_frame = ser.readline()
    
    #debug
    # print(response_frame.hex(' ').upper())
    # response frame ok

    response_frame_arr = bytearray(response_frame)
    
    # get response message
    response_message = (response_frame_arr[0].to_bytes(1, 'big') + 
                      response_frame_arr[1].to_bytes(1, 'big') + 
                      response_frame_arr[2].to_bytes(1, 'big') + 
                      response_frame_arr[3].to_bytes(1, 'big') +
                      response_frame_arr[4].to_bytes(1, 'big'))
    
    # get response crc
    crc_response_hi = response_frame_arr[5].to_bytes(1, 'big')
    crc_response_li = response_frame_arr[6].to_bytes(1, 'big')
    response_crc = crc_response_hi + crc_response_li
    
    # generate the supposed crc
    generated_crc = modbus_crc16(response_message)
    generated_crc_bytes = generated_crc.to_bytes(2, 'little')
    
    # validate response
    if len(response_frame_arr) == 7:
        if generated_crc_bytes == response_crc:
            # print("CRC OK! ...")
            data_hi = response_frame_arr[3]
            data_li = response_frame_arr[4]
            
            response = int.from_bytes([data_hi, data_li], byteorder="big")
            
            return response
        else:
            print("Checksum Error ... \n")
            return None
    else:
        print("Failed reading data ... \n")
        return None
    
    
    
# write a single keep register - function code 0x06
def write_register(device_address: int, register_address: int, value: int):
    device_address_bytes = device_address.to_bytes(1, "big")
    function_code_bytes = b'\x06'
    register_address_bytes = register_address.to_bytes(2, "big")
    value_bytes = value.to_bytes(2, "big")
    
    # request message to write
    request_message = (device_address_bytes +
                       function_code_bytes +
                       register_address_bytes +
                       value_bytes)
    
    # generate crc
    reqeust_crc = modbus_crc16(request_message)
    reqeust_crc_bytes = reqeust_crc.to_bytes(2, "little")
    
    # build frame
    request_frame = request_message + reqeust_crc_bytes
    
    # send frame
    ser.write(request_frame)
    
    # receive response frame
    response_frame = ser.readline()
    response_frame_arr = bytearray(response_frame)

    # get response message
    response_message = (response_frame_arr[0].to_bytes(1, 'big') + 
                      response_frame_arr[1].to_bytes(1, 'big') + 
                      response_frame_arr[2].to_bytes(1, 'big') + 
                      response_frame_arr[3].to_bytes(1, 'big') +
                      response_frame_arr[4].to_bytes(1, 'big') +
                      response_frame_arr[5].to_bytes(1, 'big'))
    
    # get response crc
    crc_response_hi = response_frame_arr[6].to_bytes(1, 'big')
    crc_response_li = response_frame_arr[7].to_bytes(1, 'big')
    response_crc = crc_response_hi + crc_response_li
    
    # generate the supposed crc
    generated_crc = modbus_crc16(response_message)
    generated_crc_bytes = generated_crc.to_bytes(2, 'little')
    
    # validate response
    if len(response_frame_arr) == 8:
        if generated_crc_bytes == response_crc:
            # print("CRC OK! ...")
            return True
        else:
            print("Checksum Error ... \n")
            return False
    else:
        print("Failed reading data ... \n")
        return False
    
    

# thread read sensor
def read_sensor():
    print("Reading sensor data ... \n")
    
    counter = 1
    
    while reading:
        # read input register
        temperature = read_register(1, 4, 1)
        if temperature != None:
            temperature = temperature/10
        humidity = read_register(1, 4, 2)
        if humidity != None:
            humidity = humidity/10

        # read keep register
        device_address = read_register(1, 3, 257)
        baudrate = read_register(1, 3, 258)
        temp_correction = read_register(1, 3, 259)
        hum_correction = read_register(1, 3, 260)
         
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
        
        time.sleep(1)
        
# write sensor
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
        if write_register(device_address = 1, register_address = 257, value = change):
            print("\nChanged device address to", change, "\n")
        else:
            print("\nFailed to change device address")
        
    elif write == 2:
        change = int(input("Change Baud Rate (9600, 14400, 19200): "))
        if write_register(device_address = 1, register_address = 258, value = change):
            print("\nChanged baud rate to", change, "\n")
        else:
            print("\nFailed to change baudrate")
        
    elif write == 3:
        change = int(input("Change Temperature Correction (-10 to 10): "))
        if write_register(device_address = 1, register_address = 259, value = change):
            print("\nChanged temperature correction to", change, "\n")
        else:
            print("\nFailed to change temperature correction")
 
    elif write == 4:
        change = int(input("Change Humidity Correction (-10 to 10): "))
        if write_register(device_address = 1, register_address = 260, value = change):
            print("\nChanged humidity correction to", change, "\n")
        else:
            print("\nFailed to change humidity correction")
 
    else:
        print("Invalid Input")

# main menu
try:
    ser = serial.Serial(port = "COM16", baudrate = 9600, timeout=2)
    time.sleep(1)  # wait for device init
    
    reading = False
    running = True
    
    while running: 
        print("=== XY-MD02 Sensor Driver (Pyserial) ===")
        print("1. Read Registers")
        print("2. Write Registers")
        print("3. Exit\n")
        
        menu = int(input("Input: "))
        if menu == 1:
            reading = True
            threading.Thread(target=read_sensor).start()
            input("")
            reading = False

        elif menu == 2:
            print("")
            write_sensor()

        elif menu == 3:
            print("\nProgram Closed ... \n")
            running = False

        else:
            print("\nInvalid Input")

    ser.close()

except serial.SerialException as e:
    print(f"Serial error: {e}")
except FileNotFoundError:
    print("Port not found. Check device connection.")
except PermissionError:
    print("Permission denied. Add yourself to the dialout group (Linux).")