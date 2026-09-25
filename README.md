# XYMD02 SDK

Python drivers for reading data from the XY-MD02 Modbus RTU
temperature & humidity sensor (RS485, SHT20 chip). Includes both Linux
(tested on Raspberry Pi 4B) and Windows versions, with three different
implementation variants of Modbus libraries: minimalmodbus, pymodbus, and serial

## Sensor overview

- **Model:** XY-MD02
- **Interface:** Tested with USB RS485 converter
- **Measures:** Temperature (-40°C to 80°C, ±0.5°C) and Humidity (0-100% RH, ±3% RH)
- **Default settings:** 9600 baudrate, 8 data bits, no parity, 1 stop bit, slave address 1, port "COM16" (Windows) or "/dev/ttyS0" (Linux)

## Structure

Each platform folder (`modbus-linux/`, `modbus-windows/`) contains three
variants of the same driver, one per Modbus library:

| Folder            | Library       | Usage |
|--------------------|---------------|---------------|
| `minimalmodbus/`   | minimalmodbus | Quick/simple use|
| `pymodbus/`        | pymodbus      | Feature rich scripts (GUI, service)|
| `pyserial/`        | pyserial      | Full manual control|

Each variant folder contains (at minimum):

- **`simple_xymd02_driver_<library>.py`** — reads temperature/humidity once
  and prints to terminal.
- **`xymd02_driver_<library>.py`** — CLI-based driver that reads data in a
  loop and lets you modify sensor parameters (address/ID, baud rate,
  temperature/humidity correction offset).
- **`requirements.txt`** — dependencies for that variant.

The `pymodbus` variant additionally includes two standalone extensions:

- **`driver_gui/`** — a PySide6 GUI for the driver. Lets you select
  connection parameters, modify sensor settings, and view live sensor
  output as a graph.
- **`service/`** *(Linux only)* — a robust, plug-and-play service intended
  to run indefinitely on the Raspberry Pi. On boot, it waits for both the
  sensor connection and an Ethernet link to the host PC, then:
  - reads sensor data continuously,
  - writes it to a local database,
  - saves csv logs locally,
  - and pushes it to the host PC via FTP every 5 minutes.

  It's also designed to be resilient against sudden power loss or cable
  disconnection. It has recovery logic and resumes automatically without a manual restart. See below for step by step configuration. 


## Requirements

- Python 3.9.2+
- Dependencies listed in `requirements.txt`

Install with:
```bash
pip install -r requirements.txt
```

## Usage

### CLI driver

### Desktop GUI

### Autonomous Service


<!-- ## Notes / Known limitations

- `service/` is still work in progress
- The basic terminal driver requires you to open the python files to modify the parameters -->
