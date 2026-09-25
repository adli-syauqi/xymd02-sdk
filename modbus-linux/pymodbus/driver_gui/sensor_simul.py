from pymodbus.client import ModbusSerialClient #type: ignore
import time

class Sensor():
    # connect
    def __init__(self, connect_port, connect_baudrate):
        self.temperature = 0
        self.humidity = 0
        self.device_address = 0
        self.baudrate = 0    
        self.temp_correction = 0
        self.hum_correction = 0
        
        # self.client = ModbusSerialClient(port=connect_port, stopbits = 1, bytesize = 8, parity = "N", baudrate = connect_baudrate)
        # self.client.connect() 
    
    def read(self,device_id):
        # # read input register
        # temperature_response = self.client.read_input_registers(address = 0x0001, count = 1, device_id = 1)
        # humidity_response = self.client.read_input_registers(address = 0x0002, count = 1, device_id = 1)

        # # read keep register
        # device_address_response = self.client.read_holding_registers(address = 0x0101, count = 1, device_id = 1)
        # baudrate_response = self.client.read_holding_registers(address = 0x0102, count = 1, device_id = 1)
        # temp_correction_response = self.client.read_holding_registers(address = 0x0103, count = 1, device_id = 1)
        # hum_correction_response = self.client.read_holding_registers(address = 0x0104, count = 1, device_id = 1)

        self.temperature += 1
        self.humidity += 1
        self.device_address += 1
        self.baudrate += 1
        self.temp_correction += 1
        self.hum_correction += 1
        
    def disconnect(self):
        self.client.close()
