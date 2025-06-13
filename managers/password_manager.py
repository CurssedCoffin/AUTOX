from managers.logger_manager import logger

import os
import sys
import json

class PasswordManager:
    """Password file: {password: counter, ...}"""
    def __init__(self) -> None:
        self.password_path = os.path.join(os.path.dirname(__file__), "password.json") if not hasattr(sys, "frozen") else os.path.join(os.path.dirname(sys.executable), "password.json")
    
    # read sorted passwords
    def read_password(self):
        return self.sort_password(self.read_json(self.password_path))
    
    # add password to file
    def add_password(self, password: str) -> None:
        password_info = self.read_json(self.password_path)
        if password not in password_info:
            password_info[password] = 0
            self.write_json(self.password_path, password_info)
        else:
            logger.warning(f"Password: {password} already in file.")
    
    # delete password counter from file
    def del_password(self, password: str) -> None:
        password_info = self.read_json(self.password_path)
        if password not in password_info:
            logger.warning(f"Password: {password} not in file.")
        else:
            del password_info[password]
            self.write_json(self.password_path, password_info)

    # update password counter from file by 1 or -1
    def update_password(self, password: str, times: int) -> None:
        password_info = self.read_json(self.password_path)
        if password not in password_info:
            logger.warning(f"Password: {password} not in file.")
        else:
            password_info[password] += times
            self.write_json(self.password_path, password_info)
    
    # sort passwords by counter
    def sort_password(self, data: dict):
        return dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    
    @classmethod
    # read data from json file
    def read_json(self, json_path: str) -> dict:
        if not os.path.exists(json_path):
            self.write_json(json_path, {})
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    
    @classmethod
    # write data to json file
    def write_json(self, json_path: str, json_data: dict) -> None:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
