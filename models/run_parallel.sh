# parallel --bar --colsep ',' "sh ./run_parallel.sh {1} {2} {3}" :::: grid_prag.csv
python grid_search.py $1 $2 $3