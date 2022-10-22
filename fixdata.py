#
# Handle gaps in cell-logger data, output NaN values if the gap between
# two datasets is greater than 120 seconds.
#
import sys, collections, math, pprint

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
    cellsavg = []
    for cell in range(16):

        t = tok[3+cell]
        v = float(t)

        if not math.isnan(v):
            avgdata[cell].append(v)
            cellsavg.append(v)

        values.append(v)
        cell += 1

    if not cellsavg:
        # Empty line, no values given
        continue

    cellsavg = sum(cellsavg) / len(cellsavg)
    # print("cellsavg:", cellsavg)

    assert(not math.isnan(ts))
    data.append((ts, tok[1], tok[2], values, cellsavg))

# averages = {}
lastvalues = {}
for cell in range(16):

    cellavg = sum(avgdata[cell]) / len(avgdata[cell])
    # print("cellavg %d: %f" % (cell, cellavg))
    # averages[cell] = cellavg
    lastvalues[cell] = cellavg

lastts = None
# a = collections.defaultdict(list)
filtereddata = []
for (ts, u, i, values, cellsavg) in data:

    if lastts and ts-lastts > 120:
        # print("gap:", lastts, ts, ts-lastts)
        # sys.stdout.write("NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN\n")
        for cell in range(16):
            lastvalues[cell] = cellsavg

    sys.stdout.write(f"{ts} {u} {i} ")

    hasspike = False
    hasnan = False
    for cell in range(16):
        lastval = lastvalues[cell]
        v = values[cell]

        if math.isnan(v):
            dy = abs(cellsavg - lastval)
            hasnan = True
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

        # a[cell].append(dy)

    if hasspike:
        # print(f"spike? {lastval} {v} {dy}")
        sys.stdout.write(" 3.5 xxx")
    else:
        sys.stdout.write(" 0")

    if not hasnan and not hasspike:
        filtereddata.append((ts, u, i, values, cellsavg))

    sys.stdout.write(f" {cellsavg}")
    sys.stdout.write("\n")

    lastts = ts

# for cell in range(16):
    # print(cell, min(a[cell]), max(a[cell]))


above = collections.defaultdict(float)
below = collections.defaultdict(float)
for (ts, u, i, values, cellsavg) in filtereddata:

    # compute avg of all cells
    sys.stderr.write(f"avg cell voltage: {cellsavg}\n")

    for cell in range(16):
        celldiff = (values[cell] - cellsavg) / cellsavg
        sys.stderr.write(f"cell {cell}, avg diff voltage: {celldiff}\n")

        if celldiff > 0:
            above[cell] += celldiff
        elif celldiff < 0:
            below[cell] += celldiff


sys.stderr.write(f"above:\n")
pprint.pprint(dict(above), sys.stderr)
sys.stderr.write(f"below:\n")
pprint.pprint(dict(below), sys.stderr)



sides= collections.defaultdict(float)
cside= collections.defaultdict(float)
nc = 0
dside= collections.defaultdict(float)
nd = 0
for (ts, u, i, values, cellsavg) in filtereddata:

    # min cell voltage
    mincellvolt = min(values)
    # max cell voltage
    maxcellvolt = max(values)
    voltrange = maxcellvolt - mincellvolt

    sys.stderr.write(f"mincellvolt: {mincellvolt} maxcellvolt: {maxcellvolt} voltrange: {voltrange}\n")

    assert(voltrange >= 0)

    if voltrange > 0.010: # [v] xxx hardcoded

        for cell in range(16):

            celldiff = (values[cell] - cellsavg) * 1000 # [mV]
            if cell==0:
                sys.stderr.write(f"cell {cell} diff: {celldiff}\n")

            # if float(i) > 0 and celldiff > 2 and cellsavg > 3.35: # cell ahead while charging
            if float(i) > 0 and celldiff > 3 : # cell ahead while charging
                sys.stderr.write(f"cell {cell} ahead while charging, voltage: {celldiff}\n")
                # sides[cell+1] += celldiff
                cside[cell+1] += pow(celldiff, 2)
                nc+=1
            # elif float(i) < 0 and celldiff < -2 and cellsavg < 3.30: # cell ahead while discharging
            elif float(i) < 0 and celldiff < -3 : # cell ahead while discharging
                sys.stderr.write(f"cell {cell} ahead while discharging, voltage: {celldiff}\n")
                # sides[cell+1] -= celldiff
                dside[cell+1] += pow(celldiff, 2)
                nd+=1
            else:
                sys.stderr.write(f"ignore cell {cell} i: {i} cellsavg {cellsavg} diff: {celldiff}\n")

            sides[cell+1] += abs(celldiff)

# sys.stderr.write(f"sides:\n")
# pprint.pprint(dict(sides), sys.stderr)

# for cell in cside.keys():
    # sides[cell] += cside[cell] / nc
# for cell in dside.keys():
    # sides[cell] += dside[cell] / nd

sys.stderr.write(f"Cell Quality:\n")
sidelist = []
for cell in range(16):
    sidelist.append((cell+1, sides[cell]))
sidelist.sort(key=lambda x: x[1])
# pprint.pprint(sidelist, sys.stderr)
sum = 0
for (cell, diff) in sidelist:
    sys.stderr.write(f"Cell {cell:2}: diff {diff}\n")
    sum += diff

sys.stderr.write(f"Sum: {sum}\n")

# sys.stderr.write(f"cside:\n")
# pprint.pprint(dict(cside), sys.stderr)
# sys.stderr.write(f"dside:\n")
# pprint.pprint(dict(dside), sys.stderr)









