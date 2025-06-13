from managers.password_manager import PasswordManager
from managers.install_manager import InstallManager
from managers.logger_manager import logger

import os
import sys

class ConsoleManager:
    def __init__(self) -> None:
        self.main_menu()
    
    def main_menu(self):
        key_map = {
            "q": {"msg": "退出", "func": self.quit},
            "1": {"msg": "安装右键菜单", "func": self.install},
            "2": {"msg": "卸载右键菜单", "func": self.uninstall},
            "3": {"msg": "添加密码", "func": self.add_password_menu},
            "4": {"msg": "删除密码", "func": self.del_password_menu},
            "5": {"msg": "显示所有密码", "func": self.show_password_menu},
            "6": {"msg": "清空所有密码", "func": self.cls_password_menu},
        }
        print("=" * 30 + "\n" + "\n".join([f'{k}: {v["msg"]}' for k, v in key_map.items()]))
        key = input("请输入选项: ")
        os.system("cls" if sys.platform == "win32" else "clear")
        
        if key not in key_map:
            self.main_menu()
        else:
            key_map[key]["func"]()
            self.main_menu()

    def install(self):
        success = InstallManager().install()
        if success:
            logger.success("安装成功")
        else:
            logger.error("安装失败")
    
    def uninstall(self):
        success = InstallManager().uninstall()
        if success:
            logger.success("卸载成功")
        else:
            logger.error("卸载失败")

    def add_password_menu(self):
        passwords = PasswordManager().read_password()
        password = input("请输入密码: ")

        if password == "":
            logger.warning("密码不能为空。")
            return
        elif password in passwords:
            logger.warning(f"密码: {password} 已存在。")
            return
        
        PasswordManager().add_password(password)
        logger.success(f"密码: {password} 已添加")
    
    def del_password_menu(self):
        passwords = PasswordManager().read_password()
        if not len(passwords):
            logger.warning("密码文件中没有密码。")
            return
        
        print("请选择要删除的密码:\n" + "\n".join([f'{i}: {password}' for i, password in enumerate(passwords)]) + "\n\nq: 退出")
        choice = input("请输入选项: ")
        if choice == "q":
            return
        
        if not choice.isdigit():
            logger.warning(f"无效选项: {choice}")
            self.del_password_menu()
        elif int(choice) < 0 or int(choice) >= len(passwords):
            logger.warning(f"无效选项: {choice}")
            self.del_password_menu()
        elif list(passwords.keys())[int(choice)] not in passwords:
            logger.warning(f"密码: {list(passwords.keys())[int(choice)]} 不在文件中。")
            self.del_password_menu()
        else:
            password_to_delete = list(passwords.keys())[int(choice)]
            PasswordManager().del_password(password_to_delete)
            logger.success(f"密码: {password_to_delete} 已删除")
    
    def cls_password_menu(self):
        passwords = PasswordManager().read_password()
        for password in passwords:
            PasswordManager().del_password(password)
        logger.success("所有密码已清空")
    
    def show_password_menu(self):
        passwords = PasswordManager().read_password()
        if not len(passwords):
            logger.warning("密码文件中没有密码。")
            return
        
        print("当前密码列表:\n" + "\n".join([f'{i}: {password}' for i, password in enumerate(passwords)]))
    
    def quit(self):
        sys.exit(0)