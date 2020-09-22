#!/bin/sh
echo "[config]" > config.ini

if [ -n "$PASSWORD" ]; then
    echo "PASSWORD=$PASSWORD" >> config.ini
else
    echo "please set PASSWORD"
    exit
fi


if [ -n "$ROUTE_IP" ]; then
    echo "ROUTE_IP=$ROUTE_IP" >> config.ini
else
    echo "please set ROUTE_IP"
    exit
fi

if [ -n "$SLEEP_TIME" ]; then
    echo "SLEEP_TIME=$SLEEP_TIME" >> config.ini
else
    echo "SLEEP_TIME=10" >> config.ini
fi

if [ -n "$EXPORTER_PORT" ]; then
    echo "EXPORTER_PORT=$EXPORTER_PORT" >> config.ini
else
    echo "EXPORTER_PORT=8211" >> config.ini
fi

if [ -n "$MAX_RETRIES" ]; then
    echo "MAX_RETRIES=$MAX_RETRIES" >> config.ini
else
    echo "MAX_RETRIES=3" >> config.ini
fi

if [ -n "$TIMEOUT" ]; then
    echo "TIMEOUT=$TIMEOUT" >> config.ini
else
    echo "TIMEOUT=10" >> config.ini
fi

python3 main.py
