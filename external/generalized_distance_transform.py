#!/usr/bin/python3
# coding=utf-8
from copy import deepcopy

from numpy.random import random
from matplotlib import pyplot as plt

__author__ = 'bbogacz'

# Batteries

# Numpy
from numpy import zeros, inf, array


def of_column(dataInput):
    f = dataInput
    n = len(dataInput)

    d = zeros((n, ))
    v = zeros((n,))
    z = zeros((n + 1,))
    k = 0

    v[0] = 0
    z[0] = -2**31
    z[1] = +2**31

    for q in range(1, n):
        s = (((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2.0 * q - 2.0 * v[k]))
        while s <= z[k]:
            k -= 1
            s = (((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2.0 * q - 2.0 * v[k]))
        k += 1
        v[k] = q
        z[k] = s
        z[k + 1] = +2**31

    k = 0

    for q in range(n):
        while z[k + 1] < q:
            k += 1
        d[q] = ((q - v[k]) * (q - v[k]) + f[v[k]])

    return d


def of_image(I):
    D1 = zeros(I.shape)
    for i in range(0, I.shape[0]):
        D1[i, :] = of_column(I[i, :])

    D2 = zeros(I.shape)
    for i in range(0, I.shape[1]):
        D2[:, i] = of_column(D1[:, i])

    return D2

