#!/usr/bin/env bash
# $1 = venv name
# ${@:2} = list of pip packages to install

# creating virtual environment
module purge
module load python/3.7.0 venv/wrap

# installing kernel 
workon $1
pip install ${@:2}