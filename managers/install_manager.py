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
            logger.critical(f"不支持的操作系统平台: {self.platform}")
            sys.exit(1)
    
    def uninstall(self):
        if self.platform == "win32":
            return self.uninstall_win32()
        else:
            logger.critical(f"不支持的操作系统平台: {self.platform}")
            sys.exit(1)

    def install_win32(self):
        def create_context_class(rel_path: str, key: str, name: str | None = None):
            logger.info(f"正在创建右键菜单类 {name} 于 {rel_path}\\{key}")
            
            reg_root = reg.OpenKey(reg.HKEY_CURRENT_USER, rel_path, 0, reg.KEY_ALL_ACCESS)
            reg_menu = reg.CreateKey(reg_root, rf"{key}\\")
            if name is not None:
                reg.SetValue(reg_menu, 'MUIVerb', reg.REG_SZ, f'{name}')
                reg.CloseKey(reg_menu)
        
        def create_context_command(rel_path: str, command: str):
            logger.info(fr"正在创建右键菜单命令 {command} 于 {rel_path}\command")
            reg_root = reg.OpenKey(reg.HKEY_CURRENT_USER, rel_path, 0, reg.KEY_ALL_ACCESS)
            reg_menu_command = reg.CreateKey(reg_root, "command") # SubCommands
            reg.SetValue(reg_menu_command, '', reg.REG_SZ, f"{command}")
            reg.CloseKey(reg_menu_command)
        
        def register_context_menu():
            reg_root_path = r'Software\Classes\Directory\Background\shell'

            # 添加程序名到 shell 菜单
            create_context_class(reg_root_path, "AUTOX", name = "AUTOX")

            # 创建右键菜单命令
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
            logger.info(f"正在移除右键菜单项: {key_path}\\command")
            reg.DeleteKey(reg.HKEY_CURRENT_USER, rf'{key_path}\command')
            logger.info(f"正在移除右键菜单项: {key_path}\\MUIVerb")
            reg.DeleteKey(reg.HKEY_CURRENT_USER, rf'{key_path}\MUIVerb')
            logger.info(f"正在移除右键菜单项: {key_path}")
            reg.DeleteKey(reg.HKEY_CURRENT_USER, rf'{key_path}')
        except:
            success = False
        
        return success