# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         release_new_version.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/07/02
# -------------------------------------------------------------------------------
import os
import time

# 获取当前文件所在目录
current_path = os.path.dirname(os.path.abspath(__file__))
PyWxDump_path = os.path.dirname(current_path)
os.chdir(PyWxDump_path)
version_path = os.path.join(PyWxDump_path, "pywxdump", "__init__.py")

# 读取版本号 pywxdump/__init__.py 中的 __version__
with open(version_path, "r", encoding="utf-8") as f:
    for line in f.readlines():
        if line.startswith("__version__"):
            version = line.split("=")[-1].strip().strip("\"'")
            break
    else:
        raise RuntimeError("version not found")

print(f"{PyWxDump_path=}")
print(f"{version=}")
os.system(f"git tag -a v{version} -m 'v{version}'")
time.sleep(1)
os.system(f"git push origin v{version}")

print("发布成功 master\n")

pywxdumpweb_path = os.path.join(os.path.dirname(PyWxDump_path), "wxdump_web")
os.chdir(pywxdumpweb_path)
print(f"{pywxdumpweb_path=}")
print(f"{version=}")
os.system(f"git tag -a v{version} -m 'v{version}'")
time.sleep(1)
os.system(f"git push origin v{version}")
print("发布成功 wxdump_web")
