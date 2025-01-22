# AUTOX

## 1. install dependencies

Normal installation with python already installed:
```bash
pip install git+https://github.com/CurssedCoffin/AUTOX
autox_setup # initialize the setup
# add a password, like autox_add_pass "123456" to add "123456" to the password file
```

Or quick install with uv virtual environment:

First, install uv, check [uv github repo](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)
```bash
uv venv autox --python 3.10 # create a virtual environment with python 3.10 at current directory
autox\Scripts\activate # activate the virtual environment
uv pip install git+https://github.com/CurssedCoffin/AUTOX # install the package with uv
autox_setup
# add a password, like autox_add_pass "123456" to add "123456" to the password file
```

## 2. command line
If installed with uv virtual environment, must activate the virtual environment first:
```bash
autox\Scripts\activate
```

```bash
# This will add a "AUTOX" option to the context menu of the folder.
# It tries to add AUTOX key to the registry ```HKEY_CURRENT_USER\Software\Classes\directory\Background\shell```.
autox_setup 

# show password file path
# Content: one line one password
autox_show_pass_path 

# show password
autox_show_pass 

# add a password, like 123456
autox_add_pass "123456"

# empty password file
autox_empty_pass 
```

## 3. run autox.py

Right click on plain area of a folder, and select "AUTOX" to extract all files in the folder.
