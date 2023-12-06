# FAQ

- ### 一、怎么下载/怎么安装？

  方法一：进入链接[releases](https://github.com/xaoyaoo/PyWxDump/releases)下载最新版本exe文件

  方法二：（本地安装有python环境）使用pip安装
    ```
    pip install PyWxDump
    ```

- ### 二、怎么使用


1. 打开微信电脑版，登录微信
2. 进入下载的exe文件所在目录,使用pip安装，跳过此步
3. 按住shift键，同时鼠标右键，选择“在此处打开命令窗口”，或者“在此处打开powershell窗口”
4. 在命令窗口中输入`./wxdump.exe`，按回车键（pip安装输入`wxdump`）
5. 接着根据提示输入参数，回车键确认

- ### 三、每台电脑上微信账户的key是不是永远不会变？

1. 同一设备，同一微信，不删除数据情况下，key（密钥）相同

- ### 四、刚打开就闪退的问题


1. 请检查是否由cmd或powershell打开，不要直接双击exe文件
2. 如果使用方法二安装，请检查是否已经安装了python环境（如果使用pip安装，命令行直接输入wxdump即可）
3. 如果使用方法二安装，检查是否将python安装目录添加到了环境变量中，如果没有，请添加

- ### 五、如果遇到其他问题

1. 截图或复制错误信息，请全截图或全复制，不要只截一部分或复制部分信息。
2. 通过issue反馈问题，或者加入QQ群：[加入QQ群](https://s.xaoyo.top/gOLUDl)

- ### 六、如何为PyWxDump贡献代码（提交pr）

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

- ### 七、为什么要提交issues

1. 提交issues可以帮助我们更好的改进项目，提高项目的质量

- ### 八、提交issues方法

[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/22d15ea6-05d6-4f30-8b24-04a51a59d56d)](https://github.com/xaoyaoo/PyWxDump/issues)
[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/9bdc2961-694a-4104-a1c7-05403220c0fe)](https://github.com/xaoyaoo/PyWxDump/issues)
[![image](https://github.com/xaoyaoo/PyWxDump/assets/37209452/be1d8913-5a6e-4fff-9fcd-00edb33d255b)](https://github.com/xaoyaoo/PyWxDump/issues)

- ### 九、版本差异

1. 版本 < 3.7.0.30 只运行不登录能获取个人信息，登录后可以获取数据库密钥
2. 版本 > 3.7.0.30 只运行不登录不能获取个人信息，登录后都能获取

- ### 十、为什么会有解密失败的情况

1. 非当前登录微信的数据库--eg：当前登录微信为A，但是曾经登录过的微信为B，也会尝试解密B的数据库，但是密钥不匹配，所以解密失败
2. 部分数据库本来就是未加密的

- ### 十一、参数无效

1. 请检查参数是否正确，如果正确，请检查是否使用了中文输入法，如果使用了中文输入法，请切换为英文输入法
2. 检查路径是否正确，如果路径中有空格，请使用英文双引号包裹路径