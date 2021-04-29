import sys
from datetime import datetime

import serial
from influxdb import InfluxDBClient


def read_streaming_data(serial_object: serial.Serial):
    while True:
        lst = []
        lst.append(datetime.now().strftime("%Y%m%d_%H%M%S%f"))

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
    # lst = [int(element) for element in lst]
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
    entry = {timestamp: data_dict}
    return entry


if __name__ == "__main__":
    client = InfluxDBClient(
        host="localhost", port=8086, username="influxdb", password="influxdb"
    )

    # client.create_database("air_quality_table")
    # client.switch_database("air_quality_table")
    from serial.tools import list_ports

    ports = list_ports.comports(include_links=True)
    print("available ports: ", ports)
    print([port.name for port in ports])

    with serial.Serial("dev/tty0/") as ser:
        gen = read_streaming_data(ser)
        while True:
            x = next(gen)
            print(x)
            y = preprocess_data(x)
            print(y)
