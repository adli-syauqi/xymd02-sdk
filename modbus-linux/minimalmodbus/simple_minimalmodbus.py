import minimalmodbus
import time

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
sensy_boi.debug = True


print("Requesting Data From Sensor ... \n")
counter = 1

while True:
    print("Data No-" + str(counter))
    counter += 1
    
    temperature = sensy_boi.read_register(1, 1, 4, False)
    print("Temperature =", temperature, "C")
    
    time.sleep(1)
