import numpy as np


a=[]
for i in range(1000):
    a.append(np.random.randint(0,11))

mean= np.array(a).mean()
pass