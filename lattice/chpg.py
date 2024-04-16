import numpy as np
import os
import sys
import secrets
import scipy as sp
import math
import time
from sympy.discrete import convolutions
from sympy.polys import *
from sympy import GF
from scipy.signal import fftconvolve
from sympy import pprint
from sympy.abc import x,y,z
# from __future__ import print_function, division
# from sympy.core.compatibility import range
from sympy.ntheory import nextprime
from Crypto.Util import number
from Crypto.Hash import SHA256

import pickle

from helper import *

# CHPG algorithm
def CHPG(m, n, degree):
    
    start = time.time()

    entire_list = []
    for i in range (n):
        this_row = []
        for j in range (m + 1):
            if j == i:
                # Identity matrix diagonal
                this_row.append(one_poly)
            elif j < N:
                # Identity matrix
                this_row.append(zero_poly)
            else:
                # G'
                this_row.append(random_poly(degree))
        entire_list.append(this_row)
    G = np.asarray(entire_list) # the matrix [I||G']
    # print(G)

    end = time.time()

    return G, (end - start)
