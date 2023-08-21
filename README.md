## SharpWxDump
如何获取指定版本基址：https://github.com/AdminTest0/SharpWxDump/blob/master/CE%E8%8E%B7%E5%8F%96%E5%9F%BA%E5%9D%80.md

## 特别说明
该分支是<a href="https://github.com/AdminTest0/SharpWxDump">SharpWxDump</a>的python语言版本。
同时添加了一些新的功能。

**使用方法**
```
cd Program
python3 Program.py

# 也可以import 调用
import Program
Program.read_test(version)
```

**支持功能**
1. 支持微信多开场景，获取多用户信息等
2. 微信需要登录状态才能获取数据库密钥
3. 没有动态获取功能，已将偏移地址写入version_list.josn内，会不定期更新，**如有需要的版本请提交Issues**

![image](https://user-images.githubusercontent.com/33925462/179410099-c0f52c1c-b552-4a51-9822-7440b097bca4.png)

**版本差异**
1. 版本 < 3.7.0.30 只运行不登录能获取个人信息，登录后可以获取数据库密钥
2. 版本 > 3.7.0.30 只运行不登录不能获取个人信息，登录后都能获取

**利用场景**
1. 钓鱼攻击(通过钓鱼控到的机器通常都是登录状态)
2. 渗透到运维机器(有些运维机器会日常登录自己的微信)
3. 某些工作需要取证(数据库需要拷贝到本地)
4. 自行备份(日常备份自己留存)
5. 等等...............

**数据库解密**

解密后可拖入数据库工具查找敏感信息

![image](https://user-images.githubusercontent.com/33925462/179410883-10deefb3-793d-4e15-8475-a74954fafe19.png)

**参考地址**

数据库解密脚本：https://mp.weixin.qq.com/s/4DbXOS5jDjJzM2PN0Mp2JA


## 免责声明
本项目仅允许在授权情况下对数据库进行备份，严禁用于非法目的，否则自行承担所有相关责任。使用该工具则代表默认同意该条款;

请勿利用本项目的相关技术从事非法测试，如因此产生的一切不良后果与项目作者无关。
