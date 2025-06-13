from managers.logger_manager import logger

import os
import sys
import json

class PasswordManager:
    """密码文件: {密码: 计数器, ...}"""
    def __init__(self) -> None:
        self.password_path = os.path.join(os.path.dirname(__file__), "password.json") if not hasattr(sys, "frozen") else os.path.join(os.path.dirname(sys.executable), "password.json")
    
    # 读取排序后的密码
    def read_password(self):
        return self.sort_password(self.read_json(self.password_path))
    
    # 添加密码到文件
    def add_password(self, password: str) -> None:
        password_info = self.read_json(self.password_path)
        if password not in password_info:
            password_info[password] = 0
            self.write_json(self.password_path, password_info)
        else:
            logger.warning(f"密码: {password} 已存在于文件中。")
    
    # 从文件中删除密码
    def del_password(self, password: str) -> None:
        password_info = self.read_json(self.password_path)
        if password not in password_info:
            logger.warning(f"密码: {password} 不在文件中。")
        else:
            del password_info[password]
            self.write_json(self.password_path, password_info)

    # 从文件更新密码计数器，+1 或 -1
    def update_password(self, password: str, times: int) -> None:
        password_info = self.read_json(self.password_path)
        if password not in password_info:
            logger.warning(f"密码: {password} 不在文件中。")
        else:
            password_info[password] += times
            self.write_json(self.password_path, password_info)
    
    # 按计数器对密码进行排序
    def sort_password(self, data: dict):
        return dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    
    @classmethod
    # 从 json 文件读取数据
    def read_json(cls, json_path: str) -> dict:
        if not os.path.exists(json_path):
            cls.write_json(json_path, {})
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    
    @classmethod
    # 将数据写入 json 文件
    def write_json(cls, json_path: str, json_data: dict) -> None:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)