
set yrange [3.2:3.8]
set grid
set grid mytics
set mytics 5

set xdata time
set timefmt "%s"
set format x "%H:%M" 

# stats datafile using 6 prefix "A"
# stats datafile using 5 prefix "B"

# plot datafile using 4:5 with linespoints title "flowrate stepper", \
    # datafile using 4:($5/B_mean) with linespoints title "stepper norm", \
    # datafile using 4:6 with linespoints title "flowrate sensor", \
    # datafile using 4:($6/A_mean) with linespoints title "sensor norm", \
    # A_mean title "Mean Sensor"

# plot "cell-logger.dat" using 1:($2/15) with lines title "voltage" linecolor "grey" lw 4, 
plot "cell-logger.dat" using 1:($3/1500+3.7) with lines title "current" linecolor "grey" lw 2, \
     "cell-logger.dat" using 1:4 with lines title "cell1" lt 1 linecolor 1, \
     "cell-logger.dat" using 1:5 with lines title "cell2" lt 2 linecolor 2, \
     "cell-logger.dat" using 1:6 with lines title "cell3" lt 3 linecolor 3, \
     "cell-logger.dat" using 1:7 with lines title "cell4" lt 4 linecolor 4, \
     "cell-logger.dat" using 1:8 with lines title "cell5" lt 5 linecolor 5, \
     "cell-logger.dat" using 1:9 with lines title "cell6" lt 6 linecolor 6, \
     "cell-logger.dat" using 1:10 with lines title "cell7" lt 7 linecolor 7, \
     "cell-logger.dat" using 1:11 with lines title "cell8" lt 8 linecolor 8, \
     "cell-logger.dat" using 1:12 with lines title "cell9" lt 9 linecolor 9, \
     "cell-logger.dat" using 1:13 with lines title "cell10" lt 10 linecolor 10, \
     "cell-logger.dat" using 1:14 with lines title "cell11" lt 11 linecolor 11, \
     "cell-logger.dat" using 1:15 with lines title "cell12" lt 12 linecolor 12, \
     "cell-logger.dat" using 1:16 with lines title "cell13" lt 13 linecolor 13, \
     "cell-logger.dat" using 1:17 with lines title "cell14" lt 14 linecolor 14, \
     "cell-logger.dat" using 1:18 with lines title "cell15" lt 15 linecolor 15, \
     "cell-logger.dat" using 1:19 with lines title "cell16" lt 16 linecolor 16, \
     3.7


# A_min title "  Min", A_max title "  Max"
# , datafile using 4:6 with linespoints smooth bezier, 
# , 1 title datafile 


pause mouse close


