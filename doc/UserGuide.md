# User Guide

## Quick Tutorial (Beginners - Advanced users see below)

### 1. Installation

Download the exe file from the [release](https://github.com/xaoyaoo/PyWxDump/releases) (select the latest version)

### 2. Usage

* 1. Open WeChat desktop version and log in
* 2. Navigate to the directory where the downloaded exe file is located
* 3. Double-click wx_dump.exe to run
* 4. Open a browser and visit http://127.0.0.1:5000/ to use the GUI
* 5. Follow the on-screen prompts

【Note】For more detailed usage instructions, follow the official account: `逍遥之芯`, reply: `PyWxDump` to get illustrated tutorials.

## Detailed Tutorial (Beginners see above)

### 1. Installation

#### 1.1 Install from PyPI (install stable version)

```shell script
pip install -U pywxdump
```

#### 1.2 Install from source code (install latest version)

```shell script
pip install -U git+git://github.com/xaoyaoo/PyWxDump.git # This method cannot install the web GUI, which will cause the browser to display page not found, showing 404
```

or

```shell script
# If you want to use the web GUI, execute the following commands
git clone https://github.com/xaoyaoo/wxdump_web.git
cd wxdump_web
npm run build
cd ..
# Install PyWxDump
git clone https://github.com/xaoyaoo/PyWxDump.git
cp -r wxdump_web/dist PyWxDump/pywxdump/ui/web # Copy the web GUI files to PyWxDump. If you don't need the web GUI, you can skip this step
cd PyWxDump
python -m pip install -U .
```

#### 1.3 Package executable exe file

* By default, you have already installed the Python environment, downloaded the source code, and entered the project root directory. You have also installed pyinstaller
* And completed [1.2 Install from source code](#12-install-from-source-code-install-latest-version)

```shell
cd tests
python build_exe.py
# Then execute the output packaging script
pyinstaller --clean --distpath=dist dist/pywxdump.spec
```

* Directly download the packaged exe file: [release](https://github.com/xaoyaoo/PyWxDump/releases)

### 2. Usage

#### 2.1 Command Line

After activating the virtual environment (if applicable), run in the project root directory:

```shell script
wxdump -h  # View specific help
# Usage: 
# wxdump mode [parameters]
#  mode           Running mode:
#    bias         Get WeChat base address offset
#    info         Get WeChat information
#    wx_path      Get WeChat folder path
#    decrypt      Decrypt WeChat database
#    merge        [Test feature] Merge WeChat database (MSG.db or MediaMSG.db)
#    all          【Deprecated】Get WeChat information, decrypt WeChat database, view chat history
#    ui           Start web GUI
#    api          Start API service, default port 5000, no GUI
```

*Examples*

<details>
<summary>Click to expand examples</summary>

The following are example commands:

##### Get WeChat base address offset

```bash
wxdump bias -h # View specific help
wxdump bias --mobile <phone number> --name <WeChat nickname> --account <WeChat account> [--key <key>] [--db_path <WeChat folder path of logged-in account>] [--WX_OFFS_path <WeChat version offset file path>]
```

##### Get WeChat information

```bash
wxdump info -h # View specific help
wxdump info [--WX_OFFS_path <WeChat version offset file path>]
```

##### Get WeChat folder path

```bash
wxdump wx_path -h # View specific help
wxdump wx_path [-r <required database name>] [-wf <WeChat Files path>] [-id <wxid_>] 
```

##### Decrypt WeChat database

```bash
wxdump decrypt -h # View specific help
wxdump decrypt -k <key> -i <database path (directory or file)> [-o <output path>]
```

##### Get WeChat information, decrypt database, view chat history with one command, open port 5000, access via browser to view chat history (supports access from other machines on local network)

```bash
wxdump all -h # 【Deprecated】View specific help
wxdump all
```

##### Start web GUI (follow the GUI prompts for usage)

```bash
wxdump ui -h # View specific help
wxdump ui
```

##### Start API service

```bash
wxdump api -h # View specific help
wxdump api
```

</details>

#### 2.2 Python API

*Import usage examples*

<details>
<summary>Click to expand examples</summary>

```python
# Use individual modules separately, return values are generally dictionaries, parameters refer to command line
from pywxdump import *

# ************************************************************************************************ #
# Get WeChat base address offset
args = {
    "mode": "bias",
    "mobile": "13800138000",  # Phone number
    "name": "WeChat nickname",  # WeChat nickname
    "account": "WeChat account",  # WeChat account
    "key": "key",  # Key (optional)
    "db_path": "WeChat folder path of logged-in account",  # WeChat folder path (optional)
    "WX_OFFS_path": "WeChat version offset file path"  # WeChat version offset file path (optional)
}
bias_addr = BiasAddr(args["account"], args["mobile"], args["name"], args["key"], args["db_path"])
result = bias_addr.run(True, args["WX_OFFS_path"])
# ************************************************************************************************ #
# Get WeChat information
wx_info = read_info(WX_OFFS, True)

# Get WeChat folder path
args = {
    "mode": "db_path",
    "require_list": "all",  # Required database name (optional)
    "wx_files": "WeChat Files",  # 'WeChat Files' path (optional)
    "wxid": "wxid_",  # wxid_, used to confirm user folder (optional)
}
user_dirs = get_wechat_db(args["require_list"], args["wx_files"], args["wxid"], True)
# ************************************************************************************************ #
# Decrypt WeChat database
args = {
    "mode": "decrypt",
    "key": "key",  # Key
    "db_path": "database path (directory or file)",  # Database path
    "out_path": "/path/to/decrypted"  # Output path (must be a directory) [default: decrypted folder in current path]
}
result = batch_decrypt(args["key"], args["db_path"], args["out_path"], True)
# ************************************************************************************************ #
```

</details>

For more usage methods, refer to the [test_*.py](../tests/) files in the [tests](../tests) folder

#### 2.3 Executable exe file

Navigate to the exe file directory and run: `wxdump.exe mode [parameters]`, method same as [command line](#21-command-line)

### 3. FAQ

See [FAQ](./FAQ.md)

### 4. Changelog

See [Changelog](./CHANGELOG.md)

### 5. Other

For group password, please check [FAQ](./FAQ.md)
System support versions: Windows 10 64-bit and above, Python 3.8 and above. For other versions, you need to solve errors yourself
