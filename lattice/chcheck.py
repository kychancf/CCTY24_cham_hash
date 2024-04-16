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

def CHCHECK(m, n, degree, G, pk, msg, h, r):

    start = time.time()

    # Parse r
    z1 = r[0]
    z2 = r[1]
    c1 = r[2]

    # H(m)
    hash_object = SHA256.new()
    hash_object.update(msg.encode()) # encode as string
    h_m = int(hash_object.hexdigest(), 16)

    # y_prime
    y_prime = h - h_m
    for ii in range(len(y_prime)):
        y_prime[ii] = Poly(y_prime[ii].all_coeffs(), x, modulus = Q, symmetric = True)
    # print(y_prime)

    ## T1
    # G dot z1
    G_z1 = G_mul(G, z1) # vector
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

    ## c2
    c2_hash_object = SHA256.new()
    c2_hash_object.update(str(T1).encode())
    c2_hash_object.update(str(pk).encode())
    c2_hash_object.update(str(y_prime).encode())
    c2_hash_object.update(msg.encode()) # encode as string
    c2 = int(c2_hash_object.hexdigest(), 16)
    # print(c2)

    ## T2
    # G dot z2
    G_z2 = G_mul(G, z2) # vector
    # reducing by mod x**d - 1
    for ii in range (len(G_z2)):
        foo, G_z2[ii] = div(G_z2[ii], modulus_poly)
        G_z2[ii] = Poly(G_z2[ii].all_coeffs(), x, modulus = Q, symmetric = True)
    # y' dot c2
    y_prime_c2 = y_prime * c2
    # reducing by mod x**d - 1
    for ii in range(len(y_prime_c2)):
        y_prime_c2[ii] = Poly(y_prime_c2[ii].all_coeffs(), x, modulus = Q, symmetric = True)
    # T2
    T2 = G_z2 + y_prime_c2
    # reducing by mod x**d - 1
    for ii in range(len(T2)):
        T2[ii] = Poly(T2[ii].all_coeffs(), x, modulus = Q, symmetric = True)
    # print(T2)

    ## c1_test
    c1_test_hash_object = SHA256.new()
    c1_test_hash_object.update(str(T2).encode())
    c1_test_hash_object.update(str(pk).encode())
    c1_test_hash_object.update(str(y_prime).encode())
    c1_test_hash_object.update(msg.encode()) # encode as string
    c1_test = int(c1_test_hash_object.hexdigest(), 16)
    # print(c1_test)

    ## Tests
    result = True

    # Check is c1 = c1_test
    if c1 == c1_test:
        None
        # print("c1_test test passed!")
    else:
        print("c1_test test failed...")
        result = False
    
    # Check infinity norm of z1
    md2_minus_d = (m * (degree ** 2)) - degree
    inf_norm_z1 = z1.copy()
    inf_norm_z1 = inf_norm_z1 + 1 - 1 # Type conversion
    for i in range(len(inf_norm_z1)):
        inf_norm_z1[i] = inf_norm_z1[i].max_norm()
    inf_norm_z1 = max(inf_norm_z1)
    if inf_norm_z1 <= md2_minus_d:
        None
        # print("z1 test passed!")
    else:
        print("z1 test failed...")
        result = False

    # Check infinity norm of z2
    inf_norm_z2 = z2.copy()
    for i in range(len(inf_norm_z2)):
        inf_norm_z2[i] = inf_norm_z2[i].max_norm()
    inf_norm_z2 = max(inf_norm_z2)
    if inf_norm_z2 > md2_minus_d:
        None
        # print("z2 test passed!")
    else:
        print("z2 test failed...")
        result = False

    end = time.time()

    return result, (end - start)