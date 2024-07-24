import sys
from datetime import datetime, timedelta

import pytz
import serial
from influxdb import InfluxDBClient
from serial.tools import list_ports


def read_streaming_data(serial_object: serial.Serial):
    while True:
        lst = []

        for i in range(17):
            if i in [1, 16]:
                x = ord(serial_object.read())
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

    CO2_ppm = lst[2] << 8 | lst[3]
    CH20 = lst[4] << 8 | lst[5]
    TVOC_ugm3 = lst[6] << 8 | lst[7]
    PM25 = lst[8] << 8 | lst[9] - 10  # adjustment to correct for bias
    PM10 = lst[10] << 8 | lst[11] - 10  # adjustment to correct for bias
    temperature = lst[12] + lst[13] / 10 - 1.0  # adjustment to correct for bias
    humidity = lst[14] + lst[15] / 10

    timestamp = datetime.now(tz=pytz.timezone("Europe/Berlin"))

    checksum = (sum(lst) - lst[-1] - 256) == lst[-1]
    values = [CO2_ppm, CH20, TVOC_ugm3, PM25, PM10, temperature, humidity, checksum]

    data_dict = dict(zip(keys, values))
    return {"measurement": "air_quality", "time": timestamp, "fields": data_dict}


def db_exists(client: InfluxDBClient, dbname: str) -> bool:
    """Returns True if the database exists."""
    dbs = client.get_list_database()
    return any(db["name"] == dbname for db in dbs)


def connect_db(client: InfluxDBClient, dbname: str) -> None:
    """Connect to the database, and create it if it does not exist."""
    print("connecting to database...")
    if not db_exists(client, dbname):
        print(f"Creating database {dbname}")
        client.create_database(dbname)
        client.create_retention_policy(
            name="short_term_retention", duration="2w", default=True, replication=1
        )
        client.create_retention_policy(
            name="long_term_retention", duration="52w", default=True, replication=1
        )
    else:
        print("Database already exists")
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
        print(f"No Database Connection: {e}")
        raise Exception from e

    ports = list_ports.comports(include_links=True)
    print("available ports: ", [port.name for port in ports])

    last_temp_write = datetime.now(tz=pytz.timezone("Europe/Berlin")) - timedelta(seconds=30)
    with serial.Serial("/dev/ttyUSB0") as ser:
        gen = read_streaming_data(ser)
        while True:
            raw_data = next(gen)
            preprocessed_data = preprocess_data(raw_data)
            
            current_time = datetime.now(tz=pytz.timezone("Europe/Berlin"))
            if (current_time - last_temp_write).total_seconds() >= 60:
                print("Storing to 'long_term_retention'")
                downsampled_data = preprocess_data(raw_data)
                client.write_points(
                    [downsampled_data],
                    retention_policy="long_term_retention",
                )
                last_temp_write = current_time
            print("Storing to 'short_term_retention'")
            client.write_points(
                [preprocessed_data],
                retention_policy="short_term_retention",
            )