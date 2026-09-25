import os
import time
import csv
import ftplib
from datetime import datetime
import mariadb  # type: ignore
from pymodbus.client import ModbusSerialClient  # type: ignore

# ----------------- CONFIGURATION -----------------
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

DB_CONFIG = {
    "user": "adli",
    "password": "adli",
    "host": "localhost",
    "port": 3306,
    "database": "sensor_adli",
    "connect_timeout": 5
}

CSV_FILE = "sensor_data.csv"
MAX_CSV_ROWS = 100               # Threshold to trigger upload
POLL_INTERVAL = 2                # Sensor polling rate in seconds

FTP_HOST = "192.168.1.50"        # Target PC IP on direct Ethernet
FTP_PORT = 21
FTP_USER = "ftpuser"
FTP_PASS = "ftppass"
FTP_TIMEOUT = 5
# --------------------------------------------------


def get_db_connection():
    """Establish and return a MariaDB connection."""
    try:
        conn = mariadb.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except mariadb.Error as e:
        print(f"[DB] Connection failed: {e}")
        return None


def get_modbus_client():
    """Initialize Modbus Serial Client."""
    return ModbusSerialClient(
        port=SERIAL_PORT,
        stopbits=1,
        bytesize=8,
        parity="N",
        baudrate=BAUDRATE,
        timeout=1
    )


def append_to_csv(filepath, row_data):
    """Safely append row and initialize headers if new file."""
    file_exists = os.path.isfile(filepath)
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "temperature", "humidity", "device_id", "baudrate"])
        writer.writerow(row_data)


def count_csv_rows(filepath):
    if not os.path.isfile(filepath):
        return 0
    with open(filepath, "r") as f:
        return sum(1 for _ in f) - 1  # Exclude header


def attempt_ftp_upload(file_path):
    """
    Check if target host is reachable via FTP and transfer file.
    Returns True if uploaded and removed locally.
    """
    temp_upload_name = f"uploading_{int(time.time())}.csv"
    os.rename(file_path, temp_upload_name)

    try:
        with ftplib.FTP() as ftp:
            ftp.connect(FTP_HOST, FTP_PORT, timeout=FTP_TIMEOUT)
            ftp.login(FTP_USER, FTP_PASS)
            
            with open(temp_upload_name, "rb") as f:
                remote_filename = f"sensor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                ftp.storbinary(f"STOR {remote_filename}", f)

            print(f"[FTP] Successfully uploaded {remote_filename}")
        
        os.remove(temp_upload_name)
        return True

    except (ftplib.all_errors, OSError) as e:
        print(f"[FTP] Target unreachable or upload failed: {e}")
        # Restore or queue for next attempt
        if os.path.exists(temp_upload_name):
            if os.path.exists(file_path):
                # Append staged back to main if created in between
                with open(temp_upload_name, "r") as src, open(file_path, "a") as dst:
                    next(src)  # Skip header
                    dst.writelines(src.readlines())
                os.remove(temp_upload_name)
            else:
                os.rename(temp_upload_name, file_path)
        return False



db_conn = None
mb_client = get_modbus_client()

print("[SYSTEM] Industrial sensor logger service initialized.")

while True:
    # 1. Maintain Database Connection
    if db_conn is None:
        db_conn = get_db_connection()
    else:
        try:
            db_conn.ping()
        except mariadb.Error:
            print("[DB] Lost connection. Reconnecting...")
            db_conn = get_db_connection()

    # 2. Query Sensor over Modbus
    sensor_data = None
    try:
        if not mb_client.connected:
            mb_client.connect()

        # Read inputs (Temperature & Humidity)
        t_res = mb_client.read_input_registers(address=0x0001, count=1, slave=1)
        h_res = mb_client.read_input_registers(address=0x0002, count=1, slave=1)

        # Read device metadata
        addr_res = mb_client.read_holding_registers(address=0x0101, count=1, slave=1)
        baud_res = mb_client.read_holding_registers(address=0x0102, count=1, slave=1)

        if not (t_res.isError() or h_res.isError()):
            temp = t_res.registers[0] / 10.0
            hum = h_res.registers[0] / 10.0
            dev_addr = addr_res.registers[0] if not addr_res.isError() else 1
            baud = baud_res.registers[0] if not baud_res.isError() else BAUDRATE

            sensor_data = {
                "time": datetime.now(),
                "temp": temp,
                "hum": hum,
                "dev_addr": dev_addr,
                "baud": baud
            }
        else:
            print("[MODBUS] Packet error or sensor timeout.")
            mb_client.close()

    except Exception as e:
        print(f"[MODBUS] Communication failure: {e}")
        mb_client.close()

    # 3. Store Data (DB + CSV)
    if sensor_data:
        # DB Insertion
        if db_conn:
            try:
                cursor = db_conn.cursor()
                cursor.execute(
                    "INSERT INTO sensor (time, temperature, humidity) VALUES (%s, %s, %s)",
                    (sensor_data["time"], sensor_data["temp"], sensor_data["hum"])
                )
                cursor.close()
            except mariadb.Error as e:
                print(f"[DB] Insert failed: {e}")

        # CSV Logging
        csv_row = [
            sensor_data["time"].strftime("%Y-%m-%d %H:%M:%S"),
            sensor_data["temp"],
            sensor_data["hum"],
            sensor_data["dev_addr"],
            sensor_data["baud"]
        ]
        append_to_csv(CSV_FILE, csv_row)

    # 4. Check CSV Threshold & Attempt FTP Dispatch
    current_rows = count_csv_rows(CSV_FILE)
    if current_rows >= MAX_CSV_ROWS:
        print(f"[BUFFER] CSV reached {current_rows} lines. Checking Ethernet link...")
        attempt_ftp_upload(CSV_FILE)

    time.sleep(5)

