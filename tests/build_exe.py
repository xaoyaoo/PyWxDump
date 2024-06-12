# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         gen_exe.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/11/10
# -------------------------------------------------------------------------------
import shutil
import site
import os
import base64
import pywxdump

__version__ = pywxdump.__version__
ma_version = __version__.split(".")[0]
mi_version = __version__.split(".")[1]
pa_version = __version__.split(".")[2]

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')


def base64_to_image(base64_string, image_path):
    with open(image_path, "wb") as image_file:
        decoded_string = base64.b64decode(base64_string)
        image_file.write(decoded_string)


code = """
# -*- coding:utf-8 -*-
from pywxdump.cli import console_run
console_run()
"""
spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['tmp.py'],
             pathex=[],
             binaries=[],
             datas=[(r'{root_path}\\version_list.json', 'pywxdump'),
              (r'{root_path}/ui/templates/chat.html', 'pywxdump/ui/templates'), 
             (r'{root_path}/ui/templates/index.html', 'pywxdump/ui/templates'),
            {datas_741258}
            ],
             hiddenimports={hidden_imports},
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

version_info = {{
          'FileDescription': 'PyWxDump from https://github.com/xaoyaoo/PyWxDump',
          'OriginalFilename': 'None',
          'ProductVersion': '{version}.0',  # 版本号
          'FileVersion': '{version}.0',
          'InternalName': 'wxdump'
}}
a.version = version_info


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='wxdump',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,  # 启用压缩
          console=True,  # 使用控制台 
          disable_windowed_traceback=True,  # 不禁用堆栈跟踪
          argv_emulation=False, # 不模拟命令行参数
          target_arch=None,  # 自动检测目标 CPU 架构
          codesign_identity=None,  # 不签名应用程序
          entitlements_file=None,  # 不使用 entitlements 文件
          onefile=True,  # 生成单个可执行文件
          icon="icon.ico",
          version='wxdump_version_info.txt'
          )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='wxdump')
'''

wxdump_version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({ma_version}, {mi_version}, {pa_version}, 0),
    prodvers=({ma_version}, {mi_version}, {pa_version}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904b0',
        [StringStruct('CompanyName', 'PyWxDump'),
        StringStruct('FileDescription', 'PyWxDump from https://github.com/xaoyaoo/PyWxDump'),
        StringStruct('FileVersion', '{__version__}'),
        StringStruct('InternalName', 'wxdump.exe'),
        StringStruct('LegalCopyright', 'Copyright (C) http://github.com/xaoyaoo/PyWxDump. All rights reserved'),
        StringStruct('OriginalFilename', 'wxdump.exe'),
        StringStruct('ProductName', 'wxdump'),
        StringStruct('ProductVersion', '{__version__}'),
        StringStruct('SquirrelAwareVersion', '1')])
      ]), 
    VarFileInfo([VarStruct('Translation',  [2052, 1200])])
  ]
)
"""


# 创建文件夹
os.makedirs("dist", exist_ok=True)
# 将代码写入文件
with open("dist/tmp.py", "w", encoding="utf-8") as f:
    f.write(code.strip())

current_path = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(current_path, "favicon.ico"), "dist/icon.ico")  # 复制图标
# base64_to_image(ico_base64, "dist/icon.png")  # 将 base64 转换为图片
with open("dist/wxdump_version_info.txt", "w", encoding="utf-8") as f:
    f.write(wxdump_version_info.strip())


# 获取安装包的路径
package_path = site.getsitepackages()
if package_path:
    package_path = package_path[1]  # 假设取第一个安装包的路径

    current_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在路径
    require_path = os.path.join(os.path.dirname(current_path), "requirements.txt")  # requirements.txt 路径
    with open(require_path, "r", encoding="utf-8") as f:
        hidden_imports = f.read().splitlines()
    hidden_imports = [i.replace('-','_') for i in hidden_imports if i not in ["setuptools", "wheel"]]  # 去掉setuptools、wheel

    # 获取 ui 文件夹下的所有文件 用于打包
    root_path = os.path.join(package_path, 'pywxdump')
    datas_741258 = []
    for root, dirs, files in os.walk(os.path.join(root_path, "ui")):
        for file in files:
            file_path = os.path.join(root, file)
            datas_741258.append(f'''(r'{file_path}', r'{os.path.dirname(file_path.replace(package_path, "")[1:])}' )''')
    datas_741258 = ",\n".join(datas_741258)

    # 获取 wx_info/tools 文件夹下的所有文件 用于打包
    for root, dirs, files in os.walk(os.path.join(root_path, "wx_info", "tools")):
        for file in files:
            file_path = os.path.join(root, file)
            datas_741258 += f''',\n(r'{file_path}', r'{os.path.dirname(file_path.replace(package_path, "")[1:])}' )'''


    # print(datas_741258)
    # 生成 spec 文件
    spec_content = spec_content.format(root_path=root_path, hidden_imports=hidden_imports, datas_741258=datas_741258, version=__version__)
    spec_file = os.path.join("dist", "pywxdump.spec")
    with open(spec_file, 'w', encoding="utf-8") as f:
        f.write(spec_content.strip())

    # 执行打包命令
    cmd = f'pyinstaller --clean --distpath=dist {spec_file}'
    print(cmd)
    # os.system(cmd)

else:
    print("未找到安装包路径")
