#!/bin/bash
#

. /opt/victronenergy/serial-starter/run-service.sh

app="python3 /home/root/dbus-cell-logger/dbus-cell-logger.py"
start 
