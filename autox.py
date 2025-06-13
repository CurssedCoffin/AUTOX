from managers.console_manager import ConsoleManager
from managers.password_manager import PasswordManager
from managers.logger_manager import logger, console

import rich
import rich.progress
from natsort import natsorted

import os
import sys
import atexit
import shutil
import tempfile
import traceback
import subprocess
from glob import glob

VERBOSE = False

class AutoX:
    def __init__(self, root: str, min_size: int = 1024 * 1024 * 50) -> None:
        self.root = root
        self.min_size = min_size
        if sys.platform == "win32":
            self.bin_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin", "windows", "7z.exe")
        else:
            logger.critical(f"不支持的操作系统平台: {sys.platform}")
            sys.exit(1)

        self.bar = rich.progress.Progress(
            *rich.progress.Progress.get_default_columns(),
            rich.progress.MofNCompleteColumn(),
            rich.progress.TimeElapsedColumn(),
            console=console
        )
        self.bar.start()

        self.return_code_status = {
            -2: "密码错误",
            -1: "子进程未知错误",
            0: "无错误",
            1: "警告 (非致命错误)。例如，一个或多个文件被其他应用程序锁定，因此未被压缩。",
            2: "致命错误",
            7: "命令行错误",
            8: "内存不足",
            255: "用户已停止该过程",
        }
        self.is_code_success = lambda code: code in [0, 1]

        paths_by_name = self.determine_zipfile(self.root)
        self.run(paths_by_name)
    
    # 获取压缩、分卷压缩的逻辑
    def determine_zipfile(self, root):
        black_lists = [
            ".exe",
            ".dll",
            ".lib",
        ]
        paths_by_name = {} # {basename: [path, ...], ...}

        paths = natsorted([x for x in glob(os.path.join(root, "*")) if os.path.isfile(x)])
        for path in paths:
            # 跳过黑名单
            if any(path.endswith(ext) for ext in black_lists):
                continue
            
            # 跳过小文件
            if os.path.getsize(path) < self.min_size:
                continue
            
            filename = os.path.basename(path)
            parts = filename.rsplit('.', 2) # 兼容分卷压缩文件
            if len(parts) > 1 and (parts[-1].isdigit() or parts[-2].endswith('part')):
                basename = parts[0]
            else:
                basename, _ = os.path.splitext(filename)
            
            if basename not in paths_by_name:
                paths_by_name[basename] = []
            paths_by_name[basename].append(path)
        
        # # 按文件名排序
        # for name in paths_by_name:
        #     paths_by_name[name] = natsorted(paths_by_name[name])
        
        return paths_by_name

    # 7z子进程解压压缩包
    def extract_zipfile(self, task, zipfile_path, dst_root, password = None):
        if VERBOSE: logger.info(f"正在解压 {zipfile_path} 到 {dst_root}")

        # 7z 命令
        command = [self.bin_path, 'x', '-bsp1', '-aoa', f'-o{dst_root}'] # bsp1: bsp to 1 to switch to view the progress | aoa: Overwrite All existing files without prompt.
        if password: # if with password
            command += [f'-p{password}']
        command += [f'--', f'{zipfile_path}']

        code = None # 进程返回码
        process = None # 进程
        pipe = None # 管道
        try:
            password_invalid = False # 密码是否无效
            able_to_progress = False # 是否能获取进度

            # 启动进程
            pipe = tempfile.SpooledTemporaryFile()
            process = subprocess.Popen(
                command,
                stdout=pipe,
                stderr=pipe,
                shell=False,
                cwd=os.path.dirname(zipfile_path)
            )

            # 读取进程输出
            where = 0
            while process.poll() is None:
                pipe.seek(where)
                lines = pipe.readlines()
                cat_lines = b"\n".join(lines)
                where_offset = len(cat_lines)
                where += where_offset
                if VERBOSE:
                    for line in lines:
                        try: line = line.decode("utf-8").strip()
                        except: pass
                        finally: logger.debug(line)
                
                # 错误密码
                if b"Enter password" in cat_lines or b"Wrong password" in cat_lines:
                    password_invalid = True
                    break

                # 更新进度
                try:
                    if b"Path =" in cat_lines: able_to_progress = True
                    if b"%" in cat_lines and able_to_progress:
                        percent = int(cat_lines.split(b"%")[-2].split(b"\n")[-1].strip().decode())
                        if percent: self.bar.advance(task, percent - last_progress)
                        last_progress = percent
                except:
                    pass

            # 错误密码，立即终止进程
            if password_invalid:
                code = -2
                process.kill()
                process.wait()
                pipe.close()
        
        # 未知错误
        except Exception:
            if VERBOSE: logger.error(f"\n命令执行失败: {command}\n错误信息: \n{traceback.format_exc()}")
        
        # 清理回收
        finally:
            if process is not None and code is None: # 进程正常结束
                code = process.returncode # 获取进程返回码
            else:
                code = -1 if code is None else code # 进程异常结束
            
            if process.poll() is None: # 等待进程结束
                process.kill()
                process.wait()
            
            if pipe is not None:
                pipe.close()

        return code

    # 移动解压成功的压缩包到指定目录，或不移动
    def move_zipfile(self, paths, dst_root, keep = False):
        os.makedirs(dst_root, exist_ok=True)
        for path in paths:
            if not keep:
                shutil.move(path, dst_root)

    # 当存在嵌套路径时，将嵌套路径移动到上一层
    def clean_dst_root(self, dst_root):
        sub_paths = natsorted(glob(os.path.join(dst_root, "*")))
        if len(sub_paths) == 1 and os.path.isdir(sub_paths[0]):
            sub_path = sub_paths[0]
            shutil.move(sub_path, dst_root + "_temp")
            shutil.rmtree(dst_root)
            os.rename(dst_root + "_temp", dst_root)

    # 解压压缩包的逻辑, 包括密码尝试、解压、移动压缩包、清理路径、尝试移动单文件结果
    def run_extract(self, name, paths, zipfile_path, dst_root, move_root, sub_path):
        task = self.bar.add_task("解压中")
        success = False

        # 尝试密码
        for password in [None] + list(PasswordManager().read_password()):
            code = self.extract_zipfile(task, zipfile_path, dst_root, password)
            
            # 成功解压
            if self.is_code_success(code):
                self.bar.remove_task(task)
                if password is not None:
                    PasswordManager().update_password(password, 1)

                # 移动压缩包到缓存目录
                self.move_zipfile(paths, move_root, keep = bool(sub_path)) # 如果是递归一次解压，则不进行移动，保留原来的压缩包，防止误删

                # 解决嵌套路径
                self.clean_dst_root(dst_root)

                # 如果解压后的目录还有可解压的文件，也一并解压
                if sub_path is None:
                    paths_by_name = self.determine_zipfile(dst_root)
                    self.run(paths_by_name, sub_path = dst_root)
                
                success = True
                break
            
            # 解压失败
            else:
                if VERBOSE:
                    if code in self.return_code_status:
                        logger.error(f"使用密码 {password} 解压 {name} 失败: {self.return_code_status[code]}")
                    else:
                        logger.error(f"使用密码 {password} 解压 {name} 失败: 未知错误，代码 {code}。")
                shutil.rmtree(dst_root, ignore_errors=False)
        
        # 回收进度条
        if not success:
            self.bar.remove_task(task)

        return success

    # 解压主逻辑
    def run(self, paths_by_name, sub_path = None):
        """sub_path: 如果调用方来自run_extract, 则会带上该参数，防止递归解压"""
        
        num = 0
        for name, paths in self.bar.track(paths_by_name.items(), description="总进度", total=len(paths_by_name)) if not sub_path else paths_by_name.items():
            zipfile_path = paths[0]
            dst_root = os.path.join(self.root if not sub_path else sub_path, name)
            move_root = os.path.join(self.root if not sub_path else sub_path, "_done")

            # 进行解压
            success = self.run_extract(name, paths, zipfile_path, dst_root, move_root, sub_path)
            if success:
                num += len(paths)
        
        if sub_path is None:
            num_all = sum(len(v) for v in paths_by_name.values())
            msg = f"已解压 {num}/{num_all} 个文件"
            if num == num_all:
                logger.success(msg)
            elif num == 0:
                logger.error(msg)
            else:
                logger.warning(msg)
        
def run_autox(root):
    autox = AutoX(root)
    autox.bar.stop()
    
def run_console():
    ConsoleManager()

if __name__ == "__main__":
    atexit.register(lambda: input("按回车键退出..."))
    args = sys.argv[1:]

    try:
        # 如果传入参数，则运行autox
        if len(args):
            root = " ".join(args)
            run_autox(root)
        # 否则运行console
        else:
            run_console()
    
    except Exception as e:
        logger.critical(traceback.format_exc())