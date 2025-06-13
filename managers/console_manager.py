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
            "q": {"msg": "quit", "func": self.quit},
            "1": {"msg": "install", "func": self.install},
            "2": {"msg": "uninstall", "func": self.uninstall},
            "3": {"msg": "add password", "func": self.add_password_menu},
            "4": {"msg": "delete password", "func": self.del_password_menu},
            "5": {"msg": "show password", "func": self.show_password_menu},
            "6": {"msg": "clear password", "func": self.cls_password_menu},
        }
        print("=" * 30 + "\n" + "\n".join([f'{k}: {v["msg"]}' for k, v in key_map.items()]))
        key = input("Enter choice: ")
        os.system("cls" if sys.platform == "win32" else "clear")
        
        if key not in key_map:
            self.main_menu()
        else:
            key_map[key]["func"]()
            self.main_menu()

    def install(self):
        success = InstallManager().install()
        if success:
            logger.success("Install success")
        else:
            logger.error("Install failed")
    
    def uninstall(self):
        success = InstallManager().uninstall()
        if success:
            logger.success("Uninstall success")
        else:
            logger.error("Uninstall failed")

    def add_password_menu(self):
        passwords = PasswordManager().read_password()
        password = input("Enter password: ")

        if password == "":
            logger.warning("Password is empty.")
            return
        elif password in passwords:
            logger.warning(f"Password: {password} already in file.")
            return
        
        PasswordManager().add_password(password)
        logger.success(f"Password: {password} added")
    
    def del_password_menu(self):
        passwords = PasswordManager().read_password()
        if not len(passwords):
            logger.warning("No password in file.")
            return
        
        print("Choices:\n" + "\n".join([f'{i}: {password}' for i, password in enumerate(passwords)]) + "\n\nq: quit")
        choice = input("Enter choice: ")
        if choice == "q":
            return
        
        if not choice.isdigit():
            logger.warning(f"Invalid choice: {choice}")
            self.del_password_menu()
        elif int(choice) < 0 or int(choice) >= len(passwords):
            logger.warning(f"Invalid choice: {choice}")
            self.del_password_menu()
        elif list(passwords.keys())[int(choice)] not in passwords:
            logger.warning(f"Password: {list(passwords.keys())[int(choice)]} not in file.")
            self.del_password_menu()
        else:
            PasswordManager().del_password(list(passwords.keys())[int(choice)])
            logger.success(f"Password: {choice} deleted")
    
    def cls_password_menu(self):
        passwords = PasswordManager().read_password()
        for password in passwords:
            PasswordManager().del_password(password)
        logger.success("Password cleared")
    
    def show_password_menu(self):
        passwords = PasswordManager().read_password()
        if not len(passwords):
            logger.warning("No password in file.")
            return
        
        print("Choices:\n" + "\n".join([f'{i}: {password}' for i, password in enumerate(passwords)]))
    
    def quit(self):
        sys.exit(0)
