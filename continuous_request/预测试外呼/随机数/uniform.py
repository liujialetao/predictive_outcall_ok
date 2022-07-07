import numpy as np

a=[]
for i in range(100):
    a.append(np.random.uniform(low=3, high=10))
a = np.array(a)
mean= a.mean()

def cal_var(x, mean):
    sum=0
    for ele in x:
        sum+=(ele-mean)*(ele-mean)
    var = sum/len(x)
    return var

var2 = cal_var(a,mean)
var = a.var()
print(mean, var2,var)
print(mean, var2,var)