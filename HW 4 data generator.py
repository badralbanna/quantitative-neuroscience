# Imports 
import os 
import numpy as np
import pickle as pickle 

# Problem 4.1
Y1 = np.random.randn(83)*2
Y2 = np.random.randn(94)*2 + 0.3

with open(os.path.join("data", "P4-1-Y1_data.npy"), "wb") as f:
    np.save(f, Y1)
with open(os.path.join("data", "P4-1-Y2_data.npy"), "wb") as f:
    np.save(f, Y2)

# Problem 4.2 
Z1 = (np.random.randn(94)*2.3)**5
Z2 = (np.random.randn(79)*2.3 + 0.65)**3

with open(os.path.join("data", "P4-2-Z1_data.npy"), "wb") as f:
    np.save(f, Z1)
with open(os.path.join("data", "P4-2-Z2_data.npy"), "wb") as f:
    np.save(f, Z2)

