

cdef extern from "add.h":
    int add(int a, int b)

def pyadd(a, b):
    return add(a, b)