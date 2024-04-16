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
from chpg import *
from chkg import *
from chash import *
from chcheck import *
from chadapt import *

# Iteration of tests
ITER = 10

def main():

    all_chpg_time = []
    all_chkg_time = []
    all_chash_time = []
    all_chcheck_time = []
    all_chadapt_time_in = []
    all_chadapt_time_ex = []

    # Test iterations
    for i in range(ITER):
        
        # CHPG
        G, chpg_time = CHPG(M, N, DEGREE)
        all_chpg_time.append(chpg_time)

        # CHKG
        pk, sk, chkg_time = CHKG(M, N, DEGREE, G)
        all_chkg_time.append(chkg_time)

        # CHASH
        msg = "5"
        h, r, chash_time = CHASH(M, N, DEGREE, G, pk, msg)
        all_chash_time.append(chash_time)

        # CHADAPT
        msg_prime = "10"
        r_prime, chcheck_time, chadapt_time = CHADAPT(M, N, DEGREE, G, pk, sk, msg, msg_prime, h, r)
        all_chcheck_time.append(chcheck_time)
        all_chadapt_time_in.append(chadapt_time)
        all_chadapt_time_ex.append(chadapt_time - chcheck_time)

    # Print out test results
    print("========== [Average {0} times] Lattice Version on Chameleon Hash ==========".format(ITER))
    print("chpg time: {0} s".format(sum(all_chpg_time) / ITER))
    print("chkg time: {0} s".format(sum(all_chkg_time) / ITER))
    print("chash time: {0} s".format(sum(all_chash_time) / ITER))
    print("chcheck time: {0} s".format(sum(all_chcheck_time) / ITER))
    print("chadapt time (Include chcheck): {0} s".format(sum(all_chadapt_time_in) / ITER))
    print("chadapt time (Exclude chcheck): {0} s".format(sum(all_chadapt_time_ex) / ITER))


if __name__ == '__main__':
    sys.exit(main())
