# Imports 
import os 
import numpy as np
import pickle as pickle 

# Problem 4.1
Y1 = np.random.randn(loc=0, scale=2, size=50)
Y2 = np.random.randn(loc=0.3, scale=2, size=100)

with file("P4-1_data.npy", "wb") as f:
    Y1.save(f)
    Y2.save(f)

