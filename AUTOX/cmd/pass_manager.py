import os
import click

pass_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "password.txt")
if not os.path.exists(pass_path):
    with open(pass_path, "w", encoding="utf-8") as f: pass

def show_pass_path():
    print(pass_path)

def show_pass():
    with open(pass_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            print(line.strip())

@click.command()
@click.argument("password")
def add_pass(password):
    with open(pass_path, "a", encoding="utf-8") as f:
        f.write(password + "\n")

def empty_pass():
    with open(pass_path, "w", encoding="utf-8") as f:
        pass

if __name__ == "__main__":
    show_pass_path()

