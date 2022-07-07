import numpy as np
from matplotlib import pyplot as plt

sum = 0
for i in range(1000):
    x = np.random.choice(2,size=1,p=[0.7,0.3])
    sum+=x[0]
print(sum)

pass