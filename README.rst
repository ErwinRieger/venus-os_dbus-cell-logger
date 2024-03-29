
dbus-cell-logger
==================

A simple venus-os service to log battery cell voltages in a CSV (-like) format.

Cell voltages are read from "com.victronenergy.battery" service (the first one found).

The number of cells logged is 16 (hardcoded value).

Log interval
++++++++++++++

Log-interval is 60 seconds, every minute a entry is written to the log file (hardcoded value).

Logfile location
+++++++++++++++++

The log file is stored in "/data/db/cell-logger.dat" (hardcoded value). Use "scp" to copy this file
to your workstation for evaluation.

Logfile format
++++++++++++++

The file format is simple, the fields are separated by a blank. Voltages are in [volt] and current is in [ampere], positive current
means battery is charging, negative current means discharging.

::

   <unix-timestamp> <battery-voltage> <battery-current> <cell-voltage1> ... <cell-voltage16>

For example:

::

   ...
   1664070073 52.700000 -5.790000 3.305000 3.307000 3.305000 3.304000 3.304000 3.305000 3.305000 3.307000 3.286000 3.286000 3.282000 3.285000 3.288000 3.291000 3.290000 3.285000 
   1664070133 52.700000 -4.910000 3.305000 3.307000 3.305000 3.304000 3.305000 3.305000 3.305000 3.306000 3.286000 3.286000 3.283000 3.285000 3.288000 3.290000 3.290000 3.285000 
   1664070193 52.700000 -4.800000 3.305000 3.307000 3.305000 3.304000 3.305000 3.305000 3.305000 3.306000 3.287000 3.286000 3.283000 3.285000 3.289000 3.291000 3.291000 3.285000 
   ...


Gnuplot script
++++++++++++++

See plot.sh and plot-cell-data.gnuplot for a example how to copy the logfile from your venus-os box and
to plot the data using gnuplot.

Example log
++++++++++++++

The file "cell-logger.dat.example" contains some example data.

To plot it using gnuplot, use something like this:

.. code-block:: sh

   cp cell-logger.dat.example cell-logger.dat
   gnuplot -e "tzoffset=7200" plot-cell-data.gnuplo

Example plots: 

.. image:: images/example-plot1
   :width: 250
   :target: images/example-plot1

.. image:: images/example-plot1-zoomed
   :width: 250
   :target: images/example-plot1-zoomed


Example gnuplot plot
++++++++++++++++++++++

.. image:: images/example-plot2
   :width: 250
   :target: images/example-plot2


Planned extensions
++++++++++++++++++++++

* Create a config-section at the beginning of "dbus-cell-logger.py" to allow modification of some constants (log-interval, log file path...).

