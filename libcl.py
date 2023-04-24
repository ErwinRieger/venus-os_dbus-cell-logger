import sys, collections, math, pprint, time
import argparse

def printerr(*args, **kwargs):
    return sys.stderr.write(*args, **kwargs) + sys.stderr.write("\n")


class CellDatum(argparse.Namespace):

    def __init__(self, **kwargs):

        argparse.Namespace.__init__(self, **kwargs)

        self.cellsavg = None

    def cellsAvg(self):

        if self.cellsavg != None:
            return self.cellsavg

        self.cellsavg = sum(self.values) / len(self.values)
        # printerr("cellsavg: %s" % self.cellsavg)
        return self.cellsavg

    def deviation(self):
        return max(self.values) - min(self.values)


class DataRange:

    # init from pairs: 
    #   mode = "left": use data from left datum
    #   mode = "right": use data from right datum
    #   mode = "avg": use data from both datums and build average
    def __init__(self, d=None, pairs=None, mode=None):

        if d != None:
            self.data = d
        else:
            self.data = []

            if pairs:
                if mode == "left":
                    self.data = list(map(lambda p: p.left, pairs))
                else:
                    assert(0)

    def len(self):
        return len(self.data)

    def append(self, cd):
        self.data.append(cd)

    def filter(self, func):
        return DataRange(list(filter(func, self.data)))

    # returned range is one datum shorter than ours
    def dataPairs(self, step=1):

        pairs = []
        for i in range(len(self.data) - step):
            pairs.append(argparse.Namespace(left = self.data[i], right = self.data[i+step]))

        return pairs

    def filterPairs(self, pairs, func):

        return list(filter(func, pairs))

    def ravg(self, index, navg, attname, subindex=None):

        l = []
        for i in range(navg):

            attr = self.data[index+i].__dict__[attname]

            if subindex != None:
                l.append(attr[subindex])
            else:
                l.append(attr)

        return sum(l) / len(l)

    # returned range is n-1 datum shorter than ours
    def runningAvg(self, navg):

        res = DataRange()
        for i in range(len(self.data) - (navg-1)):

            d = self.data[i]

            values = []
            for ci in range(len(d.values)):
                values.append(self.ravg(i, navg, "values", subindex=ci))

            nd = CellDatum(
                    ts=d.ts,
                    u=self.ravg(i, navg, "u"),
                    i=self.ravg(i, navg, "i"),
                    values=values,
                    )

            res.append(nd)

        return res

class CellLog:

    def __init__(self):
        pass

    def read(self, f):

        self.data = []

        #
        # Read and parse/preprocess data
        #
        for line in f.readlines():

            tok = line.split()

            try:
                ts = int(tok[0])
            except ValueError:
                sys.stderr.write("Warning, can't parse timestamp, line is: '%s'\n" % line.strip())
                continue

            assert(not math.isnan(ts))

            values = []
            for cell in range(16):

                t = tok[3+cell]
                v = float(t)

                if math.isnan(v):
                    # print("skipping NAN line...")
                    break

                values.append(v)

            if len(values) < 16:
                continue # skip NaN lines


            # self.data.append((ts, tok[1], float(tok[2]), values))
            self.data.append(CellDatum(ts=ts, u=float(tok[1]), i=float(tok[2]), values=values))

        print(f"read {len(self.data)} datums")

    def filterTimeRanges(self, data=None, rangeObj=None):

        #
        # Filter ranges (gaps)
        #
        printerr("")
        lastts = None
        timerange = DataRange()
        ranges = [timerange]

        for cd in data or (rangeObj and rangeObj.data) or self.data:

            ts = cd.ts

            if not lastts:
                timerange.append(cd)
                lastts = ts
                continue

            if ts <= lastts:
                printerr(f"order error: {lastts} {ts}")
                assert(0)

            dt = ts-lastts
            if dt > 300: # allow gap up to 5 minutes, reboot for example
                printerr(f"gap from {lastts} to {ts}, delta: {dt}")
                timerange = DataRange()
                ranges.append(timerange)
                lastts = None
                continue

            timerange.append(cd)
            lastts = ts

        printerr(f"# of time ranges: {len(ranges)}")
        # sys.exit(0)

        return ranges

    #
    # Output data
    #
    def dumpGnuplot(self, ranges, ofn):

        printerr("")
        f = open(ofn, "w")

        for timerange in ranges:

            self.dumpGnuplotRange(timerange, f)

    def dumpGnuplotRange(self, timerange, f):

            for cd in timerange.data:

                f.write(f"{cd.ts} {cd.u} {cd.i} ")

                # Write Voltages
                for cell in range(16):
                    v = cd.values[cell]
                    f.write(f"{v} ")

                # Write Average Voltage of all cells
                f.write(f" {cd.cellsAvg()}")
                f.write("\n")

            f.write((21 * "nan ") + "\n") # split graphs in gnuplot




