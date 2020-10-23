#!/usr/bin/env bash
# $1 = venv name
# $2 = long name for jupyter 
# ${@:3} = list of pip packages to install

# recording current directory
PWD0=$PWD

#Storing user directory as variable
USERDIR=/ihome/$(groups)/$USER

# creating virtual environment
module purge
module load python/3.7.0 venv/wrap
mkvirtualenv -p python $1 

# installing kernel 
workon $1
pip install ipykernel ${@:3}
python -m ipykernel install --user --name $1 --display-name "$2"
KERNELDIR=$USERDIR/.local/share/jupyter/kernels/$1

# create kernel_wrapper.sh
cd $KERNELDIR
cat <<EOF > kernel_wrapper.sh
#!/usr/bin/env bash
source /ihome/crc/install/lmod/lmod/init/bash
module purge
module load python/3.7.0 venv/wrap
workon $1
exec $USERDIR/.virtualenvs/$1/bin/python \$@
EOF

# make kernel_wrapper.sh executable
chmod u+x kernel_wrapper.sh

# modify kernel.json
rm kernel.json
cat <<EOF > kernel.json
{
 "argv": [
  "$KERNELDIR/kernel_wrapper.sh",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "$2",
 "language": "python"
}
EOF

# go back
cd $PWD0
