# FAQ

### 一、怎么下载/怎么安装？

方法一：进入链接[releases](https://github.com/xaoyaoo/PyWxDump/releases)下载最新版本exe文件

方法二：（本地安装有python环境）使用pip安装
```
pip install PyWxDump
```

### 二、怎么使用

1. 打开微信电脑版，登录微信
2. 进入下载的exe文件所在目录,使用pip安装，跳过此步
3. 按住shift键，同时鼠标右键，选择“在此处打开命令窗口”，或者“在此处打开powershell窗口”
4. 在命令窗口中输入`./wxdump.exe`，按回车键（pip安装输入`wxdump`）
5. 接着根据提示输入参数，回车键确认

### 三、每台电脑上微信账户的key是不是永远不会变？

1. 同一设备，同一微信号，不删除数据情况下，key（密钥）相同

### 四、刚打开就闪退的问题

1. 请检查是否由cmd或powershell打开，不要直接双击exe文件
2. 如果使用方法二安装，请检查是否已经安装了python环境（如果使用pip安装，命令行直接输入wxdump即可）
3. 如果使用方法二安装，检查是否将python安装目录添加到了环境变量中，如果没有，请添加

### 五、如果遇到其他问题

1. 截图或复制错误信息，请全截图或全复制，不要只截一部分或复制部分信息。
2. 通过issue反馈问题，或者加入QQ群：[加入QQ群](https://s.xaoyo.top/gOLUDl)

### 六、如何为PyWxDump贡献代码（提交pr）

提交拉取请求（Pull Request），请按照以下步骤进行操作：

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
7. 提交拉取请求：在你的 GitHub 仓库页面上切换到你刚刚推送的分支，点击 "New pull request"
   按钮，填写一些说明信息，然后点击 `Create pull request`
   按钮，即可提交拉取请求。
8. 等待审核：等待项目维护者审核你的拉取请求，如果通过审核，你的修改将会被合并到项目的主分支中
9. 接着你就可以在右边的`contributors`中看到你的名字了。

### 七、为什么要提交issues

1. 提交issues可以帮助我们更好的改进项目，提高项目的质量

### 八、提交issues方法

[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/22d15ea6-05d6-4f30-8b24-04a51a59d56d)](https://github.com/xaoyaoo/PyWxDump/issues)
[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/9bdc2961-694a-4104-a1c7-05403220c0fe)](https://github.com/xaoyaoo/PyWxDump/issues)
[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/be1d8913-5a6e-4fff-9fcd-00edb33d255b)](https://github.com/xaoyaoo/PyWxDump/issues)

### 九、版本差异

1. 版本 < 3.7.0.30 只运行不登录能获取个人信息，登录后可以获取数据库密钥
2. 版本 > 3.7.0.30 只运行不登录不能获取个人信息，登录后都能获取

### 十、为什么会有解密失败的情况

1. 非当前登录微信的数据库--eg：当前登录微信为A，但是曾经登录过的微信为B，也会尝试解密B的数据库，但是密钥不匹配，所以解密失败
2. 部分数据库本来就是未加密的

### 十一、参数无效

1. 请检查参数是否正确，如果正确，请检查是否使用了中文输入法，如果使用了中文输入法，请切换为英文输入法
2. 检查路径是否正确，如果路径中有空格，请使用英文双引号包裹路径

### 十二、如何获取微信数据库路径/数据库目录是什么/数据库在哪

1. 打开微信电脑版，登录微信
2. 打开微信
3. 打开设置
4. 选择文件管理
5. 点打开文件夹
6. 进入MSG文件夹
7. 就是这个文件夹就是微信数据库目录

### 十三、关于命令没有找到、命令无效、命令无法识别

1. 请检查是否使用了中文输入法，如果使用了中文输入法，请切换为英文输入法
2. 检查是否输入为`wxdump.exe info`，而不是`info`
3. 检查当前目录是否为exe文件所在目录，如果不是，请切换到exe文件所在目录
4. 如果还是无法识别，选中exe文件，拖动到命令行窗口，然后输入 `info`，回车键确认

### 十四、微信锁定情况下能否获取数据库密钥

1. 可以

### 十五、什么是数据库/什么是sqlite数据库

1. 数据库是一个文件，里面存储了微信的聊天记录、好友信息、群信息等等 ，以.db结尾的文件就是数据库文件，这种数据库文件叫做sqlite数据库
2. 位置：打开微信电脑版，登录微信，打开设置，选择文件管理，点打开文件夹，进入MSG文件夹，就是这个文件夹就是微信数据库目录

### 十六、导出的decrypted文件夹里面的内容是什么东西，哪些是重要要，它与Multi目录下的是又是什么关系，Multi目录里面没有MicroMsg

1. `decrypted`文件夹里面的内容是解密后的数据库，对应的是微信数据库目录下的文件（都是相对路径）
2. `Multi`目录下的是微信数据目录下`Msg`下`Multi`内的数据库解密后的相对路径
3. `decrypted`根目录下的`MicroMsg`是微信数据目录下`Msg`下`MicroMsg`的数据库解密后的相对路径
4. `Multi`目录下的`MSG0`-`MSG5`是微信数据目录下`Msg`下`Multi`内的数据库解密后的相对路径
5. `Multi`目录下的`de_MediaMsg0`~`de_MediaMsg5`是微信数据目录下`Msg`下`Multi`内的`MediaMsg0`的数据库解密后的相对路径

### 十七、MSG0~4是什么关系 应该怎么选择用哪一个

1. `MSG0`~`MSG5`是微信聊天记录不同时间段下的数据库，`MSG0`是最旧的，`MSG5`是最新的
2. `MediaMsg0`~`MediaMsg5`是微信聊天记录不同时间段下的数据库，`MediaMsg0`是最旧的，`MediaMsg5`是最新的
3. 一般来说，如果想看最新的聊天记录，就选择`MSG5`和`MediaMsg5`，如果想看最旧的聊天记录，就选择`MSG0`和`MediaMsg0`，如果想看中间的聊天记录，就选择`MSG1`~`MSG4`和`MediaMsg1`~`MediaMsg4`

### 十八、如何合并数据库文件？

使用命令`wxdump.exe merge`，然后根据提示输入参数，回车键确认。
eg：`wxdump.exe merge -i "C:\Users\user\Desktop\decrypted\MSG0.db,C:\Users\user\Desktop\decrypted\MSG1.db,C:\Users\user\Desktop\decrypted\MSG2.db" -o "C:\Users\user\Desktop\decrypted\merge.db"`

### 十八、qq交流群密码

相信你看到这里，已经可以自己解决所有问题了。

如果实在还有疑问，更加建议提交issues。

如果还是想添加qq群，那么关注公众号：`逍遥之芯`，回复`qq群密码`即可获取qq群密码。（因为qq群又快满了，群主又没钱买vip，所以只能这样了）

### 十九、是否可以查看别人的聊天记录

不可以，只能看到有密钥的数据库的聊天记录，如果你有别人的密钥，那么可以查看别人的聊天记录。

### 二十、不登录微信，能获取到密钥吗

不能，必须登录微信才能获取到密钥。
但是可以保存密钥，下次再次使用时候，不需要登录即可。

### 二十一、打开浏览器页面空白

https://blog.csdn.net/qq_46106285/article/details/124749512 
根据这个链接进行修复

### 二十二、关于打包exe文件

参看[UserGuide](./UserGuide.md)中的打包exe文件部分
本项目具体打包流程，参看[../.github/workflows/publish.yml](../.github/workflows/publish.yml)文件

### 二十三、关于系统支持版本

1. Windows 10 64位及以上
2. python 3.8及以上
3. 其他版本遇到错误需要自行解决

### 二十四、实时聊天记录怎么获取

1. `/api/realtimemsg`接口，更新最新数据到数据库中