#!/usr/bin/env bash

module purge
module load python/3.7.0 venv/wrap
mkvirtualenv -p python py3-qn
workon py3-qn
pip install ipykernel numpy scipy matplotlib xarray pandas h5py dowhy causalgraphicalmodels
python -m ipykernel install --user --name=py3-qn --display-name "Python 3 (QN)"
