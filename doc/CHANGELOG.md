## v3.0.36.(待发布)

- UPDATE CHANGELOG.md

## v3.0.35

- fix 部分表情无法显示

## v3.0.34

- fix
- (49, 2000): "转账",
- UPDATE CHANGELOG.md

## v3.0.33

- fix
- UPDATE CHANGELOG.md

## v3.0.32

- 使用本地设置，增加选项

## v3.0.31

- fix bug
- UPDATE CHANGELOG.md

## v3.0.30

- 位置显示支持
- 消息类型统一处理
- 转账消息更加明确
- 增加更多消息类型的说明
- UPDATE CHANGELOG.md
- get_BytesExtra 数据类型增加其他处理

## v3.0.29

- wx 3.9.11.17支持
- user_list_by_label
- UPDATE CHANGELOG.md

## v3.0.28

- 修复打包问题
- 增加联系人标签显示
- UPDATE CHANGELOG.md
- get info add decorator info_error

## v3.0.27

- fix
- 增加容错
- fix 浏览器打开参数

## v3.0.26

- fix
- fix test

## v3.0.25

- fix
- fix Favorite
- fix wx 3.9.10.27
- feat: 数据库合并与查询优化 (#97)
- fix: fix bug on cli dbshow command (#96)
- Merge branch 'master' of github.com:xaoyaoo/PyWxDump

## v3.0.24

- 增加说明
- 增加收藏夹的库
- UPDATE CHANGELOG.md

## v3.0.23

- fix
- 增加注释
- 更新DOC
- 增加注释方便使用
- 增加收藏数据库解析
- 准备添加收藏数据库解析

## v3.0.22

- fix
- 修改获取name的逻辑
- 增加依赖库pandas
- fix dbshow 命令
- UPDATE CHANGELOG.md

## v3.0.21

- fix
- fix 增加容错 #93

## v3.0.20

- fix 合并实时数据库的函数在路径名中有中文时会报错 #92

## v3.0.19

- fix
- 更新FAQ
- 加快info的获取速度
- UPDATE CHANGELOG.md
- 优化代码，增加name获取的容错 #94

## v3.0.18

- 修复无法自动解密（解密报错的问题）
- UPDATE CHANGELOG.md

## v3.0.17

- 修复无法自动解密（解密报错的问题）

## v3.0.16

- 更新文档
- 格式化代码
- 优化命令说明
- 更新说明文件
- 废弃命令增加说明
- 增加合并全部数据库的命令
- UPDATE CHANGELOG.md

## v3.0.15

- 增加合并数据库的容错
- (backup/master) 增加合并数据库的容错

## v3.0.14

- fix auto无法使用的问题。

## v3.0.13

- test 聊天记录分析
- fix 无法auto无法使用的问题。

## v3.0.12

- 调整显示样式
- 增加数据展示的包
- 更新 FAQ.md
- 更新 UserGuide.md
- UPDATE CHANGELOG.md

## v3.0.11

- fix
- 清理代码
- 清理微信存储空间核心代码
- 更新 README_CN.md
- 更新 README_EN.md
- 清理已经废弃的代码（可能会存在有用代码被清除）

## v3.0.10

- fix
- fix 部分错误
- 删除部分命令行不可用命令

## v3.0.8

- fix

## v3.0.7

- 重构导出
- 重构导出csv
- 重构导出json
- 增加获取群备注的功能
- 增加数据库查询失败的容错
- UPDATE CHANGELOG.md
- OpenIMContact表中不到的问题

## v3.0.6

- fix

## v3.0.5

- fix
- fix 数据库合并的问题
- UI 偏移地址获取 fix
- UPDATE README.md

## v3.0.4

- fix

## v3.0.3

- fix

## v3.0.2

- fix

## v3.0.1

- fix
- 优化代码
- 增加注释
- UPDATE README.md
- UPDATE CHANGELOG.md

## v3.0.0

- 加速访问，增加容错merge
- 重构大部分API，响应速度翻倍
- UPDATE CHANGELOG.md
- 加快数据库访问速度，同时独立处理每一个数据库
- 增加新的使用方法，加快访问速度，合并相似的功能

## v2.4.71

- fix
- 完善注释
- 修改数据库匹配规则
- 增加3.9.10.19支持
- fix 图片优先显示清晰版本
- 增加UI选项是否自动打开浏览器
- UPDATE README.md
- 读取ExtraBuf（联系人表）
- fix 部分情况下视频不能正常显示
- UPDATE CHANGELOG.md
- MSG数量超过10个无法获取最新数据的bug

## v2.4.70

- 增加对引用消息的解析
- Update README.md
- UPDATE CHANGELOG.md
- 读取群聊数据,主要为 wxid，以及对应昵称

## v2.4.62

- 增加对引用消息的解析
- UPDATE CHANGELOG.md

## v2.4.61

- fix
- UPDATE DOC
- fix and add
- 解密并合并 OpenIM*
- OpenIM* 增加 #86
- UPDATE README.md
- 优化 decryption.py
- UPDATE CHANGELOG.md
- 数据库连接方式改为共用连接，降低时间开销
- 添加编码# -*- coding:utf-8 -*-

## v2.4.60

- fix
- 系统通知，显示为系统发送
- subprocess 隐藏调用过程

## v2.4.59

- 修复无法打开聊天查看

## v2.4.58

- fix 群聊图片发送者显示为未知
- UPDATE CHANGELOG.md

## v2.4.57

- fix AND MicroMsg实时数据库 #82

## v2.4.56

- fix

## v2.4.55

- fix
- 转账显示具体金额
- 合并转发的聊天记录 #84
- UPDATE CHANGELOG.md

## v2.4.54

- fix
- fix 高频使用

## v2.4.50

- 误删2.4.46，重新发布
- UPDATE CHANGELOG.md

## v2.4.46

- 格式化文件
- 增加获取总消息数的接口
- UPDATE CHANGELOG.md

## v2.4.44

- fix 无法导出html

## v2.4.43

- fix权限错误问题
- UPDATE CHANGELOG.md

## v2.4.42

- fix 白屏问题
- UPDATE CHANGELOG.md

## v2.4.41

- html fix
- 更新 README.md
- UPDATE CHANGELOG.md

## v2.4.40

- v2.4.35
- 导出为html
- 过去最新更新版本
- 修复语音通话的显示
- 增加检查更新的按钮
- 更新 READNE.md
- 自动加载 markdown
- 修复3.9.9.43偏移错误
- Type为49，默认显示文件名称
- UPDATE CHANGELOG.md

## v2.4.35

- 格式化代码
- v2.4.35
- 自动生成更新日志
- 自动生成CHANGELOG.md
- 优化cli.console_run (#81)

## v2.4.34

- 格式化文件
- 增加实时数据库解密方法
- 语音or视频通话正常显示
- 图片路径统一请求，无需单独使用请求
- UPDATE CHANGELOG.md
- 感谢zhyc9de增加消息类型 #77

## v2.4.33

- add wx3.9.9.43bias
- online 参数无需添加 true
- UPDATE CHANGELOG.md
- wx3.9.9.43bias、online 参数

## v2.4.32

- 自定义路径，自动去除引号
- UPDATE CHANGELOG.md
- 自定义路径，不使用key时，设置非必须参数

## v2.4.31

- fix
- 增加注释
- 修改版权信息
- UPDATE CHANGELOG.md
- 将自动解密微信数据改为重新解密数据库，获取最新数据
- 增加了单api的运行和返回聊天中所有用户接口 (#73)
- 增加使用上次数据的选择，同时将自动解密微信数据改为重新解密数据库，获取最新数据

## v2.4.30

- 格式化代码
- 删除test下不必要文件
- 增加打包为exe时，添加版本信息
- UPDATE CHANGELOG.md

## v2.4.29

- 代码格式化
- 重命名conf.json
- session保存更加合理化
- 增加视频文件等内容显示 #71
- 文件和视频的支持api (#71)
- UPDATE CHANGELOG.md
- 添加微信数据文件路径通过读取内存方式获取
- Merge branch 'master' of https://github.com/xaoyaoo/PyWxDump

## v2.4.28

- 更新FAQ
- v2.4.28
- 更新偏移地址获取函数
- 更新test Bias
- 3.9.9.35 版本支持
- UPDATE CHANGELOG.md
- add video api (#69)
- Merge branch 'master' of https://github.com/xaoyaoo/PyWxDump

## v2.4.27

- UPDATE CHANGELOG.md
- fix 自动解密中获取主要数据库失败问题

## v2.4.26

- test
- api接口返回值增加报错堆栈
- UPDATE CHANGELOG.md

## v2.4.25

- UPDATE 文档
- UPDATE README.md
- 增加报错的具体显示内容，方便调试
- UPDATE CHANGELOG.md
- 添加api接口报错9999的文件以及行号

## v2.4.24

- 生成CHANGELOG.md
- publish.yml发布时候增加日志说明

## v2.4.23

- 增加部分导出的功能
- 增加导出json方式
- 分离启动flask的方式
- 增加导出加密数据库的方式
- 增加导出解密数据库、csv方式
- start falsk 添加参数是否自动打开浏览器

## v2.4.22

- fix
- 添加3.9.27偏移
- 添加3.9.9.27偏移

## v2.4.21

- fix

## v2.4.20

- 聊天记录显示添加自定义数据库路径功能

## v2.4.19

- 导出
- 解密MAC
- 导出聊天记录
- 添加UI的命令
- 添加聊天记录选择展示
- 解密MAC数据库方法
- 聊天记录显示添加自定义数据库路径功能

## v2.4.18

- 修复语音无法使用

## v2.4.17

- 语音错误
- 修复语音无法使用
- UPDATE README
- create pipeline-20240113.yml
- add default pipeline template yaml
- Merge remote-tracking branch 'gitee/master'

## v2.4.16

- fix

## v2.4.15

- fix

## v2.4.14

- 聊天记录查看更丝滑
- 使用命令增加版本提示，方便排错
- all 命令添加局域网访问选项online，dbshow添加merge命令，可以只输入一个

## v2.4.13

- 更新2.4.13
- 更新README
- 添加专业工具中偏移功能
- 添加专业工具中解密的功能
- 添加专业工具中合并数据库功能
- 添加专业工具中获取正在运行微信信息内容

## v2.4.12

- 将文件打包zip,自动发布

## v2.4.11

- 将文件打包
- 添加自动更具web库构建exe，并发布
- 添加自动根据web库构建exe，并发布

## v2.4.10

- 添加自动更具web库构建exe，并发布
- 添加是否支持局域网访问选项，默认为false

## v2.4.9

- 更新README
- 完善命令行错误提示
- 更新导出的csv命名方式
- 更新导出为csv的方式，字段中有因为,自动转义

## v2.4.8

- api 增加参数
- 更新UI,上拉更新数据
- 逆序加载聊天记录，api聊天记录添加id
- 获取contact_count_list增加去重功能

## v2.4.7

- 修复bug

## v2.4.6

- 修复UI的问题

## v2.4.5

- 自动构建
- 修复UI的问题
- update UI
- update README

## v2.4.4

- 增加默认执行all命令

## v2.4.3

- 增加默认执行all命令
- 修复打包，未将资源打包进去

## v2.4.2

- 修复打包，未将资源打包进去

## v2.4.1

- 更新2.4.1，使用新版UI

## v2.4.0

- UI
- UI修改
- 修复bug
- 增加图片显示
- 增加语音展示
- 增加无权限的容错
- 更新2.4.0，使用新版UI

## v2.3.29

- 修复无法正常显示图片并报错的问题

## v2.3.28

- 更新文档
- 修复无法正常显示图片并报错的问题
- 命令行添加保存info信息到json文件选项
- Squashed 'pywxdump/ui/web/' content from commit 7283129
- Merge commit '054ade4b293dedaf0f92c9a8675148b962231e51' as 'pywxdump/ui/web'

## v2.3.27

- 防止打包没有数据文件报错
- ALL命令自动查看所有的本地聊天记录，自动合并所有聊天记录相关数据库

## v2.3.26

- 更新测试
- 添加导出为csv函数
- 添加.gitignore
- 添加导出为csv命令【测试功能】
- 优化wx_info导入，分离工具。
- Update db_parsing.py (#54)
- Merge remote-tracking branch 'origin/master'

## v2.3.25

- 设置FileStorage_path为非必须选项

## v2.3.24

- 导出文件
- 更新3.9.8.25支持。 #52

## v2.3.23

- 改善python3.8以下版本的容错

## v2.3.22

- 修复聊天记录图片无法显示的问题。
- 改善python3.8以下版本的容错
- 修复聊天记录图片无法显示的问题。 #49

## v2.3.21

- mini
- 添加简单教程
- v2.3.21
- test setup.py
- 修改FAQ，为qq群添加密码
- 修复多开微信无法获取key的bug
- simplify_wx_info 更新

## v2.3.11

- 更新
- 添加计划
- 修复合并数据库功能
- 更新db_parsing
- 修复多开微信无法获取key的bug

## v2.3.10

- 修复合并数据库后无法播放语音
- 修复聊天记录为0时，报错的bug

## v2.3.9

- merge 参数修改

## v2.3.8

- 新增FAQ
- merge 参数修改
- 修复info_filePath v2.3.7

## v2.3.7

- 修复bug
- 修改小白文档
- 修复info_filePath
- 修复info_filePath v2.3.7

## v2.3.6

- 优化命令行提示，优化合并数据库方法

## v2.3.5

- merge命令错误修复

## v2.3.4

- merge命令错误修复
- merge 输出如果不是文件，则自动创建文件

## v2.3.3

- 更新32wx获取key的方式
- 群聊显示具体的发送人。 #31
- v2.3.3 新增简化版info获取

## v2.3.2

- 更新文档
- 群聊显示具体的发送人。
- 群聊显示具体的发送人。 #31

## v2.3.1

- 更新文档
- 修复32版本无法获取到key的偏移
- 更新v2.3.0，添加合并数据库功能
- 修复32位版本无法获取到key的偏移 v2.3.1

## v2.3.0

- 更新v2.3.0
- 更新v2.2.18
- 更新v2.3.0，添加合并数据库功能
- 重构文件结构，增加合并数据库功能，修复部分bug

## v2.2.18

- 更新文档
- 重构代码
- 更新v2.2.18
- parse.py 修改
- 修复部分bug #34
- 修复多微信获取wxid错误。 #33
- Delete dist directory
- Delete .eggs directory
- Delete pywxdump.egg-info directory
- Delete build/lib/pywxdump directory
- fix decompress_CompressContent func parameter
- Merge branch 'master' of github.com:xaoyaoo/PyWxDump
- lz4 decompress and bytesExtra decode and enhance ET (#37)

## v2.2.17

- 优化命令行界面
- 为exe添加图标
- 更新README

## v2.2.16

- 优化命令行界面
- 优化bias获取

## v2.2.15

- 发布2.2.15
- 修复publish
- publish test
- 重建说明文档，对新手更友好
- publish add cache
- 添加异性wxid获取方式，添加用户路径自动获取
- 添加异性wxid获取方式，添加用户路径自动获取 #33

## v2.2.14

- publish test

## v2.2.13

- 修改wxid获取方式，修复部分bug

## v2.2.12

- 修复publish

## v2.2.11

- v2.2.11
- test publish.yml

## v2.2.10

- v2.2.10

## v2.2.9

- 修改readme
- 发布修正版2.2.9
- 更新workflows
- 修改readme，添加计划
- 解决相对导入包的问题,完善错误提示

## v2.2.8

- 增加聊天记录导出为html
- 添加all命令中解密错误数据日志写入文件,修复部分bug #28 #29

## v2.2.7

- 增加聊天记录导出为html

## v2.2.6

- 添加版本描述
- 更新README
- 添加test文件，添加自动构建可执行文件的脚本
- 修复无法获取wxid的bug,更新部分逻辑,重构解密脚本的返回值，重构命令行参数

## v2.2.5

- 修复无法获取wxid的bug,更新部分逻辑,重构解密脚本的返回值，重构命令行参数

## v2.2.2

- 修复部分bug

## v2.2.1

- 添加聊天记录解析，查看工具

## v2.2.0

- 添加聊天记录解析，查看工具

## v2.1.13

- 增加3.9.8.15版本支持
- 修复wxdump wx_db命令行参数错误 #19

## v2.1.12

- 增加3.9.8.15版本支持

## v2.1.11

- 修改version_list
- 修复3.9.2.*版本无法正常运行
- 添加自动发布到pypi的github action

## v2.1.10

- 添加自动发布到pypi的github action

## v2.1.9

- 修复3.9.2.*版本无法正常运行
- 添加自动发布到pypi的github action

## v2.1.7

- update version_list
- 添加自动发布到pypi的github action
- add auto get bias addr ,not need input key or wx folder path.

## v2.1.5

- 更新
- 更新readme
- Create LICENSE
- 添加"3.9.7.15"偏移 #12
- add auto get bias addr ,not need input key or wx folder path.

## v2.1

- 优化代码
- 作为包安装使用
- 添加注释，优化代码
- (origin/v1.0) 优化代码
- 添加"3.9.5.81"版本偏移地址
- 将整个项目作为包安装，增加命令行统一操作
- 整体重构项目，优化代码，增加命令行统一操作
- 添加"3.9.5.81"版本偏移地址 #10

## python

- 优化代码
- 完善错误判断
- 修改readme
- Ð޸Äbug #3
- 添加数据库解析说明
- 3.9.7.29偏移
- 使用python重构
- SharpWxDump
- Crypto导入方式更改
- 3.7.5.11以上为40
- 格式化MSG数据库解析代码
- 增加3.9.7.25版本支持
- 优化get_wx_info代码
- 新增数据库解析，数据库字段说明
- 更换更高效的key地址计算方式
- 添加自动解密数据库的命令行操作
- Create CE获取基址.md
- Create README.md
- Update README.md
- 缩短使用db_path的运行时间
- Delete Program.cs
- Update Program.cs
- Add files via upload
- Delete obj directory
- '修改获取基址内存搜索方式，防止进入死循环'
- Update issue templates
- 修改内存搜索方式，防止参数错误，无限循环搜索
- 获取key基址偏移可以根据微信文件夹获取，不需要输入key
- Delete bin/x86/Release directory
- Delete .vs/SharpWxDump/v16 directory
- 完善项目，添加 数据库解密脚本，添加自动获取当前登录微信的数据库并解密，增加偏移地址脚本获取方式，可以一件获取偏移。
- Merge branch 'python1.0' of github.com:xaoyaoo/PyWxDump into python1.0