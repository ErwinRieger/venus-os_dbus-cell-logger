#!/usr/bin/env python3

"""
File-format:

    <timestamp> <packvoltage> <current> <cell-voltage1> ... <cell-voltage16>

"""
from gi.repository import GLib
import platform
import logging
import sys
import os, time

from logging.handlers import TimedRotatingFileHandler 

sys.path.insert(1, os.path.join(os.path.dirname(__file__), './ext/velib_python'))
from vedbus import VeDbusService
from dbusmonitor import DbusMonitor
from ve_utils import exit_on_error

servicename='com.victronenergy.cell-logger'

class CellLogger(object):

    def __init__(self, productname='IBR PV CellLogger', connection='CellLogger'):

        logging.debug("Service %s starting... "% servicename)

        dummy = {'code': None, 'whenToLog': 'configChange', 'accessLevel': None}
        register = { '/Dc/0/Voltage': dummy, '/Dc/0/Current': dummy } 
        for i in range(16):
            register["/Voltages/Cell%d" % (i+1)] = dummy
        dbus_tree= {
                'com.victronenergy.battery': register,
                }

        self._dbusmonitor = DbusMonitor(dbus_tree)

	# Get dynamic servicename for serial-battery
        serviceList = self._get_service_having_lowest_instance('com.victronenergy.battery')
        if not serviceList:
            # Restart process
            logging.info("service com.victronenergy.battery not registered yet, exiting...")
            sys.exit(0)
        self.batt_service = serviceList[0]
        logging.info("service of battery: " +  self.batt_service)

        self._dbusservice = VeDbusService(servicename)

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
        self._dbusservice.add_path('/Mgmt/ProcessVersion', 'Unkown version, and running on Python ' + platform.python_version())
        self._dbusservice.add_path('/Mgmt/Connection', connection)

        # Create the mandatory objects
        self._dbusservice.add_path('/DeviceInstance', 1) # deviceinstance)
        self._dbusservice.add_path('/ProductId', 0)
        self._dbusservice.add_path('/ProductName', productname)
        self._dbusservice.add_path('/FirmwareVersion', 0)
        self._dbusservice.add_path('/HardwareVersion', 0)
        self._dbusservice.add_path('/Connected', 1)

        self.dataLogger = logging.getLogger("dbus-cell-logger") 
        self.dataLogger.addHandler(
                TimedRotatingFileHandler('/data/db/cell-logger.dat', when="W0", backupCount=4) 
            )

        GLib.timeout_add(60000, exit_on_error, self.update)

    def update(self):

        v = self._dbusmonitor.get_value(self.batt_service, "/Dc/0/Voltage")
        c = self._dbusmonitor.get_value(self.batt_service, "/Dc/0/Current")

        s = f"{int(time.time())} {self.getValue(v)}{self.getValue(c)}"

        for i in range(16):
            cv = self._dbusmonitor.get_value(self.batt_service, "/Voltages/Cell%d" % (i+1))
            s += f"{self.getValue(cv)}"

        self.dataLogger.warning(s)

        return True

    # Handle None values
    def getValue(self, v):

        if v != None:
            return "%.3f " % v

        return "NaN "

    # returns a tuple (servicename, instance)
    def _get_service_having_lowest_instance(self, classfilter=None): 
        services = self._get_connected_service_list(classfilter=classfilter)
        if len(services) == 0: return None
        s = sorted((value, key) for (key, value) in services.items())
        return (s[0][1], s[0][0])

    def _get_connected_service_list(self, classfilter=None):
        services = self._dbusmonitor.get_service_list(classfilter=classfilter)
        # self._remove_unconnected_services(services)
        return services

# === All code below is to simply run it from the commandline for debugging purposes ===

# It will created a dbus service called com.victronenergy.pvinverter.output.
# To try this on commandline, start this program in one terminal, and try these commands
# from another terminal:
# dbus com.victronenergy.pvinverter.output
# dbus com.victronenergy.pvinverter.output /Ac/Energy/Forward GetValue
# dbus com.victronenergy.pvinverter.output /Ac/Energy/Forward SetValue %20
#
# Above examples use this dbus client: http://code.google.com/p/dbus-tools/wiki/DBusCli
# See their manual to explain the % in %20

def main():

    format = "%(asctime)s %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=logging.DEBUG, format=format, datefmt="%d.%m.%y_%X_%Z")

    from dbus.mainloop.glib import DBusGMainLoop
    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)

    cellLogger = CellLogger( )

    logging.info('Connected to dbus, and switching over to GLib.MainLoop() (= event based)')
    mainloop = GLib.MainLoop()

    mainloop.run()


if __name__ == "__main__":
    main()


