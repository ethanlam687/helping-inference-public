import csv
import numpy as np

chainNum = 10000
with open('grid_prag.csv', 'w') as csv_file :
    writer = csv.writer(csv_file, delimiter=',')
    for literal_beta in np.arange(0, 50, 0.5):
        for pragmatic_beta in np.arange(0, 50, 0.5):
            if(literal_beta == 0 or pragmatic_beta == 0):
                # dont save these
                continue
            writer.writerow([literal_beta,pragmatic_beta, chainNum])
            chainNum = chainNum + 1