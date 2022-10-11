#
# Handle gaps in cell-logger data, output NaN values if the gap between
# two datasets is greater than 120 seconds.
#
import sys

lastts = None

for line in sys.stdin.readlines():

    tok = line.split()
    ts = int(tok[0])

    if lastts and ts-lastts > 120:
        # print("gap:", lastts, ts, ts-lastts)
        sys.stdout.write("NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN\n")

    lastts = ts
    sys.stdout.write(line)

