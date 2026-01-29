import numpy as np

cpp_2400=np.load("./data/cpp_2400.txt")
python_2400=np.load("./data/python_2400.txt")

cpp_pair_mathch=[]
python_pair_mathch=[]

for a in cpp_2400:
    for b in cpp_2400:
        cpp_pair_mathch.append(a==b)

for a in python_2400:
    for b in python_2400:
        python_pair_mathch.append(a==b)

matched=0

for a,b in zip(cpp_pair_mathch,python_pair_mathch):
    matched+=a==b

print(matched/len(cpp_pair_mathch))