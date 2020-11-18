#!/usr/bin/env bash

module purge
module load python/3.7.0 venv/wrap
module load git 

# installing kernel 
workon py3-qn

mkdir packages
cd packages
git clone https://github.com/bantin/jPCA.git
git clone https://github.com/BouchardLab/DynamicalComponentsAnalysis
git clone https://github.com/pavanramkumar/pyglmnet

cd jPCA 
pip install -e .
cd ../DynamicalComponentsAnalysis
pip install -e .
cd ../pyglmnet
pip install -e .

cd ../..