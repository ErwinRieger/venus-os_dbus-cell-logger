#!/bin/bash
#

. /opt/victronenergy/serial-starter/run-service.sh

app="python3 /home/root/dbus-pvcontrol/dbus-pvcontrol.py"
start 
