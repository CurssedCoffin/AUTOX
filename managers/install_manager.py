from managers.logger_manager import logger

import os
import sys

if sys.platform == "win32":
    import winreg as reg

class InstallManager:
    def __init__(self) -> None:
        self.platform = sys.platform
        # a.exe or python.exe autox.py
        self.command = os.path.abspath(sys.executable) if hasattr(sys, "frozen") else f"{sys.executable} {os.path.join(os.path.abspath(os.path.dirname(__file__)), 'autox.py')}"
    
    def install(self):
        if self.platform == "win32":
            return self.install_win32()
        else:
            logger.critical(f"Platform {self.platform} not supported")
            sys.exit(1)
    
    def uninstall(self):
        if self.platform == "win32":
            return self.uninstall_win32()
        else:
            logger.critical(f"Platform {self.platform} not supported")
            sys.exit(1)

    def install_win32(self):
        def create_context_class(rel_path: str, key: str, name: str | None = None):
            logger.info(f"Creating context class {name} in {rel_path}\\{key}")
            
            reg_root = reg.OpenKey(reg.HKEY_CURRENT_USER, rel_path, 0, reg.KEY_ALL_ACCESS)
            reg_menu = reg.CreateKey(reg_root, rf"{key}\\")
            if name is not None:
                reg.SetValue(reg_menu, 'MUIVerb', reg.REG_SZ, f'{name}')
                reg.CloseKey(reg_menu)
        
        def create_context_command(rel_path: str, command: str):
            logger.info(fr"Creating context command {command} in {rel_path}\command")
            reg_root = reg.OpenKey(reg.HKEY_CURRENT_USER, rel_path, 0, reg.KEY_ALL_ACCESS)
            reg_menu_command = reg.CreateKey(reg_root, "command") # SubCommands
            reg.SetValue(reg_menu_command, '', reg.REG_SZ, f"{command}")
            reg.CloseKey(reg_menu_command)
        
        def register_context_menu():
            reg_root_path = r'Software\Classes\Directory\Background\shell'

            # add the program name to the shell menu
            create_context_class(reg_root_path, "AUTOX", name = "AUTOX")

            # create the context command
            create_context_command(reg_root_path + rf'\{"AUTOX"}', f'{self.command} %v')
        
        success = True
        try:
            register_context_menu()
        except:
            success = False
        
        return success
    
    def uninstall_win32(self):
        key_path = r'Software\Classes\Directory\Background\shell\AUTOX'
        success = True
        
        try:
            logger.info(f"Removing context menu entry: {key_path}\command")
            reg.DeleteKey(reg.HKEY_CURRENT_USER, rf'{key_path}\command')
            logger.info(f"Removing context menu entry: {key_path}\MUIVerb")
            reg.DeleteKey(reg.HKEY_CURRENT_USER, rf'{key_path}\MUIVerb')
            logger.info(f"Removing context menu entry: {key_path}")
            reg.DeleteKey(reg.HKEY_CURRENT_USER, rf'{key_path}')
        except:
            success = False
        
        return success
