#!/bin/bash
#

. /opt/victronenergy/serial-starter/run-service.sh

app="python3 /opt/victronenergy/dbus-cell-logger/dbus-cell-logger.py"
start 
