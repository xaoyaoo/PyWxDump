# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         gen_exe.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/11/10
# -------------------------------------------------------------------------------
import site
import os

code = """from pywxdump.command import console_run;console_run()"""

# 创建文件夹
os.makedirs("dist", exist_ok=True)
# 将代码写入文件
with open("dist/tmp.py", "w", encoding="utf-8") as f:
    f.write(code)

# 获取安装包的路径
package_path = site.getsitepackages()
if package_path:
    package_path = package_path[1]  # 假设取第一个安装包的路径
    version_list_path = os.path.join(package_path,'pywxdump', 'version_list.json')

    # 执行打包命令
    cmd = f'pyinstaller --onefile --clean --add-data "{version_list_path};pywxdump" dist/tmp.py'
    print(cmd)
    os.system(cmd)

else:
    print("未找到安装包路径")
