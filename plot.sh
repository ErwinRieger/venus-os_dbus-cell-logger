#!/usr/bin/env bash

datafile="cell-logger.dat"
host="ess"
if [ -n "$1" ]; then
    if [ -e "$1" ]; then
        datafile="$1"
    else
        echo "note: using $1 as a hostname"
        host="$1"
    fi
fi

# 7200 minutes are 5 days
if [ "$1" != "$datafile" ]; then
    ssh root@${host} 'cat $(ls -rt /data/db/cell-logger.dat*)|tail -7200' | python3 fixdata.py > cell-logger.dat
fi

# Get local timezone offset in seconds
tzoffset="$(date +%z|cut -c1,3)"    # +0200 -> +2
echo "tzoffset: 3600*${tzoffset}"

gnuplot -e "datafile='"${datafile}"'" -e "tzoffset=3600*${tzoffset}" plot-cell-data.gnuplot

