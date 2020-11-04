#!/usr/bin/env /ihome/crc/wrappers/py3_wrap.sh
""" crc-jupyter-kernel.py Create a virtual environment which works with hub.crc.pitt.edu
Usage:
    crc-jupyter-kernel.py (-n <name>) [-d <display>] [-p <args>] [-hvcV]

Positional Arguments:
    -n --name <name>                The name of the kernel
    -d --display <display>          The display name of the kernel in Jupyter
    -p --pass <args>                Pass these arguments to `pip install` or `conda install -n <name>`
    -c --conda                      Use conda (default is use virtualenvwrapper)
    -V --verbose                    Print output from commands

Options:
    -h --help                       Print this screen and exit
    -v --version                    Print the version of crc-scontrol.py

Examples:
    - Install pytorch using virtualenvwrapper:

        crc-jupyter-kernel.py -n torch -d "PyTorch" -p "torch==1.7.0+cu101 torchvision==0.8.1+cu101 torchaudio==0.7.0 -f https://download.pytorch.org/whl/torch_stable.html"

    - Install packages from a requirements.txt file:

        crc-jupyter-kernel.py -n environment -d "Environment" -p "requirements.txt"

    - Install pytorch using conda:

        crc-jupyter-kernel.py -n torch -d "PyTorch" -c -p "pytorch torchvision torchaudio cudatoolkit=10.1 -c pytorch"

    - Install from an environment.yml file (it must use `python=3.7` or it will fail!)

        crc-jupyter-kernel.py -n environment -d "Environment" -c -p "environment.yml"

Notes:
    - If you use `-c` and `-p` is given `*.yml` or `*.yaml` the script will
      assume you want `conda env create -f *.yml` and not `conda install`
"""

from docopt import docopt
from pathlib import Path
import os
import stat
from tempfile import mkstemp
from subprocess import Popen, PIPE
import json
from shutil import copy
import yaml

args = docopt(__doc__, version="crc-jupyter-kernel.py version 0.0.1")

# We need the home directory for later
home_directory = os.environ["HOME"]

# No space like characters allowed in the kernel name!
# -> docopt will strip leading/trailing spaces automatically
if len(args["--name"].split()) > 1:
    print("Error: the `--name` parameter can not accept space characters!")
    print("Allowed:")
    print("  hello")
    print("  hello_world")
    print("  hello-world-123")
    exit()

# Analyze the arguments to be passed to pip or conda
# If we find:
#   - requirements.txt: don't use conda, add `-r` to `pip install`
#   - environment.yml: use conda, don't use `conda install` use `conda env create`
# Else: just pass the arguments and hope the user knows what they are doing
requirements_txt = False
environment_yaml = False
if args["--pass"]:
    split_pass = args["--pass"].split()
    if len(split_pass) == 1:
        p = Path(args["--pass"])
        if p.is_file() and p.name == "requirements.txt":
            print("Warning: detected requirements.txt file, using virtualenvwrapper")
            args["--conda"] = False
            requirements_txt = True
        elif p.is_file() and p.suffix in [".yml", ".yaml"]:
            print("Warning: detected environment.yml file, using conda")
            args["--conda"] = True
            environment_yaml = True
        else:
            print(
                "Warning: no requirements.txt or environment.yml file detected, passing arguments verbatim"
            )
else:
    args["--pass"] = ""

# Which virtual environment provider should we use?
suffix = "venv"
if args["--conda"]:
    suffix = "conda"

# Set or append the environment to the display name
if not args["--display"]:
    args["--display"] = f"{args['--name']} ({suffix})"
else:
    args["--display"] = f"{args['--display']} ({suffix})"

# This script shouldn't overwrite existing virtual environments

script_header = """\
#!/usr/bin/env bash
source /ihome/crc/install/lmod/lmod/init/bash &> /dev/null
module purge &> /dev/null
module load python/3.7.0 venv/wrap &> /dev/null
{0}
"""

if args["--conda"]:
    env_list = script_header.format("conda env list --json")
else:
    env_list = script_header.format("workon")

def generate_and_run_script(contents):
    # Make a temporary file
    _, fname = mkstemp()
    pth = Path(fname)

    # Write the contents of the script
    with open(pth, "w") as f:
        f.write(contents)

    # Run the script capturing standard output/standard error
    stdout, stderr = Popen(["bash", pth], stdout=PIPE, stderr=PIPE).communicate()

    pth.unlink()

    return stdout.decode("utf-8"), stderr.decode("utf-8")

out, err = generate_and_run_script(env_list)

if err == "":
    if args["--conda"]:
        json_d = json.loads(out)
        list_of_env_names = [Path(x).name for x in json_d["envs"]]
        if args["--name"] in list_of_env_names:
            print(f"Error: A conda environment with name `{args['--name']}` exists already")
            exit()
    else:
        if args["--name"] in out.split("\n"):
            print(f"Error: A virtualenvwrapper environment with name `{args['--name']}` exists already")
            exit()
else:
    exit(f"Please report this error at crc.pitt.edu/tickets: {err}")

kernel_wrapper_location = f"{home_directory}/.local/bin/{args['--name']}_{suffix}.sh"

# 2. Build the virtual environment with ipykernel

virtualenvwrapper_create = """\
mkvirtualenv {0}
workon {0}
pip install {1} ipykernel
"""

conda_install = """\
conda create -y -n {0} python=3.7 ipykernel {1}
"""

conda_install_environment = """\
conda env create -y -n {0} -f {1}
conda install -y -n {0} ipykernel
"""

def build_virtual_environment_script(args, environment_yaml, requirements_txt):
    if args["--conda"]:
        if environment_yaml:
            # Check that environment_yaml contains python=3.7
            with open(args["--pass"], "r") as f:
                yml = yaml.safe_load(f.read())
            if "python=3.7" not in yml["dependencies"]:
                print(f"Error: hub.crc.pitt.edu will only work with Python 3.7 environments")
                exit()
            return script_header.format(
                conda_install_environment.format(args["--name"], args["--pass"])
            )
        else:
            return script_header.format(
                conda_install.format(args["--name"], args["--pass"])
            )
    else:
        if requirements_txt:
            return script_header.format(
                virtualenvwrapper_create.format(args["--name"], f"-r {args['--pass']}")
            )
        else:
            return script_header.format(
                virtualenvwrapper_create.format(args["--name"], args["--pass"])
            )

virtual_env_script = build_virtual_environment_script(
    args, environment_yaml, requirements_txt
)

print("Progress: This might take a while, I am building you a virtual environment...")
out, err = generate_and_run_script(virtual_env_script)
if args["--verbose"]:
    print("--> output <--")
    print(out)
    print("--> error <--")
    print(err)
print("Progress: virtual environment built")

# 3. Build an executable kernel wrapper for the environment

virtualenvwrapper_wrapper = """\
workon {0}
python $@
"""

conda_wrapper = """\
source activate {0}
python $@
"""

def build_kernel_wrapper(args):
    if args["--conda"]:
        return script_header.format(
            conda_wrapper.format(args["--name"])
        )
    else:
        return script_header.format(
            virtualenvwrapper_wrapper.format(args["--name"])
        )

# Create the contents for the wrapper, write them out, and make it executable
kernel_wrapper = build_kernel_wrapper(args)
local_bin = Path(f"{home_directory}/.local/bin")
local_bin.mkdir(parents=True, exist_ok=True)
with open(kernel_wrapper_location, "w") as f:
    f.write(kernel_wrapper)
st = os.stat(kernel_wrapper_location)
os.chmod(kernel_wrapper_location, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# 4. Install a kernel.json file into home directory

kernel_json = f"""\
{{
 "argv": [
  "{kernel_wrapper_location}",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{{connection_file}}"
 ],
 "display_name": "{args["--display"]}",
 "language": "python"
}}
"""

# Generate the kernel directory in user space, populate kernel.json and copy the Python image files
kernel_json_location_dir = Path(f"{home_directory}/.local/share/jupyter/kernels/{args['--name']}_{suffix}")
kernel_json_location_dir.mkdir(parents=True, exist_ok=True)
kernel_json_location = kernel_json_location_dir / "kernel.json"
thirty_two = Path("/ihome/crc/install/python/miniconda3-3.7/share/jupyter/kernels/python3/logo-32x32.png")
sixty_four = Path("/ihome/crc/install/python/miniconda3-3.7/share/jupyter/kernels/python3/logo-64x64.png")
with open(kernel_json_location, "w") as f:
    f.write(kernel_json)
copy(thirty_two, kernel_json_location_dir / "logo-32x32.png")
copy(sixty_four, kernel_json_location_dir / "logo-64x64.png")

print("--> Summary <--")
print(f"""\
I built a python/3.7.0 virtual environment for you with the name `{args['--name']}`

To access the environment, first run:

```
module purge
module load python/3.7.0 venv/wrap
```

""")
if args["--conda"]:
    print(f"- activate it with `source activate {args['--name']}`")
    print(f"- remove it with `conda env remove -n {args['--name']}`")
else:
    print(f"- activate it with `workon {args['--name']}`")
    print(f"- remove it with `rmvirtualenv {args['--name']}`")
print(f"- a kernel wrapper was installed here: {kernel_wrapper_location}")
print(f"- the jupyter kernel was installed here: {kernel_json_location_dir}")
