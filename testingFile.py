import math
from timeit import timeit

import numpy


N = 1_000_000
x = 1.23

print("numpy:", timeit("""
numpy.cos(x)
""", number=N, globals=globals()))

print("math:", timeit("""
math.cos(x)
""", number=N, globals=globals()))