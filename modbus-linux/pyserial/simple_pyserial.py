import serial
import time

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

# # Verify: read 3 holding registers from slave 1, starting at address 1
# frame = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x03])
# crc = modbus_crc16(frame)
# print(f"CRC: 0x{crc:04X}")
# print(f"Frame: {(frame + crc.to_bytes(2, 'little')).hex().upper()}")

def modbus_read_temperature(): # input register: 0x04
    # send format: device address, function code, starting address HI,
    #              starting address Li, quantitiy Hi, quantity Li, CRC Hi,
    #              CRC Li
    # data frame (XY-MD02)
    # request message: 0x01, 0x04, 0x00, 0x01, 0x00, 0x01, 0x60, 0x0A
    # response message (expected): 0x01, 0x04, 0x02, temp Hi, temp Li, 0x79, 0x74
    
    # request_frame = request_message + request_crc
    
    # base message to reqeust temperature
    request_message = bytes([0x01, 0x04, 0x00, 0x01, 0x00, 0x01])
    
    # calculate crc for the message
    request_crc = modbus_crc16(request_message) # return int
    request_crc_bytes = request_crc.to_bytes(2, 'little')
    
    # complete message to send
    request_frame = request_message + request_crc_bytes
    
    print("===== SENDING TEMP REQUEST ============================")
    print(f"Temp frame request: {request_frame.hex(' ').upper()}")
    print(f"Temp message request: {bytes([0x01, 0x04, 0x00, 0x01]).hex(' ').upper()}")
    print(f"Temp CRC request: {request_crc_bytes.hex(' ').upper()}")
    print("===== READING TEMP RESPONSE ===========================")
    
    ser.write(request_frame)
    
    # response_frame = response_message + response_crc
    # response from sensor
    response_frame = ser.readline()
    print(f"Temp frame response: {response_frame.hex(' ').upper()}")
    
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
    
    print(f"Temp message response: {response_message.hex(' ').upper()}")
    print(f"Temp crc response: {response_crc.hex(' ').upper()}")
    
    # generate the supposed crc
    generated_crc = modbus_crc16(response_message)
    generated_crc_bytes = generated_crc.to_bytes(2, 'little')
    print("===== GENERATING CRC TO CHECK =========================")    
    print(f"Temp crc generated: {response_crc.hex(' ').upper()}")
    
    
    # validate response
    if len(response_frame_arr) == 7:
        if generated_crc_bytes == response_crc:
            print("CRC OK! ...")
            temp_hi = response_frame_arr[3]
            temp_li = response_frame_arr[4]
            
            response = int.from_bytes([temp_hi, temp_li], byteorder="big")
            
            return response
        else:
            print("Checksum Error ... \n")
            return None
    else:
        print("Failed reading data ... \n")
        return None

def modbus_read_humidity(): # input register: 0x04
    # send format: device address, function code, starting address HI,
    #              starting address Li, quantitiy Hi, quantity Li, CRC Hi,
    #              CRC Li
    # data frame (XY-MD02)
    # request message: 0x01, 0x04, 0x00, 0x02, 0x00, 0x01, 0x60, 0x0A
    # response message (expected): 0x01, 0x04, 0x02, hum Hi, hum Li, 0x79, 0x74
    
    # request_frame = request_message + request_crc
    
    # base message to reqeust temperature
    request_message = bytes([0x01, 0x04, 0x00, 0x02, 0x00, 0x01])
    
    # calculate crc for the message
    request_crc = modbus_crc16(request_message) # return int
    request_crc_bytes = request_crc.to_bytes(2, 'little')
    
    # complete message to send
    request_frame = request_message + request_crc_bytes
    
    print("===== SENDING HUM REQUEST =============================")
    print(f"Hum frame request: {request_frame.hex(' ').upper()}")
    print(f"Hum message request: {bytes([0x01, 0x04, 0x00, 0x01]).hex(' ').upper()}")
    print(f"Hum CRC request: {request_crc_bytes.hex(' ').upper()}")
    print("===== READING HUM RESPONSE ============================")
    
    ser.write(request_frame)
    
    # response_frame = response_message + response_crc
    # response from sensor
    response_frame = ser.readline()
    print(f"Hum frame response: {response_frame.hex(' ').upper()}")
    
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
    
    print(f"Hum message response: {response_message.hex(' ').upper()}")
    print(f"Hum crc response: {response_crc.hex(' ').upper()}")
    
    # generate the supposed crc
    generated_crc = modbus_crc16(response_message)
    generated_crc_bytes = generated_crc.to_bytes(2, 'little')
    print("===== GENERATING CRC TO CHECK =========================")    
    print(f"Hum crc generated: {response_crc.hex(' ').upper()}")
    
    
    # validate response
    if len(response_frame_arr) == 7:
        if generated_crc_bytes == response_crc:
            print("CRC OK! ...")
            hum_hi = response_frame_arr[3]
            hum_li = response_frame_arr[4]
            
            response = int.from_bytes([hum_hi, hum_li], byteorder="big")
            
            return response
        else:
            print("Checksum Error ... \n")
            return None
    else:
        print("Failed reading data ... \n")
        return None
    
try:
    ser = serial.Serial(port = "/dev/ttyS0", baudrate = 9600, timeout=2)
    time.sleep(1)  # wait for device init

    temperature = modbus_read_temperature()/10
    print("=======================================================")
    print("Temperature:", temperature)
    print("=======================================================\n\n\n")
    
    humidity = modbus_read_humidity()/10
    print("=======================================================")
    print("Humidity:", humidity)
    print("=======================================================\n\n\n")

    ser.close()

except serial.SerialException as e:
    print(f"Serial error: {e}")
except FileNotFoundError:
    print("Port not found. Check device connection.")
except PermissionError:
    print("Permission denied. Add yourself to the dialout group (Linux).")
