'''
Created on 29/gen/2013

@author: mpre
'''

import matplotlib
matplotlib.use("GTKAgg")
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('multipage.pdf')

import sys

files = (("avg_dist.csv", [0, 15]),
         ("avg_moves.csv", [0, 10]),
         ("wl_var.csv", [0, 100]),
         ("wl.csv", [0, 105]))

colors = ( (1,0,0),
           (0,1,0),
           (0,0,1))

directories = sys.argv[1:]

dir_num = len(directories)

d_files = []

for x in files:
    d_files += [["{0}/{1}".format(d,x[0]), x[1]] for d in directories]
    
print d_files

for fname in files:
    i = 0
    values = []
    limit = []
    for _ in range(dir_num):
        v_temp = []
        fin, limit = d_files.pop(0)
        for line in open(fin):
            v_temp.append(float(line))
        values.append(v_temp)
    fig = matplotlib.pyplot.figure(figsize=(8.0, 5.0))
    ax = fig.add_subplot(111)
    for v in values:
        ax.plot(v, c=colors[i%len(colors)])
        i += 1
    ax.set_ylim(limit)
    fig.savefig("img/{0}_comparison.png".format(fname[0][:-4]))