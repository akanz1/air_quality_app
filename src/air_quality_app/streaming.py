import sys
from datetime import datetime

import pytz
import serial
from influxdb import InfluxDBClient
from serial.tools import list_ports


def read_streaming_data(serial_object: serial.Serial):
    while True:
        lst = []
        lst.append(
            datetime.now(tz=pytz.timezone("Europe/Berlin")).strftime("%Y%m%d_%H%M%S%f")
        )

        for j in range(17):
            if j in [1, 16]:
                x = ord(serial_object.read())
                lst.append(x)
            else:
                x = int.from_bytes(serial_object.read(), byteorder=sys.byteorder)
                lst.append(x)

        yield lst


def preprocess_data(lst: list) -> dict:
    keys = [
        "CO2_ppm",
        "CH20_ugm3",
        "TVOC_ugm3",
        "PM2.5",
        "PM10",
        "Temperature",
        "Humidity",
        "Checksum",
    ]

    CO2_ppm = lst[3] << 8 | lst[4]
    CH20 = lst[5] << 8 | lst[6]
    TVOC_ugm3 = lst[7] << 8 | lst[8]
    PM25 = lst[9] << 8 | lst[10]
    PM10 = lst[11] << 8 | lst[12]
    temperature = lst[13] + lst[14] / 10
    humidity = lst[15] + lst[16] / 10

    timestamp = lst.pop(0)
    checksum = (sum(lst) - lst[-1] - 256) == lst[-1]
    values = [CO2_ppm, CH20, TVOC_ugm3, PM25, PM10, temperature, humidity, checksum]

    data_dict = dict(zip(keys, values))
    # entry = {timestamp: data_dict}
    return data_dict


def db_exists(client: InfluxDBClient, dbname: str) -> bool:
    """returns True if the database exists"""
    dbs = client.get_list_database()
    for db in dbs:
        if db["name"] == dbname:
            return True
    return False


def connect_db(client: InfluxDBClient, dbname: str):
    """connect to the database, and create it if it does not exist"""
    print("connecting to database...")
    if not db_exists(client, dbname):
        print(f"creating database {dbname}")
        client.create_database(dbname)
    else:
        print("database already exists")
        client.switch_database(dbname)


if __name__ == "__main__":
    dbname = "air_quality_db"
    try:
        client = InfluxDBClient(
            host="influxdb",
            port=8086,
            username="influxdb",
            password="influxdb",
            database=dbname,
        )
        print(client.ping())
        connect_db(client, dbname)
        print("Successfully Connected")
    except ConnectionError as e:
        print("No Database Connection")

    ports = list_ports.comports(include_links=True)
    print("available ports: ", [port.name for port in ports])

    with serial.Serial("/dev/ttyUSB0") as ser:
        gen = read_streaming_data(ser)
        while True:
            raw_data = next(gen)
            preprocessed_data = preprocess_data(raw_data)
            print(preprocessed_data)
            client.write_points([preprocessed_data])
