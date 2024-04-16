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


# General parameters
N = 7
M = 15
# degree of the polynomial in the matrix G' (use 128)
DEGREE = 128
# q: random prime; around size 2^26 bits, pq = 1 mod 256
Q = 33564673

# useful global varaibles to avoid repeat computation
one_poly = [1] * DEGREE
zero_poly = [0] * DEGREE
one_poly = Poly(one_poly, x, modulus = Q, symmetric = True)
zero_poly = Poly(zero_poly, x, modulus = Q, symmetric = True)

# x**d + 1
modulus_poly = [0] * (DEGREE + 1)
modulus_poly[0] = 1
modulus_poly[DEGREE] = 1
modulus_poly = Poly(modulus_poly, x, modulus = Q, symmetric = True)

# for polynomial multiplication, either use fftconvolve(m1, m2) or Poly1 * Poly2


# return a random polynomial with degree d - 1 and coefficient mod Q
def random_poly(d):
    vector = [None] * d
    for i in range (d):
        vector[i] = secrets.randbelow(Q)
    return Poly(vector, x, modulus = Q, symmetric = True)


# return a random polynomial with degree d - 1 and coefficient 0, 1 or -1
def random_special_poly(d):
    choice_list = [0, 1, -1]
    vector = [None] * d
    for i in range (d):
        vector[i] = secrets.choice(choice_list)
    return Poly(vector, x, modulus = Q, symmetric = True)


# generate polynomial in S with degree d - 1 and coefficient mod md^2
def generate_S(d):
    vector = [None] * d
    for i in range (d):
        num = secrets.randbelow(M * d**2 * 2)
        num = num - M * d**2
        vector[i] = num
    return Poly(vector, x, modulus = Q)


# return the vector S with M + 1 polynomials
def random_special_S(d):
    column = []
    for i in range (M):
        column.append(generate_S(d))
#     append 0 polynomial at end
    column.append(zero_poly)
    np_column = np.asarray(column)
    return (np.transpose(np_column))


# generate polynomial in S with degree d - 1 and coefficient mod (md^2 - d)
def generate_S_md2_minus_d(d):
    vector = [None] * d
    for i in range (d):
        num = secrets.randbelow(((M * d**2) - d) * 2)
        num = num - ((M * d**2) - d)
        vector[i] = num
    return Poly(vector, x, modulus = Q)


# return the vector S with M + 1 polynomials and coefficient mod (md^2 - d) 
def random_special_S_md2_minus_d(d):
    column = []
    for i in range (M):
        column.append(generate_S_md2_minus_d(d))
#     append 0 polynomial at end
    column.append(zero_poly)
    np_column = np.asarray(column)
    return (np.transpose(np_column))


# return the vector with all coefficient 1, 0 or -1 with M + 1 
def random_special_column(d):
    column = []
    for i in range (M):
        column.append(random_special_poly(d))
#     append 0 polynomial at end
    column.append(zero_poly)
    np_column = np.asarray(column)
    return (np.transpose(np_column))


# input: one_x: one specific x(a polynomial); one_pk: one public key, a vector of polynomials
def x_pk_mul(one_x, one_pk):
    result = [None] * len(one_pk)
    for i in range (len(one_pk)):
#         call ntt
        product = convolutions.convolution_ntt(one_x.all_coeffs(), one_pk[i].all_coeffs(), prime = 16389* 2**11 + 1)
        result[i] = Poly(product, x, modulus = Q, symmetric = True)
    return np.asarray(result)


# transform a number to its ternary form
def ternary(n):
    if n == 0:
        return '0'
    nums = []
    while n:
        n, r = divmod(n, 3)
        nums.append(str(r))
    return ''.join(reversed(nums))


# input: a ternary string; the number of bits should be larger than the highest degree
# output: a polynomial with each coefficient between 0, 1, -1
# ternary 2 becomes -1 in our case
def ternary_poly(ter_str, degree):
    coef = []
    for i in range (degree):
        current_num = int(ter_str[i])
        if current_num == 2:
            coef.append(-1)
        else:
            coef.append(current_num )
    return Poly(coef, x, modulus = 3, symmetric = True)


# check if z coefficients are in range 
# return 0 if fail, 1 if success
def z_check(z):
#     start_time = time.time()
    for i in range (len(z)):
        this_poly = z[i]
        this_coef = this_poly.all_coeffs()
        for coef in this_coef:
            c = int(coef)
            c = abs(coef)
            if c > M * DEGREE**2 - DEGREE:
#             print(coef)
#             if coef > 0:
#                 print('z check failed')
                return 0
    return 1


# doing z_check on a specific row
def z_check_row(z):
#     start_time = time.time()
    this_coef = z.all_coeffs()
    for coef in this_coef:
        c = int(coef)
        c = abs(coef)
        if c > M * DEGREE**2 - DEGREE:
#             print(coef)
#             if coef > 0:
#                 print('z check failed')
            return 0
    return 1


# transform the x corresponded to the secret key to have coefficient 0, 1 or -1
def find_my_x(p):
    coef = []
    my_coef = p.all_coeffs()
    length = len(my_coef)
    difference = DEGREE - length
    for i in range (length):
        current_num = int(my_coef[length - i - 1]) % 3
        if current_num == 2:
            coef.append(-1)
        else:
            coef.append(current_num)
    for i in range (difference):
        coef.append(0)
    list.reverse(coef)
    return Poly(coef, x, modulus = 3, symmetric = True)


# using ntt and matrix multiplication (involving matrix G)
def G_mul(g, s):
    result = []
    for i in range (N):
        result.append(Poly([0], x, modulus = Q, symmetric = True))
    for i in range(len(g)): 
        for k in range(len(s)): 
            product = convolutions.convolution_ntt(g[i][k].all_coeffs(), s[k].all_coeffs(), prime = 16389* 2**11 + 1)
            result[i] = result[i] + Poly(product, x, modulus = Q, symmetric = True)
    return np.asarray(result)