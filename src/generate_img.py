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

files = (("data/avg_dist.csv", [0, 15]),
         ("data/avg_moves.csv", [0, 10]),
         ("data/wl_var.csv", [0, 100]),
         ("data/wl.csv", [0, 105]))

for (f, limit) in files:
    fin = open(f)
    values = []
    for x in fin.readlines():
        if x is not "NaN":
            values.append(float(x))
        else:
            values.append(0.0)
    fig = matplotlib.pyplot.figure(figsize=(8.0, 5.0))
    fig.add_subplot(111).plot(values, label = f)
    fig.add_subplot(111).set_ylim(limit)
    fig.savefig("{0}.png".format("img"+f[4:-3]+"png"))