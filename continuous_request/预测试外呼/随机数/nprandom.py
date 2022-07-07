import numpy as np

a = []
N = 100
for i in range(N):
    x = np.random.normal(loc=30, scale=4)
    print(x)
    a.append(x)
mean = np.mean(a)
var = np.var(a)
print(mean, var)
pass


