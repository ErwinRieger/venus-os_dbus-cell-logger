#
# Handle gaps in cell-logger data, output NaN values if the gap between
# two datasets is greater than 120 seconds.
#
import sys, collections, math

data = []
avgdata = collections.defaultdict(list)

for line in sys.stdin.readlines():

    tok = line.split()

    try:
        ts = int(tok[0])
    except ValueError:
        sys.stderr.write("Warning, can't parse timestamp, line is: '%s'\n" % line.strip())
        # sys.stdout.write("NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN\n")
        continue

    values = []
    for cell in range(16):

        t = tok[3+cell]

        if 1: # try:
            v = float(t)
        # except ValueError:
            # v = None

        if not math.isnan(v):
            avgdata[cell].append(v)

        values.append(v)
        cell += 1

    assert(not math.isnan(ts))
    data.append((ts, tok[1], tok[2], values))

averages = {}
lastvalues = {}
for i in range(16):

    avg = sum(avgdata[i]) / len(avgdata[i])
    # print("avg %d: %f" % (i, avg))
    averages[i] = avg
    lastvalues[i] = avg

lastts = None
a = collections.defaultdict(list)
for (ts, u, i, values) in data:

    if lastts and ts-lastts > 120:
        # print("gap:", lastts, ts, ts-lastts)
        # sys.stdout.write("NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN\n")
        for cell in range(16):
            lastvalues[cell] = averages[cell]

    sys.stdout.write(f"{ts} {u} {i} ")

    hasspike = False
    for cell in range(16):
        lastval = lastvalues[cell]
        v = values[cell]

        if math.isnan(v):
            dy = abs(averages[cell] - lastval)
        else:
            dy = abs(v - lastval)

        # dx = 60
        # a = dy / dx
        # print("steigung:", dy, dy)

        if dy > 0.5:
            # print(f"spike? {lastval} {v} {dy}")
            hasspike = True
            sys.stdout.write(f"nan ")
        else:
            sys.stdout.write(f"{v} ")


        a[cell].append(abs(dy))

    if hasspike:
        # print(f"spike? {lastval} {v} {dy}")
        sys.stdout.write(" 3.5")
    else:
        sys.stdout.write(" 0")

    sys.stdout.write("\n")

    lastts = ts

# for cell in range(16):
    # print(cell, min(a[cell]), max(a[cell]))

