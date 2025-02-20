import os
import sys
import shutil
import tempfile
import traceback
import subprocess
from glob import glob

import rich
import rich.progress
from rich.logging import RichHandler
from loguru import logger
from natsort import natsorted

from AUTOX.password import get_passwords, save_passwords

# define logger
logger.configure(handlers=[{"sink":RichHandler(), "format":"{message}"}])

# check platform
if sys.platform == "win32":
    BIN_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin", "windows", "7z.exe")
else:
    raise NotImplementedError(f"Platform {sys.platform} not supported")

# define progress bar
bar = rich.progress.Progress(
    *rich.progress.Progress.get_default_columns(),
    rich.progress.MofNCompleteColumn(),
    rich.progress.TimeElapsedColumn(),
)
bar.start()

# load password
passwords = get_passwords()

def sort_root_by_name(root):
    """
    Get all files in the root directory and sort them by name
    """
    paths = [x for x in glob(os.path.join(root, "*")) if os.path.isfile(x)]
    paths_by_name = {}

    for path in paths:
        if os.path.getsize(path) <= 10 * 1024 * 1024: continue # skip small files like 10M
        if path.endswith(".exe"): continue # skip large exe files
        name = ".".join(os.path.splitext(os.path.basename(path))[:-1]) # normal is like a.zip
        if len(name.split(".")) > 1 and "part" in name.split(".")[-1]: # in case of a.part1.rar
            name = ".".join(name.split(".")[:-1])
        if name not in paths_by_name:
            paths_by_name[name] = []
        paths_by_name[name].append(path)
    return paths_by_name

def sort_root_by_size(root, default_size = 1024 * 1024 * 100):
    """
    Get paths that larger than default_size, default is 100M
    """
    paths = [x for x in glob(os.path.join(root, "*")) if os.path.isfile(x) and os.path.getsize(x) >= default_size]
    paths_by_name = {}

    for path in paths:
        if path.endswith(".exe"): continue # skip large exe files
        name = name = ".".join(os.path.splitext(os.path.basename(path))[:-1]) # normal is like a.zip
        if len(name.split(".")) > 1 and "part" in name.split(".")[-1]: # in case of a.part1.rar
            name = ".".join(name.split(".")[:-1])
        if name not in paths_by_name:
            paths_by_name[name] = []
        paths_by_name[name].append(path)
    return paths_by_name

def get_top_level_path(subpaths):
    """
    Return the sorted first path in the subpaths
    """
    if len(subpaths) == 1:
        return subpaths[0]
    else:
        return natsorted(subpaths)[0]

def collect_files(dst_root, basename):
    """
    When the extraction is completed, collect all the files in the destination root
    """
    sub_paths = os.listdir(dst_root)
    if len(sub_paths) == 1:
        sub_path = os.path.join(dst_root, sub_paths[0])
        move_root = os.path.join(os.path.abspath(os.path.dirname(dst_root)), basename)

        if os.path.basename(sub_path) == os.path.basename(dst_root) or os.path.basename(move_root) == os.path.basename(dst_root):
            os.rename(dst_root, dst_root + "_temp")
            sub_path = os.path.join(dst_root + "_temp", os.path.relpath(sub_path, dst_root))
            shutil.move(sub_path, move_root)
            shutil.rmtree(dst_root + "_temp")
        else:
            shutil.move(sub_path, move_root)
            shutil.rmtree(dst_root)
        return move_root
    else:
        return dst_root

def collect_zipfiles(subpaths):
    """
    Move zip files to _done folder
    """
    for path in subpaths:
        dst_path = os.path.join(os.path.abspath(os.path.dirname(path)), "_done", os.path.basename(path))
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        os.rename(path, dst_path)

def run_extract(basename, subpaths, del_after_extract = False, verbose = True):
    """
    Do the extraction
    """
    # get the top level path and destination root
    path = get_top_level_path(subpaths)
    dst_root = os.path.join(os.path.abspath(os.path.dirname(path)), basename)
    os.makedirs(dst_root, exist_ok=True)
    if verbose: logger.info(f"Extracting {path} to {dst_root}")

    # run the extraction
    is_password_invalid = False # for the case that all password are invalid
    for password in passwords:
        if password == "": # without password
            command = [BIN_PATH, 'x', '-aoa', f'-o{dst_root}', f'--', f'{path}']
        else: # with password
            command = [BIN_PATH, 'x', '-aoa', f'-o{dst_root}', f'-p{password}', f'--', f'{path}']
        res = None
        code = None
        success = False
        output = False
        # if verbose: logger.warning(" ".join(command))

        try:
            pipe = tempfile.SpooledTemporaryFile()
            res = subprocess.Popen(command, stdout=pipe, stderr=pipe, shell=True, cwd=os.path.dirname(path))
            
            where = 0
            while res.poll() is None:
                pipe.seek(where)
                lines = pipe.readlines()
                where_offset = len(b"\n".join(lines))
                where += where_offset
                if output:
                    for line in lines:
                        try: line = line.decode("utf-8").strip()
                        except: pass
                        finally: print(line)
                if b"Enter password" in b"\n".join(lines):
                    is_password_invalid = True
                    break
            
            if is_password_invalid:
                code = -2
                res.kill()

        except Exception:
            if verbose: logger.error(f"\nCommand execution failed: {command}\nError message: \n{traceback.format_exc()}")
        finally:
            if res is not None and code is None:
                code = res.returncode
                if code in [0, 1]: success = True
            else:
                code = -1 if code is None else code

        if success:
            if del_after_extract:
                for path in subpaths:
                    os.remove(path)
            else:
                collect_zipfiles(subpaths)
            dst_root = collect_files(dst_root, basename=os.path.splitext(os.path.basename(path))[0])

            passwords[password] += 1
            save_passwords(passwords)
            if verbose: logger.success(f"Extraction completed successfully.")
            return True, dst_root

    if not success:
        """
            -2  Password is invalid
            -1  Unknown error with subprocess
            0	No error
            1	Warning (Non fatal error(s)). For example, one or more files were locked by some other application, so they were not compressed.
            2	Fatal error
            7	Command line error
            8	Not enough memory for operation
            255	User stopped the process
        """
        if verbose:
            if code == -2:
                logger.error(f"Extraction failed with wrong password")
            elif code == -1:
                logger.error(f"Extraction failed with unknown error with code {code}")
            elif code == 1:
                logger.warning(f"Extraction completed with warnings with code {code}")
            elif code == 2:
                logger.error(f"Extraction failed with fatal error with code {code}")
            elif code == 7:
                logger.error(f"Extraction failed with command line error with code {code}")
            elif code == 8:
                logger.error(f"Extraction failed with not enough memory for operation with code {code}")
            else:
                logger.critical(f"Extraction failed with unknown error with code {code}")
        
        shutil.rmtree(dst_root)
        return False, None

def run(root):
    paths = sort_root_by_name(root)

    for basename, subpaths in bar.track(paths.items(), description="Extracting", total=len(paths)):
        try:
            status, dst_root = run_extract(basename, subpaths)
            if status:
                for basename, subpaths in sort_root_by_size(dst_root).items():
                    run_extract(basename, subpaths, del_after_extract=True, verbose=False)
        except Exception as e:
            logger.error(f"Extraction failed with error: {e}")

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        root = " ".join(args)
    else:
        root = args[0]

    try:
        run(root)
    except Exception as e:
        logger.critical(traceback.format_exc())

    input("Press Enter to exit...")
