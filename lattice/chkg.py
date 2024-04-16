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

# CHKG algorithm
def CHKG(m, n, degree, G):

    start = time.time()

    # multiplying two matrices
    sk = random_special_column(degree) # vector
    pk = G_mul(G, sk) # vector
    
    # reducing by mod x**d - 1
    for ii in range (len(pk)):
        foo, pk[ii] = div(pk[ii], modulus_poly)
    
    end = time.time()

    return pk, sk, (end - start)