import os
import sys
import winreg as reg

# will add bounch settings to HKEY_CURRENT_USER\Software\Classes\directory\Background\shell

PROG_NAME = "AUTOX"
PYTHON_EXE = sys.executable
SCRIPT_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "autox.py")

def create_context_class(rel_path: str, key: str, name: str | None = None):
    print(f"Creating context class {name} in {rel_path}\\{key}")
    
    reg_root = reg.OpenKey(reg.HKEY_CURRENT_USER, rel_path, 0, reg.KEY_ALL_ACCESS)
    reg_menu = reg.CreateKey(reg_root, rf"{key}\\")
    if name is not None:
        reg.SetValue(reg_menu, 'MUIVerb', reg.REG_SZ, f'{name}')
        reg.CloseKey(reg_menu)

def create_context_command(rel_path: str, command: str):
    print(fr"Creating context command {command} in {rel_path}\command")
    reg_root = reg.OpenKey(reg.HKEY_CURRENT_USER, rel_path, 0, reg.KEY_ALL_ACCESS)
    reg_menu_command = reg.CreateKey(reg_root, "command") # SubCommands
    reg.SetValue(reg_menu_command, '', reg.REG_SZ, f"{command}")
    reg.CloseKey(reg_menu_command)

def register_context_menu():
    reg_root_path = r'Software\Classes\Directory\Background\shell'

    # add the program name to the shell menu
    create_context_class(reg_root_path, PROG_NAME, name = PROG_NAME)

    # create the context command
    create_context_command(reg_root_path + rf"\{PROG_NAME}", f"{PYTHON_EXE} {SCRIPT_PATH} %v")

if __name__ == "__main__":
    register_context_menu()
