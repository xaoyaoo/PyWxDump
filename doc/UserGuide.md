# 用户指南

##  小白教程（大佬请看下面）

### 1. 安装

下载[release](https://github.com/xaoyaoo/PyWxDump/releases)中的exe文件

### 2. 使用

* 1.打开微信电脑版，登录微信
* 2.进入下载的exe文件所在目录
* 3.双击wx_dump.exe运行
* 4.打开浏览器，访问 http://127.0.0.1:5000/ 使用图形界面

【注】更多详细使用方法关注公众号：`逍遥之芯`，回复：`PyWxDump` 获取图文教程。

## 详细教程(小白请看上面)

### 1. 安装

#### 1.1 从pypi安装(安装稳定版)

```shell script
pip install -U pywxdump
```

#### 1.2 从源码安装(安装最新版)

```shell script
pip install -U git+git://github.com/xaoyaoo/PyWxDump.git # 该方法无法安装网页图形界面
```

或

```shell script
# 如果使用网页图形界面，需要执行以下命令
git clone https://github.com/xaoyaoo/wxdump_web.git
cd wxdump_web
npm run build
cd ..
# 安装PyWxDump
git clone https://github.com/xaoyaoo/PyWxDump.git
cp -r wxdump_web/dist PyWxDump/pywxdump/ui/web # 将网页图形界面文件复制到PyWxDump中，如果不需要网页图形界面，可以跳过这一步
cd PyWxDump
python -m pip install -U .
```

#### 1.3 打包可执行文件exe

* 打包前需要在python环境中安装pywwxdump，参考[1.2 从源码安装](#12-从源码安装安装最新版)或[1.1 从pypi安装](#11-从pypi安装安装稳定版)
* 自行打包，打包脚本见： [/tests/build_exe.py](https://github.com/xaoyaoo/PyWxDump/blob/master/tests/build_exe.py)

```shell
cd tests
python build_exe.py
# 接着执行输出的打包脚本
```

* 直接下载打包好的exe文件：[release](https://github.com/xaoyaoo/PyWxDump/releases)

### 2. 使用

#### 2.1 命令行

激活虚拟环境后（如果有的话），在项目根目录下运行：

```shell script
wxdump -h  # 查看具体帮助
# 用法: 
# wxdump 模式 [参数]
#  mode           运行模式:
#    bias         获取微信基址偏移
#    info         获取微信信息
#    db_path      获取微信文件夹路径
#    decrypt      解密微信数据库
#    merge        [测试功能]合并微信数据库(MSG.db or MediaMSG.db)
#    dbshow       聊天记录查看
#    export       聊天记录导出为html
#    all          获取微信信息，解密微信数据库，查看聊天记录
#    ui           启动网页图形界面
```

*示例*

<details>
<summary>点击展开示例</summary>

以下是示例命令：

##### 获取微信基址偏移

```bash
wxdump bias -h # 查看具体帮助
wxdump bias --mobile <手机号> --name <微信昵称> --account <微信账号> [--key <密钥>] [--db_path <已登录账号的微信文件夹路径>] [--version_list_path <微信版本偏移文件路径>]
```

##### 获取微信信息

```bash
wxdump info -h # 查看具体帮助
wxdump info [--version_list_path <微信版本偏移文件路径>]
```

##### 获取微信文件夹路径

```bash
wxdump db_path -h # 查看具体帮助
wxdump db_path [-r <需要的数据库名称>] [-wf <WeChat Files 路径>] [-id <wxid_>] 
```

##### 解密微信数据库

```bash
wxdump decrypt -h # 查看具体帮助
wxdump decrypt -k <密钥> -i <数据库路径(目录or文件)> [-o <输出路径>]
```

##### 查看聊天记录

```bash
wxdump dbshow -h # 查看具体帮助
wxdump dbshow -msg <解密后的 MSG.db 的路径> -micro <解密后的 MicroMsg.db 的路径> -media <解密后的 MediaMSG.db 的路径> [-fs <FileStorage 路径>]
```

##### 导出聊天记录为 HTML

```bash
wxdump export -h # 查看具体帮助
wxdump export -u <微信账号> -o <导出路径> -msg <解密后的 MSG.db 的路径> -micro <解密后的 MicroMsg.db 的路径> -media <解密后的 MediaMSG.db 的路径> [-fs <FileStorage 路径>]
```

##### 获取微信信息、解密数据库、查看聊天记录，一条命令搞定，开放端口5000，浏览器访问查看聊天记录（支持局域网其他机器访问）

```bash
wxdump all -h # 查看具体帮助
wxdump all
```

##### 启动网页图形界面

```bash
wxdump ui -h # 查看具体帮助
pywxdump ui
```

</details>

#### 2.2 python API

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

更多使用方法参考[tests](../tests)文件夹下的[test_*.py](../tests/)文件

#### 2.3 可执行文件exe

进入exe文件所在目录，运行： `wxdump.exe 模式 [参数]`，方法同[命令行](#21-命令行)

### 3. FAQ

详见[FAQ](./FAQ.md)

### 4. 更新日志

详见[更新日志](./CHANGELOG.md)

### 5. 其他

进群密码请查看[FAQ](./FAQ.md)