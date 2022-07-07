import numpy as np

x = np.random.choice(['unsuccess_call','success_call' ],size=1,p=[0.7,0.3])[0]
print(x)