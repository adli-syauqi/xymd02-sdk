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
        
        self.client = ModbusSerialClient(port=connect_port, stopbits = 1, bytesize = 8, parity = "N", baudrate = connect_baudrate)
        self.client.connect() 
    
    def read(self, device_id):
        # read input register
        temperature_response = self.client.read_input_registers(address = 0x0001, count = 1, device_id = device_id)
        humidity_response = self.client.read_input_registers(address = 0x0002, count = 1, device_id = device_id)

        # read keep register
        device_address_response = self.client.read_holding_registers(address = 0x0101, count = 1, device_id = device_id)
        baudrate_response = self.client.read_holding_registers(address = 0x0102, count = 1, device_id = device_id)
        temp_correction_response = self.client.read_holding_registers(address = 0x0103, count = 1, device_id = device_id)
        hum_correction_response = self.client.read_holding_registers(address = 0x0104, count = 1, device_id = device_id)

        self.temperature = temperature_response.registers[0]/10
        self.humidity = humidity_response.registers[0]/10
        self.device_address = device_address_response.registers[0]
        self.baudrate = baudrate_response.registers[0]
        self.temp_correction = temp_correction_response.registers[0]/10
        self.hum_correction = hum_correction_response.registers[0]/10
        
    def disconnect(self):
        self.client.close()
        
    def modify(self, deviceid, changeid, changebr, changehc, changetc):
        self.client.write_register(address = 0x0101, value = changeid, device_id = deviceid)
        self.client.write_register(address = 0x0102, value = changebr, device_id = deviceid)
        self.client.write_register(address = 0x0103, value = 10*changetc, device_id = deviceid)
        self.client.write_register(address = 0x0104, value = 10*changehc, device_id = deviceid)