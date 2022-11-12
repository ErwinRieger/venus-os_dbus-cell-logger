#
# Handle gaps in cell-logger data, output NaN values if the gap between
# two datasets is greater than 120 seconds.
#
# lineformat: <timestamp> <voltage> <current> 16*<cellvoltage> <spikeflag> <cellsaverage> ---> 21 values
#
import sys, collections, math, pprint, time

def printerr(*args, **kwargs):
    return sys.stderr.write(*args, **kwargs) + sys.stderr.write("\n")


data = []
avgdata = collections.defaultdict(list)

for line in sys.stdin.readlines():

    tok = line.split()

    try:
        ts = int(tok[0])
    except ValueError:
        sys.stderr.write("Warning, can't parse timestamp, line is: '%s'\n" % line.strip())
        continue

    assert(not math.isnan(ts))

    values = []
    foundValue = False
    for cell in range(16):

        t = tok[3+cell]
        v = float(t)

        if not math.isnan(v):
            avgdata[cell].append(v)
            foundValue = True

        values.append(v)

    if not foundValue:
        # Empty line, no values given
        continue

    data.append((ts, tok[1], tok[2], values))

cellaverages = {}
for cell in range(16):

    cellavg = sum(avgdata[cell]) / len(avgdata[cell])
    printerr("cellavg %d: %f" % (cell, cellavg))
    cellaverages[cell] = cellavg

lastvalues = {}
for cell in range(16):
    # lastvalues[cell] = data[0][3][cell]
    lastvalues[cell] = cellaverages[cell]

printerr("")
lastts = None
ranges = []
timerange = []
ranges.append(timerange)
# for (ts, u, i, values, _) in data:
for i in range(len(data)):

    (ts, u, i, values) = data[i]

    if not lastts:
        timerange.append((ts, u, i, values))
        lastts = ts
        continue

    if ts <= lastts:
        printerr(f"order error: {lastts} {ts}")
        assert(0)

    dt = ts-lastts
    if ts-lastts > 120:
        printerr(f"gap from {lastts} to {ts}, delta: {dt}")
        assert(dt < 2*24*3600)
        timerange = []
        ranges.append(timerange)
        lastts = None
        continue

    timerange.append((ts, u, i, values))
    lastts = ts


printerr(f"# of time ranges: {len(ranges)}")
# sys.exit(0)

printerr("")
lastts = None
# datadict = {}

for timerange in ranges:

  filtereddata = []
  lastvalues = timerange[0][3]

  for di in range(len(timerange)):

    (ts, u, i, values) = timerange[di]

    nextData = None
    if di <  len(timerange)-1:
        nextData = timerange[di+1]

    sys.stdout.write(f"{ts} {u} {i} ")

    hasspike = False
    hasnan = False
    cellsavg = []

    for cell in range(16):

        v = values[cell]

        if math.isnan(v):
            hasnan = True
            sys.stdout.write(f"nan ")
            continue

        lastval = lastvalues[cell]
        dy = abs(v - lastval)

        if lastts and (dy / (ts - lastts)) > 0.01: # 0.25:

            if nextData:
                (nextTs, _, _, nextValues) = nextData
                v2 = nextValues[cell]
                assert(not math.isnan(v2))
                dy2 = abs(v2 - v)
                if (dy2 / (nextTs - ts)) > 0.01:
                    sys.stderr.write(f"spike at {ts}, cell: {cell}, lastval: {lastval}, newval: {v}, delta: {dy}\n")
                    hasspike = True
                    # sys.stdout.write(f"nan ")
                    sys.stdout.write(f"{v} ")
                else:
                    assert(0)

            else:

                # possible spike at end of range, ignore this value
                assert(0)
                sys.stderr.write(f"spike at {ts}, cell: {cell}, lastval: {lastval}, newval: {v}, delta: {dy}\n")
                hasspike = True
                sys.stdout.write(f"nan ")

            # sys.stderr.write(f"spike at {ts}, cell: {cell}, lastval: {lastval}, newval: {v}, delta: {dy}\n")
            # hasspike = True
            # sys.stdout.write(f"nan ")
        else:
            sys.stdout.write(f"{v} ")
            lastvalues[cell] = v
            cellsavg.append(v)

    if not cellsavg:
        printerr(f"no data: {ts}, {values}")
        assert(0)

    cellsavg = sum(cellsavg) / len(cellsavg)
    # printerr("cellsavg: %s" % cellsavg)

    if hasspike:
        # print(f"spike? {lastval} {v} {dy}")
        sys.stdout.write(" 3.5")
    else:
        sys.stdout.write(" 3.0")

    if not hasnan and not hasspike:
        data = (ts, u, i, values, cellsavg)
        filtereddata.append(data)
        # datadict[ts] = data

    sys.stdout.write(f" {cellsavg}")
    sys.stdout.write("\n")

    lastts = ts

  sys.stdout.write((21 * "nan ") + "\n") # split graphs in gnuplot

sys.exit(0)

# bereich der höchsten ladung
maxcvoltages = max(filtereddata, key=lambda d: max(d[3]))
mints = maxcvoltages[0]
maxvalues = maxcvoltages[3]
maxcellsavg = maxcvoltages[4]
sys.stderr.write(f"\nmax cellvoltage at {time.ctime(maxcvoltages[0])}, avg {maxcvoltages[4]}\n")
sys.stderr.write(f"cells max: {maxcvoltages[3]}\n")

# bereich der tiefsten entladung
mincvoltages = min(filtereddata, key=lambda d: min(d[3]))
mints = mincvoltages[0]
minvalues = mincvoltages[3]
mincellsavg = mincvoltages[4]
sys.stderr.write(f"\nmin cellvoltage at {time.ctime(mincvoltages[0])}, avg {mincvoltages[4]}\n")
sys.stderr.write(f"cells min: {mincvoltages[3]}\n")

# print("\n")

assert(filtereddata.count(maxcvoltages) == 1)
assert(filtereddata.count(mincvoltages) == 1)

maxindex = filtereddata.index(maxcvoltages)
minindex = filtereddata.index(mincvoltages)

startindex = minindex
endindex = maxindex
if startindex > endindex:
    startindex = maxindex
    endindex = minindex

printerr("")

leaders = []
low = []
good = []
weak = []
for cell in range(16):
    vcellcharge = maxvalues[cell]
    vcelldischa = minvalues[cell]

    if vcellcharge >= maxcellsavg and vcelldischa >= mincellsavg:
        sys.stderr.write(f"cell {cell+1} above while charging and discharging: {vcellcharge} {vcelldischa}\n")

        # compute area above avg
        a = 0
        for index in range(max(0, startindex - 10), min(len(filtereddata), endindex + 10)):
            (ts, u, i, values, cellsavg) = filtereddata[index]
            a += values[cell] - cellsavg
        leaders.append((cell, a))

    elif vcellcharge <= maxcellsavg and vcelldischa <= mincellsavg:
        sys.stderr.write(f"cell {cell+1} below while charging and discharging: {vcellcharge} {vcelldischa}\n")

        # compute area above avg
        a = 0
        for index in range(max(0, startindex - 10), min(len(filtereddata), endindex + 10)):
            (ts, u, i, values, cellsavg) = filtereddata[index]
            a += values[cell] - cellsavg
        low.append((cell, a))

    elif vcellcharge <= maxcellsavg and vcelldischa >= mincellsavg:
        sys.stderr.write(f"cell {cell+1} changes side while charging and discharging: {vcellcharge} {vcelldischa}\n")

        a = 0
        for index in range(max(0, startindex - 10), min(len(filtereddata), endindex + 10)):
            (ts, u, i, values, cellsavg) = filtereddata[index]
            a += abs(values[cell] - cellsavg)
        good.append((cell, a))

    elif vcellcharge >= maxcellsavg and vcelldischa <= mincellsavg:
        sys.stderr.write(f"cell {cell+1} changes side while charging: {vcellcharge} {vcelldischa}\n")

        a = 0
        for index in range(max(0, startindex - 10), min(len(filtereddata), endindex + 10)):
            (ts, u, i, values, cellsavg) = filtereddata[index]
            a += abs(values[cell] - cellsavg)
        weak.append((cell, a))

    else:
        printerr(f"cell {cell+1} max cell voltage {vcellcharge} max cell average {maxcellsavg}, min cell voltage: {vcelldischa} min cell average {mincellsavg}")
        assert(0)


# output data around min and max cell-average into its own datafile
f=open("cellanalyze.dat", "w")

for index in range(max(0, startindex - 30), min(len(filtereddata), endindex + 30)):

    (ts, u, i, values, cellsavg) = filtereddata[index]

    f.write(f"{ts} {u} {i} ")
    for cell in range(16):
        f.write(f"{values[cell]} ")
    if index == startindex:
        f.write(f" 3.5 ")
    elif index == endindex:
        f.write(f" 3.5 ")
    else:
        f.write(f" 0")
    f.write(f" {cellsavg}")
    f.write(f"\n")

printerr("");
printerr("***** Leading cells (cell-voltage always above the others): *****")
leaders.sort(key=lambda x: x[1])
for (cell, area) in leaders:
    printerr(f"  Cell {cell+1}: {area}")
good.sort(key=lambda x: x[1])
printerr("***** Good cells (cell-voltage low while charging and cell is strong while discharging): *****")
printerr("***** Cells with smaller area values are closer to the average *****")
for (cell, area) in good:
    printerr(f"  Cell {cell+1}: {area}")
printerr("***** LOW charge cells (cell with good capacity but low charging state, voltage always below the others): *****")
printerr("***** Cells with smaller area values are closer to the average *****")
low.sort(key=lambda x: abs(x[1]))
for (cell, area) in low:
    printerr(f"  Cell {cell+1}: {area}")
printerr("***** Weak cells (cell voltage high when charging and cellvoltage low when discharging, cell has lower capacity than the others): *****")
printerr("***** Cells with smaller area values are closer to the average *****")
weak.sort(key=lambda x: x[1])
for (cell, area) in weak:
    printerr(f"  Cell {cell+1}: {area}")












