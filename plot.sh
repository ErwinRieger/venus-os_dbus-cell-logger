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

ndays="5"
if [ -n "$2" ]; then
    ndays="$2"
fi

# 1440 minutes is 1 day
if [ "$1" != "$datafile" ]; then
    ssh root@${host} 'cat $(ls -rt /data/db/cell-logger.dat*)'"|tail -$((ndays*1440))" | python3 fixdata.py cell-logger.dat
fi

# Get local timezone offset in seconds
tzoffset="$(date +%z|cut -c1,3)"    # +0200 -> +2
echo "tzoffset: 3600*${tzoffset}"

gnuplot -e "datafile='"${datafile}"'" -e "tzoffset=3600*${tzoffset}" plot-cell-data.gnuplot

