import numpy as np
import argparse
from itertools import permutations

def print_example_of_transpose(nD: int, minD: int, maxD: int):
    print(f'# Example for {nD}D-tensor with float type element')
    Dsize = np.random.randint(minD, maxD, size=nD)
    a = np.arange(np.multiply.reduce(Dsize), dtype=np.uint64).reshape(Dsize)
    print(f'Source:\n{a}')
    for T in permutations(np.arange(nD, dtype=np.int32)):
        print(f'Result transpose {T}:')
        b = np.transpose(a, T)
        print(b)
        

def main(args):
    if args.test1: print_example_of_transpose(nD=3, minD=4, maxD=6)
    if args.test2: print_example_of_transpose(nD=4, minD=4, maxD=6)
    if args.test3: print_example_of_transpose(nD=5, minD=4, maxD=6)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Transpose example')
    parser.add_argument('--test1', action='store_true')
    parser.add_argument('--test2', action='store_true')
    parser.add_argument('--test3', action='store_true')
    args = parser.parse_args()
    main(args)