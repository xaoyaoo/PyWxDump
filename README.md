# <center>PyWxDump</center>

[![Python](https://img.shields.io/badge/Python-3-blue.svg)](https://www.python.org/)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/xaoyaoo/pywxdump)](https://github.com/xaoyaoo/PyWxDump)
[![GitHub all releases](https://img.shields.io/github/downloads/xaoyaoo/pywxdump/total)](https://github.com/xaoyaoo/PyWxDump)
[![GitHub stars](https://img.shields.io/github/stars/xaoyaoo/PyWxDump.svg)](https://github.com/xaoyaoo/PyWxDump)
[![GitHub forks](https://img.shields.io/github/forks/xaoyaoo/PyWxDump.svg)](https://github.com/xaoyaoo/PyWxDump/fork)
[![GitHub issues](https://img.shields.io/github/issues/xaoyaoo/PyWxDump)](https://github.com/xaoyaoo/PyWxDump/issues)

[![PyPI](https://img.shields.io/pypi/v/pywxdump)](https://pypi.org/project/pywxdump/)
[![Wheel](https://img.shields.io/pypi/wheel/pywxdump)](https://pypi.org/project/pywxdump/)
[![PyPI-Downloads](https://img.shields.io/pypi/dm/pywxdump)](https://pypistats.org/packages/pywxdump)
[![GitHub license](https://img.shields.io/pypi/l/pywxdump)](https://github.com/xaoyaoo/PyWxDump/blob/master/LICENSE)
[![Publish](https://github.com/xaoyaoo/PyWxDump/actions/workflows/publish.yml/badge.svg)](https://github.com/xaoyaoo/PyWxDump/actions/workflows/publish.yml)

<details>
<summary><strong>更新日志(点击展开)：</strong></summary>

* 2023.11.15 添加test文件，添加自动构建可执行文件的脚本
* 2023.11.15 [v2.2.5变化较大]重构解密脚本的返回值，重构命令行参数
* 2023.11.15 修复无法获取wxid的bug
* 2023.11.14 修复部分bug
* 2023.11.11 添加聊天记录解析，查看工具,修复部分bug
* 2023.11.10 修复wxdump wx_db命令行参数错误 [#19](https://github.com/xaoyaoo/PyWxDump/issues/19)
* 2023.11.08 增加3.9.8.15版本支持
* 2023.10.31 修复3.9.2.*版本无法正常运行
* 2023.10.28 添加自动发布到pypi的github action
* 2023.10.28 修复3.9.5.91版本的偏移
* 2023.10.24 add auto get bias addr ,not need input key or wx folder path.
* 2023.10.17 add LICENSE
* 2023.10.16 添加"3.9.7.15"版本的偏移[#12](https://github.com/xaoyaoo/PyWxDump/issues/12)
  ,感谢@[GentlemanII](https://github.com/GentlemanII)
* 2023.10.15 将整个项目作为包安装，增加命令行统一操作
* 2023.10.14 整体重构项目，优化代码，增加命令行统一操作
* 2023.10.11 添加"3.9.5.81"版本的偏移[#10](https://github.com/xaoyaoo/PyWxDump/issues/10)
  ,感谢@[sv3nbeast](https://github.com/sv3nbeast)
* 2023.10.09 获取key基址偏移可以根据微信文件夹获取，不需要输入key
* 2023.10.09 优化代码，删减没必要代码，重新修改获取基址代码，加快运行速度（需要安装新的库 pymem）
* 2023.10.07 修改获取基址内存搜索方式，防止进入死循环
* 2023.10.07 增加了3.9.7.29版本的偏移地址
* 2023.10.06 增加命令行解密数据库
* 2023.09.28 增加了数据库部分解析
* 2023.09.15 增加了3.9.7.25版本的偏移地址

</details>

# 一、项目介绍

## 1. 项目简介

PyWxDump可用于：获取用户个人信息(昵称/账号/手机/邮箱/数据库密钥(用来解密聊天记录))；数据库读取、解密脚本；聊天记录查看工具。

支持多账户信息获取，支持所有微信版本。

* <strong><big>
  超级想要star，走过路过，帮忙点个[![Star](https://img.shields.io/github/stars/xaoyaoo/PyWxDump.svg?style=social&label=Star)](https://github.com/xaoyaoo/PyWxDump/)
  呗，谢谢啦~</big></strong>

## 2. 功能介绍

* （1）获取微信昵称、微信账号、微信手机号、微信邮箱、微信KEY的基址偏移
* （2）获取微信的微信昵称、微信账号、微信手机号、微信邮箱、微信KEY、微信原始ID（wxid_******）
* （3）获取微信文件夹路径
* （4）支持查看聊天记录查看
* （5）根据key解密微信数据库
* （6）提供数据库部分字段说明
* （7）支持微信多开场景，获取多用户信息等
* （8）微信需要登录状态才能获取数据库密钥

**版本差异**

1. 版本 < 3.7.0.30 只运行不登录能获取个人信息，登录后可以获取数据库密钥
2. 版本 > 3.7.0.30 只运行不登录不能获取个人信息，登录后都能获取

**利用场景**

1. 钓鱼攻击(通过钓鱼控到的机器通常都是登录状态)
2. 渗透到运维机器(有些运维机器会日常登录自己的微信)
3. 某些工作需要取证(数据库需要拷贝到本地)
4. 自行备份(日常备份自己留存)
5. 等等...............

## 3. 项目结构

<details>
<summary>点击展开</summary>

```
PyWxDump
├─ pywxdump                        # 项目代码,存放各个模块
│  ├─ analyse                     # 解析数据库
│  │  └─ parse.py                     # 解析数据库脚本，可以解析语音、图片、聊天记录等
│  ├─ bias_addr                   # 获取偏移地址
│  │  └─ get_bias_addr.py             # 获取偏移地址脚本
│  ├─ decrypted                   # 解密数据库
│  │  ├─ decrypt.py                   # 解密数据库脚本
│  │  └─ get_wx_decrypted_db.py       # 直接读取当前登录微信的数据库，解密后保存到当前目录下的decrypted文件夹中
│  ├─ wx_info                     # 获取微信基本信息
│  │  ├─ get_wx_info.py               # 获取微信基本信息脚本
│  │  └─ get_wx_db.py                 # 获取本地所有的微信相关数据库
│  ├─ show_records                # 显示聊天记录
│  │  ├─ main_window.py               # 显示聊天记录的窗口
│  │  └─ templates                    # 显示聊天记录的html模板
│  ├─ command.py                  # 命令行入口
│  └─ version_list.json           # 微信版本列表 (十进制)按顺序代表：微信昵称、微信账号、微信手机号、微信邮箱（默认0）、微信KEY、微信原始ID（wxid_******）
├─ doc                        # 项目文档
│  ├─ python1.0_README.md         # python1.0版本的README
│  ├─ wx数据库简述.md               # wx数据库简述
│  └─ CE获取基址.md                 # CE获取基址
├─ README.md              
├─ setup.py                   # 安装脚本
└─ requirements.txt
```

</details>

## 4. 其他

[PyWxDump](https://github.com/xaoyaoo/PyWxDump)是[SharpWxDump](https://github.com/AdminTest0/SharpWxDump)
的经过重构python语言版本，同时添加了一些新的功能。

* 如发现[version_list.json](pywxdump/version_list.json)缺失或错误,
  请提交[issues](https://github.com/xaoyaoo/PyWxDump/issues).
* 如发现bug或有改进意见, 请提交[issues](https://github.com/xaoyaoo/PyWxDump/issues).
* 如有其他想要的功能, 请提交[issues](https://github.com/xaoyaoo/PyWxDump/issues).

<details>
<summary>提交issues方法(点击展开)</summary>

[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/22d15ea6-05d6-4f30-8b24-04a51a59d56d)](https://github.com/xaoyaoo/PyWxDump/issues)
[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/9bdc2961-694a-4104-a1c7-05403220c0fe)](https://github.com/xaoyaoo/PyWxDump/issues)
[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/be1d8913-5a6e-4fff-9fcd-00edb33d255b)](https://github.com/xaoyaoo/PyWxDump/issues)

</details>

**Star History**
[![Star History Chart](https://api.star-history.com/svg?repos=xaoyaoo/pywxdump&type=Date)](https://star-history.com/#xaoyaoo/pywxdump&Date)

# 二、使用说明

## 1. 安装

### 1.1 从pypi安装

```shell script
pip install pywxdump
```

### 1.2 从源码安装

```shell script
pip install git+git://github.com/xaoyaoo/PyWxDump.git
```

或

```shell script
git clone https://github.com/xaoyaoo/PyWxDump.git
cd PyWxDump
python -m pip install -U .
```

## 2. 使用

### 2.1 命令行

激活虚拟环境后（如果有的话），在项目根目录下运行：

```shell script
wxdump 模式 [参数]
#  运行模式(mode):
#    bias      获取微信基址偏移
#    info      获取微信信息
#    db_path   获取微信文件夹路径
#    decrypt   解密微信数据库
#    dbshow    聊天记录查看[需要安装flask]
#    all       获取微信信息，解密微信数据库，查看聊天记录
```

*示例*

以下是示例命令：

```shell script
wxdump bias -h
#usage: main.py bias_addr [-h] --mobile MOBILE --name NAME --account ACCOUNT [--key KEY] [--db_path DB_PATH] [-vlp VLP]
#options:
#  -h, --help            show this help message and exit
#  --mobile MOBILE       手机号
#  --name NAME           微信昵称
#  --account ACCOUNT     微信账号
#  --key KEY             (可选)密钥
#  --db_path DB_PATH     (可选)已登录账号的微信文件夹路径
#  -vlp VERSION_LIST_PATH, --version_list_path VERSION_LIST_PATH
#                        (可选)微信版本偏移文件路径,如有，则自动更新

wxdump info -h
#usage: main.py wx_info [-h] [-vlp VLP]
#options:
#  -h, --help  show this help message and exit
#  -vlp VLP    (可选)微信版本偏移文件路径

wxdump db_path -h
#usage: main.py wx_db [-h] [-r REQUIRE_LIST] [-wf WF]
#options:
#  -h, --help            show this help message and exit
#  -r , --require_list   (可选)需要的数据库名称(eg: -r MediaMSG;MicroMsg;FTSMSG;MSG;Sns;Emotion )
#  -wf , --wx_files      (可选)'WeChat Files'路径
#  -id WXID, --wxid WXID
#                        (可选)wxid_,用于确认用户文件夹

wxdump decrypt -h
#usage: main.py decrypt [-h] -k KEY -i DB_PATH -o OUT_PATH
#options:
#  -h, --help        show this help message and exit
#  -k , --key        密钥
#  -i , --db_path    数据库路径(目录or文件)
#  -o , --out_path   输出路径(必须是目录)[默认为当前路径下decrypted文件夹]

wxdump dbshow -h
#usage: wxdump show_records [-h] -msg  -micro  -media  -fs
#options:
#  -msg , --msg_path     解密后的 MSG.db 的路径
#  -micro , --micro_path
#                        解密后的 MicroMsg.db 的路径
#  -media , --media_path
#                        解密后的 MediaMSG.db 的路径
#  -fs , --filestorage_path
#                        (可选)文件夹FileStorage的路径（用于显示图片）

wxdump all -h
#usage: main.py all [-h]
#options:
#  -h, --help  show this help message and exit
```

### 2.2 python API

更多使用方法参考[tests](./tests)文件夹下的[test_*.py](./tests/)文件

```python
# 单独使用各模块，返回值一般为字典，参数参考命令行
import pywxdump
from pywxdump import VERSION_LIST_PATH, VERSION_LIST

# 1. 获取基址偏移
from pywxdump.bias_addr import BiasAddr

bias_addr = BiasAddr(VERSION_LIST_PATH, VERSION_LIST).run()

# 2. 获取微信信息
from pywxdump.wx_info import read_info

wx_info = read_info(VERSION_LIST)

# 3. 获取微信文件夹路径
from pywxdump.wx_info import get_wechat_db

wx_db = get_wechat_db()

# 4. 解密数据库
from pywxdump.decrypted import batch_decrypt

batch_decrypt("key", "db_path", "out_path")

```

### 2.3 构建可执行文件exe

将下面的代码保存为`build.py`，然后运行`python build.py`即可。（或者执行[build_exe.py](./tests/build_exe.py)）

```python
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
    version_list_path = os.path.join(package_path, 'pywxdump', 'version_list.json')
    # 执行打包命令
    cmd = f'pyinstaller --onefile --clean --add-data "{version_list_path};pywxdump" dist/tmp.py'
    print(cmd)
    os.system(cmd)
else:
    print("未找到安装包路径")
```

【注】:

* 关于基址使用cheat engine获取，参考[CE获取基址.md](doc/CE获取基址.md)
* 关于数据库解析，参考[wx数据库简述.md](doc/wx数据库简述.md)
* 关于更多使用方法，以及各个模块的使用方法，参考前一版本的[python1.0_README.md](doc/python1.0_README.md)

# 三、免责声明（非常重要！！！！！！！）

本项目仅允许在授权情况下对数据库进行备份，严禁用于非法目的，否则自行承担所有相关责任。使用该工具则代表默认同意该条款;

请勿利用本项目的相关技术从事非法测试，如因此产生的一切不良后果与项目作者无关。

# 四、许可证

```text
MIT License

Copyright (c) 2023 xaoyaoo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

PyWxDump is hosted at: https://github.com/xaoyaoo/PyWxDump

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

