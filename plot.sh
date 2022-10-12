#!/usr/bin/env bash

host="ess"
if [ -n "$1" ]; then
    host="$1"
fi

ssh root@${host} "cat /data/db/cell-logger.dat" | python3 fixdata.py > cell-logger.dat

# Get local timezone offset in seconds
tzoffset="$(date +%z|cut -c1,3)"    # +0200 -> +2
echo "tzoffset: 3600*${tzoffset}"

gnuplot -e "datafile='cell-logger.dat'" -e "tzoffset=3600*${tzoffset}" plot-cell-data.gnuplot

