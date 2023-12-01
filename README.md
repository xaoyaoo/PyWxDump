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

* 2023.11.30 优化命令行界面
* 2023.11.29 添加异形wxid获取方式，添加用户路径自动获取，重建说明文档，对新手更友好
* 2023.11.28 修改wxid获取方式，修复部分bug
* 2023.11.27 解决相对导入包的问题,完善错误提示
* 2023.11.25 聊天记录查看工具bootstrap更换国内cdn
* 2023.11.22 添加all命令中解密错误数据日志写入文件,修复部分bug
* 2023.11.16 增加聊天记录导出为html
* 2023.11.15 添加test文件，添加自动构建可执行文件的脚本,添加版本描述
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


**更新计划**

* 1.每个人聊天记录分析，生成词云。
* 2.分析每个人每天的聊天数量，生成折线图（天-聊天数量）
* 3.分析不同的人的月聊天数量，年聊天数量，生成折线图
* 4.生成年度可视化报告
* 5.创建GUI图形界面，方便使用
* 6.查看群聊中具体发言成员的ID [#31](https://github.com/xaoyaoo/PyWxDump/issues/31)
* 7.增加数据库合并功能，方便查看

注: 欢迎大家提供更多的想法，或者提供代码，一起完善这个项目。

<details>
<summary><strong>贡献代码方法(点击展开)：</strong></summary>

要提交拉取请求（Pull Request），你需要按照以下步骤进行操作：

1. Fork 仓库：首先，在项目的 GitHub 页面上点击 "Fork" 按钮，将项目的代码仓库 fork 到你自己的 GitHub 账号下。
2. 克隆仓库：在你自己的 GitHub 账号下找到 fork 后的项目，点击 `Clone or download`按钮，获取仓库的 URL。然后在本地使用 Git
   命令克隆仓库到你的电脑上：`git clone 仓库的URL`
3. 创建分支：在本地仓库中创建一个新的分支，用于进行你的修改：`git checkout -b 你的分支名`
4. 进行修改：在新创建的分支中进行你需要的修改，包括修复错误、改进现有功能或添加新功能。
5. 提交修改：使用 `git add` 和 `git commit` 命令将修改提交到本地仓库中：
   ```
   git add .
   git commit -m "提交信息"
   ```
6. 推送分支：使用 `git push` 命令将你的本地分支推送到你的 GitHub 仓库中：`git push origin 你的分支名`
7. 提交拉取请求：在你的 GitHub 仓库页面上切换到你刚刚推送的分支，点击 "New pull request" 按钮，填写一些说明信息，然后点击 `Create pull request`
   按钮，即可提交拉取请求。
8. 等待审核：等待项目维护者审核你的拉取请求，如果通过审核，你的修改将会被合并到项目的主分支中，接着你就可以在右边的`contributors`中看到你的名字了。

</details>

欢迎加入交流qq群：577704006 or
点击链接加入群聊[pywxdump功能交流](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=d3hyEpFtRgBTZy6lyX0_ZQC5cBKQ2_Tv&authKey=bctofjxdjHb8YyPz9SpdoTVYY8QPInMQiDKQ82py4pjGYsUCJVqhhmTqHBRIZMev&noverify=0&group_code=577704006)。

[![qq](./doc/qq.png){:height="200px"}](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=d3hyEpFtRgBTZy6lyX0_ZQC5cBKQ2_Tv&authKey=bctofjxdjHb8YyPz9SpdoTVYY8QPInMQiDKQ82py4pjGYsUCJVqhhmTqHBRIZMev&noverify=0&group_code=577704006)

# 一、项目介绍

## 1. 项目简介

[PyWxDump](https://github.com/xaoyaoo/PyWxDump)是一款用于获取账号信息(昵称/账号/手机/邮箱/数据库密钥)
、解密数据库、查看聊天记录、备份导出聊天记录为html的工具。

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
* （9）支持导出聊天记录为html,备份微信聊天记录,方便查看

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

* 项目地址：https://github.com/xaoyaoo/PyWxDump
* 目前只在windows下测试过，linux下可能会存在问题。
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

### 1.1 从pypi安装(安装稳定版)

```shell script
pip install -U pywxdump
```

### 1.2 从源码安装(安装最新版)

<details>
<summary>点击展开</summary>

```shell script
pip install -U git+git://github.com/xaoyaoo/PyWxDump.git
```

或

```shell script
git clone https://github.com/xaoyaoo/PyWxDump.git
cd PyWxDump
python -m pip install -U .
```

</details>

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
#    dbshow    聊天记录查看
#    export    聊天记录导出为html
#    all       获取微信信息，解密微信数据库，查看聊天记录
```

*示例*

<details>
<summary>点击展开示例</summary>

以下是示例命令：

##### 获取微信基址偏移

```bash
pywxdump bias --mobile <手机号> --name <微信昵称> --account <微信账号> [--key <密钥>] [--db_path <已登录账号的微信文件夹路径>] [--version_list_path <微信版本偏移文件路径>]
```

##### 获取微信信息

```bash
pywxdump info [--version_list_path <微信版本偏移文件路径>]
```

##### 获取微信文件夹路径

```bash
pywxdump db_path [-r <需要的数据库名称>] [-wf <WeChat Files 路径>] [-id <wxid_>] 
```

##### 解密微信数据库

```bash
pywxdump decrypt -k <密钥> -i <数据库路径(目录or文件)> [-o <输出路径>]
```

##### 查看聊天记录

```bash
pywxdump dbshow -msg <解密后的 MSG.db 的路径> -micro <解密后的 MicroMsg.db 的路径> -media <解密后的 MediaMSG.db 的路径> [-fs <FileStorage 路径>]
```

##### 导出聊天记录为 HTML

```bash
pywxdump export -u <微信账号> -o <导出路径> -msg <解密后的 MSG.db 的路径> -micro <解密后的 MicroMsg.db 的路径> -media <解密后的 MediaMSG.db 的路径> [-fs <FileStorage 路径>]
```

##### 获取微信信息、解密数据库、查看聊天记录，一条命令搞定，开放端口5000，浏览器访问查看聊天记录（支持局域网其他机器访问）

```bash
pywxdump all
```

</details>

### 2.2 python API

*import调用示例*

<details>
<summary>点击展开示例</summary>

```python
# 单独使用各模块，返回值一般为字典，参数参考命令行
from pywxdump import *

# ************************************************************************************************ #
# 获取微信基址偏移
args = {
    "mode": "bias",
    "mobile": "13800138000",  # 手机号
    "name": "微信昵称",  # 微信昵称
    "account": "微信账号",  # 微信账号
    "key": "密钥",  # 密钥（可选）
    "db_path": "已登录账号的微信文件夹路径",  # 微信文件夹路径（可选）
    "version_list_path": "微信版本偏移文件路径"  # 微信版本偏移文件路径（可选）
}
bias_addr = BiasAddr(args["account"], args["mobile"], args["name"], args["key"], args["db_path"])
result = bias_addr.run(True, args["version_list_path"])
# ************************************************************************************************ #
# 获取微信信息
wx_info = read_info(VERSION_LIST, True)

# 获取微信文件夹路径
args = {
    "mode": "db_path",
    "require_list": "all",  # 需要的数据库名称（可选）
    "wx_files": "WeChat Files",  # 'WeChat Files'路径（可选）
    "wxid": "wxid_",  # wxid_，用于确认用户文件夹（可选）
}
user_dirs = get_wechat_db(args["require_list"], args["wx_files"], args["wxid"], True)
# ************************************************************************************************ #
# 解密微信数据库
args = {
    "mode": "decrypt",
    "key": "密钥",  # 密钥
    "db_path": "数据库路径(目录or文件)",  # 数据库路径
    "out_path": "/path/to/decrypted"  # 输出路径（必须是目录）[默认为当前路径下decrypted文件夹]
}
result = batch_decrypt(args["key"], args["db_path"], args["out_path"], True)
# ************************************************************************************************ #
# 查看聊天记录
args = {
    "mode": "dbshow",
    "msg_path": "解密后的 MSG.db 的路径",  # 解密后的 MSG.db 的路径
    "micro_path": "解密后的 MicroMsg.db 的路径",  # 解密后的 MicroMsg.db 的路径
    "media_path": "解密后的 MediaMSG.db 的路径",  # 解密后的 MediaMSG.db 的路径
    "filestorage_path": "文件夹FileStorage的路径"  # 文件夹 FileStorage 的路径（用于显示图片）
}
from flask import Flask, request, jsonify, render_template, g
import logging

app = Flask(__name__, template_folder='./show_chat/templates')
app.logger.setLevel(logging.ERROR)


@app.before_request
def before_request():
    g.MSG_ALL_db_path = args["msg_path"]
    g.MicroMsg_db_path = args["micro_path"]
    g.MediaMSG_all_db_path = args["media_path"]
    g.FileStorage_path = args["filestorage_path"]
    g.USER_LIST = get_user_list(args["msg_path"], args["micro_path"])


app.register_blueprint(app_show_chat)
print("[+] 请使用浏览器访问 http://127.0.0.1:5000/ 查看聊天记录")
app.run(debug=False)
# ************************************************************************************************ #
# 导出聊天记录为 HTML
args = {
    "mode": "export",
    "username": "微信账号",  # 微信账号（聊天对象账号）
    "outpath": "/path/to/export",  # 导出路径
    "msg_path": "解密后的 MSG.db 的路径",  # 解密后的 MSG.db 的路径
    "micro_path": "解密后的 MicroMsg.db 的路径",  # 解密后的 MicroMsg.db 的路径
    "media_path": "解密后的 MediaMSG.db 的路径",  # 解密后的 MediaMSG.db 的路径
    "filestorage_path": "文件夹FileStorage的路径"  # 文件夹 FileStorage 的路径（用于显示图片）
}
export(args["username"], args["outpath"], args["msg_path"], args["micro_path"], args["media_path"],
       args["filestorage_path"])
```

</details>

更多使用方法参考[tests](./tests)文件夹下的[test_*.py](./tests/)文件

### 2.3 可执行文件exe

* 1.release中提供了可执行文件，可以直接下载使用。
* 2.或者自行打包，打包脚本见： [build_exe.py](./tests/build_exe.py)

*使用示例*

```shell
cd tests
python build_exe.py
```

【注】:

* 关于基址使用cheat engine获取，参考[CE获取基址.md](doc/CE获取基址.md)（该方法一般可用`wxdump bias`命令代替，仅用作学习原理）
* 关于数据库解析，参考[wx数据库简述.md](doc/wx数据库简述.md)

# 三、免责声明（非常重要！！！！！！！）

本项目仅供学习交流使用，请勿用于非法用途，否则后果自负。

您应该在下载保存，编译使用本项目的24小时内，删除本项目的源代码和（编译出的）程序。

本项目仅允许在授权情况下对数据库进行备份，严禁用于非法目的，否则自行承担所有相关责任。

下载、保存、进一步浏览源代码或者下载安装、编译使用本程序，表示你同意本警告，并承诺遵守它;

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

