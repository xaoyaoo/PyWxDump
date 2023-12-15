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

* 欢迎大家提供更多的想法，或者提供代码，一起完善这个项目。


### 如有问题，请先查看：[FAQ](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/FAQ.md) 是否有答案，或者关注公众号回复: `FAQ`。

### 如果是小白，请关注公众号：`逍遥之芯` (右边二维码) ，回复：`PyWxDump` 获取图文教程。

qq交流群：577704006（左边二维码） or 点击链接加入群聊[pywxdump功能交流](https://s.xaoyo.top/gOLUDl)。 

（因为qq群将满，所以进群需要密码，密码请查看[UserGuide.md](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/UserGuide.md)）

<div>
<a href="https://s.xaoyo.top/gOLUDl">
  <img width="40%" src="https://github.com/xaoyaoo/PyWxDump/blob/master/doc/qq.png" alt="QQ群" title="加入QQ群" height="300"></a>
  <img align="right" width="40%"  src="https://github.com/xaoyaoo/PyWxDump/blob/master/doc/qrcode_gh.jpg" alt="公众号" title="关注公众号" height="300">
</div>

# 一、项目介绍

## 1. 项目简介

[PyWxDump](https://github.com/xaoyaoo/PyWxDump)是一款用于获取账号信息(昵称/账号/手机/邮箱/数据库密钥)
、解密数据库、查看聊天记录、备份导出聊天记录为html的工具。

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
* （10）合并多个数据库，方便查看
* （11）增加极简版pywxdump

**利用场景**

1. 钓鱼攻击(通过钓鱼控到的机器通常都是登录状态)
2. 渗透到运维机器(有些运维机器会日常登录自己的微信)
3. 某些工作需要取证(数据库需要拷贝到本地)
4. 自行备份(日常备份自己留存)
5. 等等...............

## 3. 更新计划【由于家里有事，这些计划(除8、9、10)将会在12.30号前统一更新】

* 1.每个人聊天记录分析，生成词云。
* 2.分析每个人每天的聊天数量，生成折线图（天-聊天数量）
* 3.分析不同的人的月聊天数量，年聊天数量，生成折线图
* 4.生成年度可视化报告
* 5.创建GUI图形界面，方便使用
* 8.增加企业微信的支持
* 9.增加获取实时聊天记录的功能
* 10.聊天记录关键字搜索 或者按时间点搜索列出所有的联系人记录就nice了
* 11.增加好友的信息获取
* 12.备份后的聊天记录，恢复到微信中
* 13.朋友圈的查看与备份

## 4. 其他

[PyWxDump](https://github.com/xaoyaoo/PyWxDump)是[SharpWxDump](https://github.com/AdminTest0/SharpWxDump)
的经过重构python语言版本，同时添加了一些新的功能。

* 项目地址：https://github.com/xaoyaoo/PyWxDump
* 目前只在windows下测试过，mac、linux下可能会存在问题。
* 如发现[version_list.json](https://github.com/xaoyaoo/PyWxDump/tree/master/pywxdump/version_list.json)缺失或错误,
  请提交[issues](https://github.com/xaoyaoo/PyWxDump/issues).
* 如发现bug或有改进意见, 请提交[issues](https://github.com/xaoyaoo/PyWxDump/issues).
* 如有其他想要的功能, 请提交[issues](https://github.com/xaoyaoo/PyWxDump/issues).
* 常见问题请参考[FAQ](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/FAQ.md)
* 更新日志请参考[CHANGELOG](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/CHANGELOG.md)
* [:sparkling\_heart: Support Me](https://github.com/xaoyaoo/xaoyaoo/blob/main/donate.md)

## 5. Star History

<details>
<summary>click to expand</summary>

[![Star History Chart](https://api.star-history.com/svg?repos=xaoyaoo/pywxdump&type=Date)](https://star-history.com/#xaoyaoo/pywxdump&Date)

</details>

# 二、使用说明

* 详细使用说明见[UserGuide.md](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/UserGuide.md)

* 极简版使用说明[pywxdumpmini](https://github.com/xaoyaoo/pywxdumpmini)

【注】:

* 关于基址使用cheat engine获取，参考[CE获取基址.md](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/CE获取基址.md)
  （该方法可用`wxdump bias`命令代替，现仅用作学习原理）
* 关于数据库解析，参考[wx数据库简述.md](https://github.com/xaoyaoo/PyWxDump/tree/master/doc/wx数据库简述.md)

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

