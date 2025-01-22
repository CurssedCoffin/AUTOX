import os
import json

password_json_path = os.path.join(os.path.dirname(__file__), "cache", "password.json")
os.makedirs(os.path.dirname(password_json_path), exist_ok=True)
password_txt_path = os.path.join(os.path.dirname(__file__), "password.txt")

def sort_dict(data: dict):
    return dict(sorted(data.items(), key=lambda x: x[1], reverse=True))

def save_passwords(password_json):
    password_json = sort_dict(password_json)
    if "" in password_json:
        password_json.pop("")
    with open(password_json_path, "w", encoding="utf-8") as f:
        json.dump(password_json, f, ensure_ascii=False, indent=4)

def get_passwords():
    # read password from txt
    passwords = []
    if os.path.exists(password_txt_path):
        with open(password_txt_path, "r", encoding="utf-8") as f:
            passwords.extend([line.strip() for line in f.readlines() if line.strip() != ""])

    # create password json if not exists
    if not os.path.exists(password_json_path):
        password_json = {password: 0 for password in passwords}
        save_passwords(password_json)
    # read password from json
    else:
        with open(password_json_path, "r", encoding="utf-8") as f:
            password_json = json.load(f)
        for password in passwords:
            if password not in password_json:
                password_json[password] = 0

    # update password json
    password_json = sort_dict(password_json)
    password_json[""] = 0
    save_passwords(password_json)
    return password_json

if __name__ == "__main__":
    passwords = get_passwords()
    print(passwords)
