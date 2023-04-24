#
# Handle gaps in cell-logger data, output NaN values if the gap between
# two datasets is greater than 120 seconds.
#
# lineformat: <timestamp> <voltage> <current> 16*<cellvoltage> <cellsaverage> ---> 21 values
#
import sys, libcl

data = libcl.CellLog()

data.read(sys.stdin)

ranges = data.filterTimeRanges()

data.dumpGnuplot(ranges, sys.argv[1])

