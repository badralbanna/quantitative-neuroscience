#!/usr/bin/env bash
module load python/3.7.0
python /ihome/sam/bmooreii/workspace/crc-wrappers/jupyter-kernel/crc-jupyter-kernel.py -n py3-qn -d "Python 3 (QN)" -p "numpy scipy matplotlib seaborn xarray netCDF4 pandas xlrd h5py patsy dowhy causalgraphicalmodels seaborn statsmodels scikit-learn dabest"

