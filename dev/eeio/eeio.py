# %%
import h5py
import numpy as np
filepath = '/Users/michaelweinold/data/REX3_Labels/Labels_Sectors_REX3.mat'
arrays = {}
f = h5py.File(filepath)
for k, v in f.items():
    arrays[k] = np.array(v)