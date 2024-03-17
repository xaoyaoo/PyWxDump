### 1.1 获取微信数据库密钥

1. 打开电脑端微信（不登陆）
2. 在Terminal输入命令`lldb -p $(pgrep WeChat)` (如果没有安装lldb，可以使用`brew install lldb`安装)
3. 输入`br set -n sqlite3_key`，回车
4. 输入`c`，回车
5. 手机扫码登陆电脑端微信
6. 这时候电脑端微信是会卡在登陆界面的，不需要担心，回到Terminal
7. 输入`memory read --size 1 --format x --count 32 $rsi`，回车
8. 将返回的原始key粘贴到下面的字符串中，用这段Python代码获得密钥

* 注：如果运行了lldb（第二步）之后出现error: attach failed: xxxxxxxxxxx 
*    1、重启电脑 黑屏后
*    2、按住 command + R 进入恢复模式，然后输入账户密码
*    3、进入之后到上方点《实用工具》-〉点击〈终端〉之后输入 `csrutil disable` 然后 reboot 重启即可进行调试。
*    (csrutil 的开启是为了提供系统完整性保护 关闭了之后就能使用lldb对wechat进行调试)
*    4、3.8.5版本及以上失效，建议直接安装旧日版

```python
ori_key = """
0x60000241e920: 0xc2 0xf9 0x13 0xbe 0xda 0xe8 0x45 0x82
0x60000241e928: 0x93 0x94 0xsb 0xbf 0x61 0x86 0xd9 0xzf
0x60000241e930: 0xab 0xd3 0x0e 0xf0 0x39 0xcf 0x4c 0xba
0x60000241e938: 0x99 0x3a 0x01 0x05 0x2f 0xz5 0x2d 0xcd
"""

key = '0x' + ''.join(i.partition(':')[2].replace('0x', '').replace(' ', '') for i in ori_key.split('\n')[1:5])
print(key)
```

通过运行上面的程序可以得到一串微信数据库密钥如下：

`0xc2f913bedae845829394sbbf6186d9zfabd30ef039cf4cba993a01052fz52dcd`

### 1.2 获取微信数据库文件

解密方式同windows数据库（但是由于数据库字段名称有差异，暂无法通过本工具查看）