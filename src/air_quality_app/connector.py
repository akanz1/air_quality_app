import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
import serial
from serial.tools import list_ports

from air_quality_app.utils import export_dir

ports = list_ports.comports(include_links=True)
print("available ports: ", ports)
print(ports[0].name)
print(20 * "-")
iterations = 3600

with serial.Serial("COM3") as ser:
    data = pd.DataFrame(columns=np.arange(18))
    for i in range(iterations):
        lst = []
        lst.append(datetime.now().strftime("%Y%m%d_%H%M%S%f"))

        for j in range(17):
            if j in [1, 16]:
                x = ord(ser.read())
                lst.append(x)
            else:
                x = int.from_bytes(ser.read(), byteorder=sys.byteorder)
                lst.append(x)

        if i % 5 == 0:
            print(f"Iteration {i} / {iterations}: {lst}")
        a_series = pd.Series(lst, index=data.columns)
        data = data.append(a_series, ignore_index=True)

    time = datetime.now().strftime("%Y%m%d_%H%M%S")

    data.to_csv(f"{export_dir}/{time}_initial_data.csv", index=False)
    print(f"Done! -- {time}_initial_data.csv")
