[![中文](https://img.shields.io/badge/README-中文-494cad.svg)](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/README_CN.md) [![English](https://img.shields.io/badge/README-English-494cad.svg)](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/README_EN.md)

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

* Welcome to provide more ideas or code to improve this project together.

### If you are a novice, please pay attention to the Official Accounts: `逍遥之芯` (the QR code is below), and reply: `PyWxDump` to get a picture text tutorial.

### If you have any questions, please check first: [FAQ](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/FAQ.md) Whether there is an answer, or follow the Official Accounts to reply: `FAQ`.

QQ GROUP：[276392799](https://s.xaoyo.top/gOLUDl) or [276392799](https://s.xaoyo.top/bgNcRa)（PASSWORD,please read:[UserGuide.md](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/UserGuide.md)）.

<div>
  <img align="" width="200"  src="https://github.com/xaoyaoo/PyWxDump/blob/master/doc/img/qrcode_gh.jpg" alt="the Official Accounts" title="the Official Accounts" height="200"/>
</div>

# I. Project Introduction

## 1. Brief Introduction

[PyWxDump](https://github.com/xaoyaoo/PyWxDump) is a tool for obtaining wx account information (nicknames/accounts/phones/emails/database keys), decrypting databases, viewing wx chat, and exporting chat as html backups.

* <strong><big>Super eager for stars, if you've come across this project, please give me a [![Star](https://img.shields.io/github/stars/xaoyaoo/PyWxDump.svg?style=social&label=Star)](https://github.com/xaoyaoo/PyWxDump/)! Thank you so much~ </big></strong>

## 2. Feature

#### 2.1 Core

* (1) Get the **base address offset** of WeChat nickname, WeChat account, WeChat phone number, WeChat email, and WeChat KEY
* (2) Get the WeChat nickname, WeChat account, WeChat phone number, WeChat email, WeChat KEY, WeChat original ID (wxid_******), and WeChat folder path of the currently logged-in WeChat
* (3) Decrypt WeChat database based on key
* (4) Combine multiple types of databases for unified viewing

#### 2.2 Extend Function

* (1) View chat history through the web
* (2) Support exporting chat logs as html, csv, and backing up WeChat chat logs
* (3) Remote viewing of WeChat chat history (must be network accessible, such as a local area network)

#### 2.3 Document Class

* (1) Provide descriptions of some fields in the database
* (2) Provide CE to obtain the base address offset method
* (3) Provide a decryption method for MAC database

#### 2.4 Other functions

* (1) Added a minimalist version of [pywxdumpmini](https://github.com/xaoyaoo/pywxdumpmini), which provides only the ability to obtain database keys and database locations
* (2) Support multiple WeChat opening scenarios, obtain multiple user information, etc.

**Utilize the scene**

1. Network security...
2. Daily backup archiving
3. View chat history remotely (view chat history through the web)
4. Wait...............

## 3. Update plan

* 1.Analyze chat logs of each person and generate word clouds.
* ~~2.Analyze the number of chats per person per day and generate a line chart (day-number of chats)~~
* ~~3.Analyze the monthly and annual chat volume of different people and generate a line chart~~
* ~~4.Generate annual visualization reports~~
* 8.Increase support for enterprise WeChat
* 12.Viewing and backing up of the circle of friends
* ~~13.Clean up WeChat storage space and reduce the space occupied by WeChat (hopefully by selecting a person or group and finding out the media files involved in the chat logs of this group, such as pictures, videos, files, voice recordings, etc., and selectively (such as time periods) or batch-wise clearing them from the computer's cache by group conversation.)~~
* 14.Automatically send messages to specified people through UI control

## 4. Other

[PyWxDump](https://github.com/xaoyaoo/PyWxDump) is a refactored python language version of [SharpWxDump](https://github.com/AdminTest0/SharpWxDump), with many new features added.

* Project address: https://github.com/xaoyaoo/PyWxDump
* Currently tested only under Windows, there may be issues under mac and Linux.
* If you find any missing or incorrect information, bugs, or suggestions for improvement in the [WX_OFFS.json](https://github.com/xaoyaoo/PyWxDump/tree/master/pywxdump/WX_OFFS.json), please submit an issue on GitHub.
* For common issues, please refer to [FAQ](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/FAQ.md), and for the update log, please refer to [CHANGELOG](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/CHANGELOG.md)
* Web UI repository location [wxdump_web](https://github.com/xaoyaoo/wxdump_web )
* If you are interested in the implementation principle of wxdump, please pay attention to the Official Accounts: `逍遥之芯`, reply: `原理` to get the principle analysis.
* [:sparkling\_heart: Support Me]( https://github.com/xaoyaoo/xaoyaoo/blob/main/donate.md)

## 5. Star History

<details>
<summary>click to expand</summary>

[![Star History Chart](https://api.star-history.com/svg?repos=xaoyaoo/pywxdump&type=Date)](https://star-history.com/#xaoyaoo/pywxdump&Date)

</details>

# Ⅱ. Instructions For Use

* Detailed instructions, see: [UserGuide.md](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/UserGuide.md)

* the minimalist version, see: [pywxdumpmini](https://github.com/xaoyaoo/pywxdumpmini)

* If you want to modify the UI, clone the [wx_dump_web](https://github.com/xaoyaoo/wxdump_web) and modify it as needed (the UI is developed using VUE+ElementUI)

【note】:

* For obtaining the base address using cheat engine, refer to [CE obtaining base address.md](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/CE获取基址.md)
  (This method can be replaced by the `wxdump bias` command, and is only used for learning principles.)
* For database parsing, refer to [wx database brief.md](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/wx数据库简述.md)

# Ⅲ. Disclaimer (VERY VERY VERY IMPORTANT ! ! ! ! ! !)

### 1. Purpose of use

* This project is only for learning and communication purposes, **please do not use it for illegal purposes**, **please do not use it for illegal purposes**, **please do not use it for illegal purposes**, otherwise the consequences will be borne by yourself.
* Users understand and agree that any violation of laws and regulations, infringement of the legitimate rights and interests of others, is unrelated to this project and its developers, and the consequences are borne by the user themselves.

### 2. Usage Period

* You should delete the source code and (compiled) program of this project within 24 hours of downloading, saving, compiling, and using it; any use beyond this period is not related to this project or its developer.

### 3. Operation specifications

* This project only allows backup and viewing of the database under authorization. It is strictly prohibited for illegal purposes, otherwise all related responsibilities will be borne by the user. Any legal liability incurred by the user due to violation of this regulation will be borne by the user, and is unrelated to this project and its developer.
* It is strictly prohibited to use it to steal others' privacy. Otherwise, all relevant responsibilities shall be borne by yourself.
* It is strictly prohibited to conduct secondary development, otherwise all related responsibilities shall be borne by yourself.

### 4. Acceptance of Disclaimer

* Downloading, saving, further browsing the source code, or downloading, installing, compiling, and using this program indicates that you agree with this warning and promise to abide by it;

### 5. Forbidden for illegal testing or penetration

* It is prohibited to use the relevant technologies of this project to engage in illegal testing or penetration, and it is prohibited to use the relevant codes or related technologies of this project to engage in any illegal work. Any adverse consequences arising therefrom are not related to this project and its developers.
* Any resulting adverse consequences, including but not limited to data leakage, system failure, and privacy infringement, are not related to this project or its developers and are the responsibility of the user.

### 6. Modification of disclaimer

* This disclaimer may be modified and adjusted based on the project's operating conditions and changes in laws and regulations. Users should regularly check this page for the latest version of the disclaimer, and should comply with the latest version of the disclaimer when using this project.

### 7. Others

* In addition to the provisions of this disclaimer, users should comply with relevant laws, regulations, and ethical norms during the use of this project. The project and its developers will not be held responsible for any disputes or losses caused by users' violation of relevant regulations.

* Users are requested to carefully read and understand all contents of this disclaimer, and ensure that they strictly comply with relevant regulations when using this project.

# Ⅳ. Acknowledgments

[![PyWxDump CONTRIBUTORS](https://contrib.rocks/image?repo=xaoyaoo/PyWxDump)](https://github.com/xaoyaoo/PyWxDump/graphs/contributors)  

UI CONTRIBUTORS:    

[![UI CONTRIBUTORS](https://contrib.rocks/image?repo=xaoyaoo/wxdump_web)](https://github.com/xaoyaoo/wxdump_web/graphs/contributors)

otherContributors:

[643104191](https://github.com/643104191) (add [ctypes_utils](https://github.com/xaoyaoo/PyWxDump/blob/9e3e4cb5aec2b9b445c8283d61c58863f4129c6e/pywxdump/wx_info/ctypes_utils.py), Accelerated the acquisition of wxinfo; [9e3e4cb](https://github.com/xaoyaoo/PyWxDump/commit/9e3e4cb5aec2b9b445c8283d61c58863f4129c6e))

