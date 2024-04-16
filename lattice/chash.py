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

def CHASH(m, n, degree, G, pk, msg):

    start = time.time()

    # Sample rho and calculate G dot rho
    rho = random_special_column(degree) # vector
    G_rho = G_mul(G, rho) # vector
    # reducing by mod x**d - 1
    for ii in range(len(G_rho)):
        foo, G_rho[ii] = div(G_rho[ii], modulus_poly)
    # print(G_rho)

    # h
    hash_object = SHA256.new()
    hash_object.update(msg.encode()) # encode as string
    h_m = int(hash_object.hexdigest(), 16)
    h = G_rho + h_m
    # reducing by mod x**d - 1
    for ii in range(len(h)):
        foo, h[ii] = div(h[ii], modulus_poly)

    while True:

        # NIZK Proof
        # ========== Step (1) ==========
        # t2 and z1
        t2 = random_special_S(degree) # vector
        z1 = random_special_S_md2_minus_d(degree) # vector
        # print(z1)

        # T2
        T2 = G_mul(G, t2) # vector
        # reducing by mod x**d - 1
        for ii in range (len(T2)):
            foo, T2[ii] = div(T2[ii], modulus_poly)
        # print(T2)

        # c1
        c1_hash_object = SHA256.new()
        c1_hash_object.update(str(T2).encode())
        c1_hash_object.update(str(pk).encode())
        c1_hash_object.update(str(G_rho).encode())
        c1_hash_object.update(msg.encode()) # encode as string
        c1 = int(c1_hash_object.hexdigest(), 16)
        # print(c1)

        ## T1
        # G dot z1
        G_z1 = G_mul(G, z1)
        # reducing by mod x**d - 1
        for ii in range (len(G_z1)):
            foo, G_z1[ii] = div(G_z1[ii], modulus_poly)
        # pk dot c1
        pk_c1 = pk * c1
        for ii in range(len(pk_c1)):
            pk_c1[ii] = Poly(pk_c1[ii].all_coeffs(), x, modulus = Q, symmetric = True)
        # T1
        T1 = G_z1 - pk_c1
        for ii in range(len(T1)):
            T1[ii] = Poly(T1[ii].all_coeffs(), x, modulus = Q, symmetric = True)
        # print(T1)

        # ========== Step (2) ==========
        # c2
        c2_hash_object = SHA256.new()
        c2_hash_object.update(str(T1).encode())
        c2_hash_object.update(str(pk).encode())
        c2_hash_object.update(str(G_rho).encode())
        c2_hash_object.update(msg.encode()) # encode as string
        c2 = int(c2_hash_object.hexdigest(), 16)
        # print(c2) 

        # ========== Step (3) ==========
        # z2
        c2_rho = rho * c2
        # print(c2_rho)
        # for ii in range(len(c2_rho)):
        #     c2_rho[ii] = Poly(c2_rho[ii].all_coeffs(), x, modulus = Q, symmetric = True)
        # print(c2_rho)
            
        z2 = t2 - c2_rho
        for ii in range(len(z2)):
            z2[ii] = Poly(z2[ii].all_coeffs(), x, modulus = Q, symmetric = True)
            z2[ii] = z2[ii] + 1 - 1
        # print(z2)

        # Check infinity norm of z2
        md2_minus_d = (m * (degree ** 2)) - degree
        neg_md2_minus_d = md2_minus_d * -1
        inf_norm_z2 = z2.copy()
        for i in range(len(inf_norm_z2)):
            inf_norm_z2[i] = inf_norm_z2[i].max_norm()
        inf_norm_z2 = max(inf_norm_z2)
        # if inf_norm_z2 > md2_minus_d:
        if neg_md2_minus_d <= inf_norm_z2 and inf_norm_z2 <= Q-1:
            # print("inf_norm_z2 test passed")
            r = (z1, z2, c1)
            end = time.time()
            return h, r, (end - start)
        else:
            None
