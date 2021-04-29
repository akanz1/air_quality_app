#!/bin/sh

echo "Waiting for InfluxDB to start..."

while ! nc -z influxdb 8086; do sleep 0.1
done

echo "InfluxDB started"

exec "$@"