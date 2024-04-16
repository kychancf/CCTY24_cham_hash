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
from chcheck import *

def CHADAPT(m, n, degree, G, pk, sk, msg, msg_prime, h, r):
    
    start = time.time()

    chcheck_result, chcheck_time = CHCHECK(m, n, degree, G, pk, msg, h, r)
    if chcheck_result == True:
        None
        # print("CHCheck test passed!")
    else:
        print("CHCheck test failed... Terminating")
        quit()
    
    # Parse r
    z1 = r[0]
    z2 = r[1]
    c1 = r[2]

    # H(m)
    hash_object = SHA256.new()
    hash_object.update(msg_prime.encode()) # encode as string
    h_m = int(hash_object.hexdigest(), 16)

    # y_prime
    y_prime = h - h_m
    for ii in range(len(y_prime)):
        y_prime[ii] = Poly(y_prime[ii].all_coeffs(), x, modulus = Q, symmetric = True)
    # print(y_prime)

    while True:
        # NIZK Proof
        # ========== Step (1) ==========
        # t1_prime and z2_prime
        t1_prime = random_special_S(DEGREE) # vector
        z2_prime = random_special_S_md2_minus_d(DEGREE) # vector
        # print(z1)

        ## T1_prime
        T1_prime = G_mul(G, t1_prime)
        # reducing by mod x**d - 1
        for ii in range (len(T1_prime)):
            foo, T1_prime[ii] = div(T1_prime[ii], modulus_poly)

        # c2
        c2_hash_object = SHA256.new()
        c2_hash_object.update(str(T1_prime).encode())
        c2_hash_object.update(str(pk).encode())
        c2_hash_object.update(str(y_prime).encode())
        c2_hash_object.update(msg_prime.encode()) # encode as string
        c2_prime = int(c2_hash_object.hexdigest(), 16)
        # print(c2_prime) 

        ## T2
        # G dot z2
        G_z2 = G_mul(G, z2) # vector
        # reducing by mod x**d - 1
        for ii in range (len(G_z2)):
            foo, G_z2[ii] = div(G_z2[ii], modulus_poly)
            G_z2[ii] = Poly(G_z2[ii].all_coeffs(), x, modulus = Q, symmetric = True)
        # y' dot c2_prime
        y_prime_c2_prime = y_prime * c2_prime
        # reducing by mod x**d - 1
        for ii in range(len(y_prime_c2_prime)):
            y_prime_c2_prime[ii] = Poly(y_prime_c2_prime[ii].all_coeffs(), x, modulus = Q, symmetric = True)
        # T2
        T2 = G_z2 + y_prime_c2_prime
        # reducing by mod x**d - 1
        for ii in range(len(T2)):
            T2[ii] = Poly(T2[ii].all_coeffs(), x, modulus = Q, symmetric = True)
        # print(T2)

        # ========== Step (2) ==========
        # c1
        c1_hash_object = SHA256.new()
        c1_hash_object.update(str(T2).encode())
        c1_hash_object.update(str(pk).encode())
        c1_hash_object.update(str(y_prime).encode())
        c1_hash_object.update(msg_prime.encode()) # encode as string
        c1_prime = int(c1_hash_object.hexdigest(), 16)
        # print(c1_prime)

        # ========== Step (3) ==========
        # z1_prime
        c1_prime_x = sk * c1_prime
        # for ii in range(len(c1_prime_x)):
        #     c1_prime_x[ii] = Poly(c1_prime_x[ii].all_coeffs(), x, modulus = Q, symmetric = True)

        z1_prime = t1_prime - c1_prime_x
        for ii in range(len(z1_prime)):
            z1_prime[ii] = Poly(z1_prime[ii].all_coeffs(), x, modulus = Q, symmetric = True)
            z1_prime[ii] = z1_prime[ii] + 1 - 1

        # Check infinity norm of z1_prime
        md2_minus_d = (m * (degree ** 2)) - degree
        neg_md2_minus_d = md2_minus_d * -1
        inf_norm_z1_prime = z1_prime.copy()
        for i in range(len(inf_norm_z1_prime)):
            inf_norm_z1_prime[i] = inf_norm_z1_prime[i].max_norm()
        inf_norm_z1_prime = max(inf_norm_z1_prime)
        if neg_md2_minus_d <= inf_norm_z1_prime and inf_norm_z1_prime <= Q-1:
            # print("inf_norm_z1_prime test passed")
            r_prime = (z1_prime, z2_prime, c1_prime)
            end = time.time()
            return r_prime, chcheck_time, (end - start)
        else:
            None