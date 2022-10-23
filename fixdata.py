#
# Handle gaps in cell-logger data, output NaN values if the gap between
# two datasets is greater than 120 seconds.
#
import sys, collections, math, pprint, time

def printerr(*args, **kwargs):
    return sys.stderr.write(*args, **kwargs) + sys.stderr.write("\n")


data = []
avgdata = collections.defaultdict(list)

lastvalues = []
nsame = 0
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

    if values == lastvalues:
        nsame += 1
        if nsame > 15:
            # skip "stalled" bms cell values
            continue
    else:
        nsame = 0

    cellsavg = sum(cellsavg) / len(cellsavg)
    # print("cellsavg:", cellsavg)

    assert(not math.isnan(ts))
    data.append((ts, tok[1], tok[2], values, cellsavg))

    lastvalues = values

# averages = {}
lastvalues = {}
for cell in range(16):

    cellavg = sum(avgdata[cell]) / len(avgdata[cell])
    # print("cellavg %d: %f" % (cell, cellavg))
    # averages[cell] = cellavg
    lastvalues[cell] = cellavg

lastts = None
lastavg = None
# a = collections.defaultdict(list)
filtereddata = []
datadict = {}
steep = collections.defaultdict(list)
for (ts, u, i, values, cellsavg) in data:

    if lastts and ts-lastts > 120:
        # print("gap:", lastts, ts, ts-lastts)
        sys.stdout.write("NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN\n")
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

        if lastts:
            sys.stderr.write(f"steigung: {dy / (ts - lastts)}\n")

        if lastts and (dy / (ts - lastts)) > 0.001: # 0.25:
            sys.stderr.write(f"spike {lastval} { math.isnan(v) and cellsavg or v } {dy}\n")
            hasspike = True
            sys.stdout.write(f"nan ")
        else:
            sys.stdout.write(f"{v} ")
            lastvalues[cell] = v

        # a[cell].append(dy)
        if lastts:
            steep[cell].append(dy / (ts-lastts))

    if lastts:
        steep[16].append((cellsavg - lastavg) / (ts-lastts)) # append steepness of cellsaverage

    if hasspike:
        # print(f"spike? {lastval} {v} {dy}")
        sys.stdout.write(" 3.5 xxx")
    else:
        sys.stdout.write(" 0")

    if not hasnan and not hasspike:
        data = (ts, u, i, values, cellsavg)
        filtereddata.append(data)
        datadict[ts] = data

    sys.stdout.write(f" {cellsavg}")
    sys.stdout.write("\n")

    lastts = ts
    lastavg = cellsavg

# for cell in range(16):
    # print(cell, min(a[cell]), max(a[cell]))

for (ts, u, i, values, cellsavg) in filtereddata:

    csteep = steep[16]
    # print(f"cellsaverage max steep: {max(csteep)}")
    # print(f"cellsaverage min steep: {min(csteep)}")

    for cell in range(16):

        csteep = steep[cell]
        # print(f"{cell}: max steep: {max(csteep)}")
        # print(f"{cell}: min steep: {min(csteep)}")

# bereich der höchsten ladung
maxavg = max(filtereddata, key=lambda d: max(d[3]))
mints = maxavg[0]
maxvalues = maxavg[3]
maxcellsavg = maxavg[4]
sys.stderr.write(f"max avg at {time.ctime(maxavg[0])}, avg {maxavg[4]}\n")
sys.stderr.write(f"cells max: {maxavg[3]}\n")

cv = []
for cell in range(16):
    cv.append((cell, maxvalues[cell]))
cv.sort(key=lambda x: x[1])

# for (cell, v) in cv:
    # if v > cellsavg:
        # print(f"cell {cell} above while charging: {v}")
    # else:
        # print(f"cell {cell} below while charging: {v}")

# bereich der tiefsten entladung
minavg = min(filtereddata, key=lambda d: min(d[3]))
mints = minavg[0]
minvalues = minavg[3]
mincellsavg = minavg[4]
sys.stderr.write(f"min avg at {time.ctime(minavg[0])}, avg {minavg[4]}\n")
sys.stderr.write(f"cells min: {minavg[3]}\n")

cv = []
for cell in range(16):
    cv.append((cell, minvalues[cell]))
cv.sort(key=lambda x: x[1])

# print("\n")

assert(filtereddata.count(maxavg) == 1)
assert(filtereddata.count(minavg) == 1)

maxindex = filtereddata.index(maxavg)
minindex = filtereddata.index(minavg)

startindex = minindex
endindex = maxindex
if startindex > endindex:
    startindex = maxindex
    endindex = minindex

# for (cell, v) in cv:
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


f=open("cellanalyze.dat", "w")

# output data around min and max cell-average into its own datafile
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




"""

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

"""








