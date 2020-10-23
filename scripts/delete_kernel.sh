#!/usr/bin/env bash
# $1 = venv/kernel name

#Storing user directory as variable
USERDIR=/ihome/$(groups)/$USER
KERNELDIR=$USERDIR/.local/share/jupyter/kernels/$1

# initializing virtual environments
module purge
module load python/3.7.0 venv/wrap

# deleting jupyter kernel 
rm $KERNELDIR/kernel_wrapper.sh
jupyter kernelspec remove $1

# deleting virtualenvironment
rmvirtualenv $1
