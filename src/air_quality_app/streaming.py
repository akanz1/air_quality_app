import sys
from datetime import datetime

import pytz
import serial
from influxdb import InfluxDBClient
from serial.tools import list_ports

DB_NAME = "air_quality_db"
TIMEZONE = pytz.timezone("Europe/Berlin")

SHORT_TERM_RETENTION = "short_term_retention"
SHORT_TERM_RETENTION_DURATION = "4w"
HISTORY_RETENTION = "history_15m"
HISTORY_CONTINUOUS_QUERY = "cq_air_quality_15m"


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

    timestamp = datetime.now(tz=TIMEZONE)

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
    else:
        print("Database already exists")
    client.switch_database(dbname)
    ensure_retention_policies(client, dbname)
    ensure_continuous_queries(client, dbname)


def ensure_retention_policies(client: InfluxDBClient, dbname: str) -> None:
    policies = {policy["name"] for policy in client.get_list_retention_policies(dbname)}
    if SHORT_TERM_RETENTION not in policies:
        client.create_retention_policy(
            name=SHORT_TERM_RETENTION,
            duration=SHORT_TERM_RETENTION_DURATION,
            default=True,
            replication=1,
            database=dbname,
        )
    else:
        client.query(
            f'ALTER RETENTION POLICY "{SHORT_TERM_RETENTION}" ON "{dbname}" '
            f"DURATION {SHORT_TERM_RETENTION_DURATION} DEFAULT"
        )

    if HISTORY_RETENTION not in policies:
        client.query(
            f'CREATE RETENTION POLICY "{HISTORY_RETENTION}" ON "{dbname}" '
            "DURATION INF REPLICATION 1 SHARD DURATION 52w"
        )


def ensure_continuous_queries(client: InfluxDBClient, dbname: str) -> None:
    existing_queries = {
        query["name"] for query in client.query("SHOW CONTINUOUS QUERIES").get_points()
    }
    if HISTORY_CONTINUOUS_QUERY in existing_queries:
        return

    client.query(
        f"CREATE CONTINUOUS QUERY {HISTORY_CONTINUOUS_QUERY} ON {dbname} "
        "RESAMPLE EVERY 15m FOR 30m "
        "BEGIN "
        'SELECT mean("CO2_ppm") AS "CO2_ppm", '
        'mean("CH20_ugm3") AS "CH20_ugm3", '
        'mean("TVOC_ugm3") AS "TVOC_ugm3", '
        'mean("PM2.5") AS "PM2.5", '
        'mean("PM10") AS "PM10", '
        'mean("Temperature") AS "Temperature", '
        'mean("Humidity") AS "Humidity" '
        f'INTO "{HISTORY_RETENTION}"."air_quality" '
        f'FROM "{SHORT_TERM_RETENTION}"."air_quality" '
        "GROUP BY time(15m) "
        "END"
    )


if __name__ == "__main__":
    try:
        client = InfluxDBClient(
            host="influxdb",
            port=8086,
            username="influxdb",
            password="influxdb",
            database=DB_NAME,
        )
        print(client.ping())
        connect_db(client, DB_NAME)
        print("Successfully Connected")
    except ConnectionError as e:
        print(f"No Database Connection: {e}")
        raise Exception from e

    ports = list_ports.comports(include_links=True)
    print("available ports: ", [port.name for port in ports])

    with serial.Serial("/dev/ttyUSB0") as ser:
        gen = read_streaming_data(ser)
        while True:
            raw_data = next(gen)
            preprocessed_data = preprocess_data(raw_data)

            print(f"Storing to '{SHORT_TERM_RETENTION}'")
            client.write_points(
                [preprocessed_data],
                retention_policy=SHORT_TERM_RETENTION,
            )
