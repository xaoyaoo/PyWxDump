# <center>PyWxDump</center>

* 更新日志（发现[version_list.json](./Program/version_list.json)缺失或错误，请提交[issues](https://github.com/xaoyaoo/PyWxDump/issues))。）
    * 2023.10.09 获取key基址偏移可以根据微信文件夹获取，不需要输入key
    * 2023.10.09 优化代码，删减没必要代码，重新修改获取基址代码，加快运行速度（需要安装新的库 pymem）
    * 2023.10.07 修改获取基址内存搜索方式，防止进入死循环
    * 2023.10.07 增加了3.9.7.29版本的偏移地址
    * 2023.10.06 增加命令行解密数据库
    * 2023.09.28 增加了数据库部分解析
    * 2023.09.15 增加了3.9.7.25版本的偏移地址

## 一、项目介绍

本项目可以获取微信基本信息，以及key，通过key可以解密微信数据库，获取聊天记录，好友信息，群信息等。

该分支是[SharpWxDump](https://github.com/AdminTest0/SharpWxDump)的经过重构python语言版本，同时添加了一些新的功能。

<strong>超想要star，走过路过，顺便点个[![Star](https://img.shields.io/github/stars/xaoyaoo/PyWxDump.svg?style=plastic&label=Star)](https://github.com/xaoyaoo/PyWxDump/)
，谢谢啦~</strong>

## 二、使用方法

### 1. 安装依赖

```shell script
pip install -r requirements.txt
```

**说明**：

1. requirements.txt中的包可能不全，如果运行报错，请自行安装缺少的包
2. 如果运行报错，请检查python版本，本项目使用的是python3.10
3. 安装pycryptodome时可能会报错，可以使用下面的命令安装，自行搜索解决方案（该包为解密的核心包）

### 2. 获取微信基本信息

获取微信的信息，获取到几个，取决于现在登录的几个微信。

**2.1 shell获取微信基本信息**

```shell script
cd Program
python get_wx_info.py
```

结果

```shell script
[+] pid: 2365  <!--进程ID-->
[+] version: *.*.*.*  <!--微信版本-->
[+] key: ******************************************d  <!--数据库密钥-->
[+] name: *****  <!--昵称-->
[+] account: ********  <!--账号-->
[+] mobile: ******  <!--手机号-->
[+] mail: *****  <!--邮箱：在微信3.7版本以上无效-->
========================================
[+] pid: 2365
[+] version: *.*.*.*
[+] key: ******************************************d
[+] name: ***** 
[+] account: ********
[+] mobile: ****** 
[+] mail: ***** 
========================================
...
```

**2.2 import 调用**

```python
import json
from Program.get_wx_info import read_info

version_list = json.load(open("version_list.json", "r", encoding="utf-8"))
data = read_info(version_list)
print(data)
```

结果：

```list
[
  {
    'pid': 5632,
    'version': '*.*.*.*',
    'key': '***************************************',
    'name': '******',
    'account': '******',
    'mobile': '135********',
    'mail': '********'
  },
  {
    'pid': 5632,
    'version': '*.*.*.*',
    'key': '***************************************',
    'name': '******',
    'account': '******',
    'mobile': '135********',
    'mail': '********'
  },
  ...
]
```

**说明**： 每个字段具体含义，参看上一条shell获取微信基本信息

### 3. 获取偏移地址

* 该方法一般不需要，只有当[version_list.json](./Program/version_list.json)没有对应的微信版本时，可以通过该方法获取偏移地址
* 如果需要请参考下面的方法获取

**3.1 通过python脚本获取**

```shell
python get_base_addr.py  --mobile 152***** --name **** --account *** --key ********** --db_path  "****\WeChat Files\wxid_******"
```

参数说明：

    以下参数必选
    mobile = "152********"  # 手机号
    name = "******"  # 微信昵称
    account = "******"  # 微信账号
    # 以上信息可以通过微信客户端获取
    
    以下参数二选一（key获取偏移更快，db_path获取偏移很慢，本地测试需要10-60s）
    key = '**********************************************'
      # 需要降低版本使用get_wx_info.py获取key，也可以通过CheatEngine等工具获取
      # 最好是保存之前同微、同设备信使用过的key，非常方便
    db_path = "****\WeChat Files\wxid_******"  
      # 微信文件夹，通过微信客户端，设置-文件管理-微信文件的默认保存位置获取

return：{'3.9.7.29': [63486984, 63488320, 63486792, 0, 63488256]}

    (十进制)按顺序代表：微信昵称、微信账号、微信手机号、微信邮箱（默认0）、微信KEY

[注]：如果参数错误，得到的对应地址偏移为0，邮箱高版本失效，默认为0

**3.2 通过CheatEngine等工具获取**

具体请查看：[CE获取基址.md](./CE%E8%8E%B7%E5%8F%96%E5%9F%BA%E5%9D%80.md)

* 该方法获取到的偏移地址需要手动添加到[version_list.json](./Program/version_list.json)中

**3.3 最简单获取方法**

最简单的方法当然是运行

```shell
git clone https://github.com/xaoyaoo/PyWxDump.git
```

重新拉取一份新的啦~

* ps: 该方法不一定能获取到最新的版本
* 如果需要最新的版本，可以通过上面的方法获取
* 你也可以提交Issues，分分钟给你更新

## 三、获取解密数据库

* [decrypt.py](./decrypted/decrypt.py) : 数据库解密脚本
* [get_wx_decrypted_db.py](./decrypted/get_wx_decrypted_db.py) :直接读取当前登录微信的数据库，解密后保存到当前目录下的decrypted文件夹中

[注]：每台设备、每个微信账号对应一个key，切换设备或者微信账号，key都会变化

![image](https://user-images.githubusercontent.com/33925462/179410883-10deefb3-793d-4e15-8475-a74954fafe19.png)

* 解密后可拖入数据库工具查找敏感信息
* 还有一份数据的说明文档，但是我累了，不想写了

**方法**

进入目录[decrypted](./decrypted)

```shell
python decrypt.py --key ******** --db_path ./decrypted/decrypted.db --out_path ./decrypted/decrypted.db
```

[注]：--key为数据库密钥，--db_path为数据库路径，--out_path为解密后的数据库路径(解密后的路径目录必须存在)

自动根据注册表读取本地微信聊天记录文件夹，解密后保存到当前目录下的decrypted文件夹中

```shell
python get_wx_decrypted_db.py --key ********
```

## 四、解析数据库

* [parse.py](./parse_db/parse.py) : 数据库解析脚本，可以解析语音、图片、聊天记录等
* 关于各个数据库的说明文档，请查看[parse_db](./parse_db)目录下的[README.md](./parse_db/README.md)

未完待续...

## 五、支持功能

1. 支持微信多开场景，获取多用户信息等
2. 微信需要登录状态才能获取数据库密钥

**版本差异**

1. 版本 < 3.7.0.30 只运行不登录能获取个人信息，登录后可以获取数据库密钥
2. 版本 > 3.7.0.30 只运行不登录不能获取个人信息，登录后都能获取

**利用场景**

1. 钓鱼攻击(通过钓鱼控到的机器通常都是登录状态)
2. 渗透到运维机器(有些运维机器会日常登录自己的微信)
3. 某些工作需要取证(数据库需要拷贝到本地)
4. 自行备份(日常备份自己留存)
5. 等等...............

## 六、免责声明（非常重要！！！！！！！）

本项目仅允许在授权情况下对数据库进行备份，严禁用于非法目的，否则自行承担所有相关责任。使用该工具则代表默认同意该条款;

请勿利用本项目的相关技术从事非法测试，如因此产生的一切不良后果与项目作者无关。
