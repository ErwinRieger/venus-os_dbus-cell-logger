
set yrange [2.8:3.8] # [V]
set ylabel "cell voltage [V]"

set y2range [-125:500] # [A]
set y2label "current [A]"

set grid
set grid mytics
set mytics 5

set y2tics 

set xdata time
set timefmt "%s"
set format x "%d.%H:%M" 

# plot "cell-logger.dat" using ($1 + tzoffset):($2/15) with lines title "voltage" linecolor "grey" lw 4, 
# datafile using ($1 + tzoffset):20 with lines title "spike" linecolor "grey" lw 2, 
plot \
datafile using ($1 + tzoffset):20 with lines title "spike" linecolor "red", \
     datafile using ($1 + tzoffset):21 with lines title "cellsavg" lt 16 linecolor "black", \
     datafile using ($1 + tzoffset):4 with lines title "cell1" lt 1 linecolor 1, \
     datafile using ($1 + tzoffset):5 with lines title "cell2" lt 2 linecolor 2, \
     datafile using ($1 + tzoffset):6 with lines title "cell3" lt 3 linecolor 3, \
     datafile using ($1 + tzoffset):7 with lines title "cell4" lt 4 linecolor 4, \
     datafile using ($1 + tzoffset):8 with lines title "cell5" lt 5 linecolor 5, \
     datafile using ($1 + tzoffset):9 with lines title "cell6" lt 6 linecolor 6, \
     datafile using ($1 + tzoffset):10 with lines title "cell7" lt 7 linecolor 7, \
     datafile using ($1 + tzoffset):11 with lines title "cell8" lt 8 linecolor 8, \
     datafile using ($1 + tzoffset):12 with lines title "cell9" lt 9 linecolor 9, \
     datafile using ($1 + tzoffset):13 with lines title "cell10" lt 10 linecolor 10, \
     datafile using ($1 + tzoffset):14 with lines title "cell11" lt 11 linecolor 11, \
     datafile using ($1 + tzoffset):15 with lines title "cell12" lt 12 linecolor 12, \
     datafile using ($1 + tzoffset):16 with lines title "cell13" lt 13 linecolor 13, \
     datafile using ($1 + tzoffset):17 with lines title "cell14" lt 14 linecolor 14, \
     datafile using ($1 + tzoffset):18 with lines title "cell15" lt 15 linecolor 15, \
     datafile using ($1 + tzoffset):19 with lines title "cell16" lt 16 linecolor 16, \
     datafile using ($1 + tzoffset):3 with lines title "current" linecolor "grey" lw 2 axes x1y2, \
     0 axes x1y2 lc "black" notitle

pause mouse close


