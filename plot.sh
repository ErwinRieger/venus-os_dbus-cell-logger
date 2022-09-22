
cp cell-logger.dat.1 cell-logger.dat; ssh root@ess "cat /data/db/cell*" >> cell-logger.dat
gnuplot plot-cell-data.gnuplot
