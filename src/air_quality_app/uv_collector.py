import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

import pytz
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError

from air_quality_app.streaming import connect_db
from air_quality_app.streaming import DB_NAME
from air_quality_app.streaming import SHORT_TERM_RETENTION

TIMEZONE = pytz.timezone("Europe/Berlin")
MEASUREMENT = "uv_sensor"
HOST = "0.0.0.0"
PORT = int(os.getenv("UV_COLLECTOR_PORT", "8088"))
TOKEN = os.getenv("UV_COLLECTOR_TOKEN", "")

FIELD_TYPES = {
    "uva_uw_cm2": float,
    "uvb_uw_cm2": float,
    "uvc_uw_cm2": float,
    "uvi": float,
    "uvi_ema": float,
    "uvi_1m": float,
    "uvi_3m": float,
    "uvi_5m": float,
    "uvi_max": float,
    "uvi_1m_max": float,
    "sed_per_h": float,
    "sed_total": float,
    "uva_dose_h": float,
    "uvb_dose_h": float,
}


def influx_client() -> InfluxDBClient:
    client = InfluxDBClient(
        host=os.getenv("INFLUXDB_HOST", "influxdb"),
        port=int(os.getenv("INFLUXDB_PORT", "8086")),
        username=os.getenv("INFLUXDB_USER", "influxdb"),
        password=os.getenv("INFLUXDB_PASSWORD", "influxdb"),
        database=DB_NAME,
    )
    connect_db(client, DB_NAME)
    return client


def parse_fields(payload: dict) -> dict:
    fields = {}
    for key, caster in FIELD_TYPES.items():
        if key in payload:
            fields[key] = caster(payload[key])
    return fields


class UVHandler(BaseHTTPRequestHandler):
    client = None

    def do_GET(self):
        if self.path != "/health":
            self.send_error(404)
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok\n")

    def do_POST(self):
        if self.path != "/uv":
            self.send_error(404)
            return
        if TOKEN and self.headers.get("X-UV-Token") != TOKEN:
            self.send_error(401)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            fields = parse_fields(payload)
        except (TypeError, ValueError, json.JSONDecodeError):
            self.send_error(400, "invalid JSON payload")
            return

        if not fields:
            self.send_error(400, "no recognized fields")
            return

        point = {
            "measurement": MEASUREMENT,
            "time": datetime.now(tz=TIMEZONE),
            "tags": {"device": str(payload.get("device", "lilygo_uv"))},
            "fields": fields,
        }

        try:
            self.client.write_points([point], retention_policy=SHORT_TERM_RETENTION)
        except InfluxDBServerError as exc:
            self.send_error(503, f"influx write failed: {exc}")
            return

        self.send_response(204)
        self.end_headers()

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args), flush=True)


if __name__ == "__main__":
    UVHandler.client = influx_client()
    print(f"UV collector listening on {HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), UVHandler).serve_forever()
