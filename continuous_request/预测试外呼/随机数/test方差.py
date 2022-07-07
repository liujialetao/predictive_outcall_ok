import numpy as np
from matplotlib import pyplot as plt

size = 200
x = np.random.normal(loc=30, scale=5, size=size)
x1 = np.array([3,4,5,8,9])

def cal_var(x, mean):
    sum=0
    for ele in x:
        sum+=(ele-mean)*(ele-mean)
    var = sum/len(x)
    return var

mean = np.mean(x)
var = np.var(x)
var2 = cal_var(x, mean)

pass