from pymodbus.client import ModbusSerialClient #type: ignore
 
client = ModbusSerialClient(port="COM16", stopbits = 1, bytesize = 8, parity = "N", baudrate = 9600)
 
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

print("Temperature =", temperature)
print("Humidity =", humidity)
print("Device Address =", device_address)
print("Baudrate =", baudrate)
print("Temperature Correction =", temp_correction)
print("Humidity Correction =", hum_correction)

client.close()