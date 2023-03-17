# visualize rho(r) for various co-latitudes theta
# include the path of the python tools in your environment 
# variable something like
# setenv PYTHONPATH $HOME/Ester/local/lib/python2.7/site-packages/ester

import sys
from ester import *
import matplotlib.pyplot as plt
import numpy as np
import sys

if len(sys.argv) == 1:
    print("Please give a file to plot as 1sr param")
    exit(1)
# the input file is here M5_O95
a=star2d(sys.argv[1])
plt.plot(a.r[:],np.log10(a.rho[:]))
plt.plot(a.r[:],np.log10(a.T[:]))
plt.show()
