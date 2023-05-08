### 如何通过CE附加进程

1. 打开CE >> 选择左上角放大镜按钮 >> 选择微信进程 >> 选择附加到进程

![image](https://user-images.githubusercontent.com/33925462/236711293-b6ab38b1-588c-4c12-988d-efb65978c781.png)

2. 数值类型选择字符串

![image](https://user-images.githubusercontent.com/33925462/236711574-71b26442-ea49-4069-a3e4-57b9143d14eb.png)

3. 搜索手机号

![image](https://user-images.githubusercontent.com/33925462/236711647-320223ce-bd80-4a1b-b3e0-3614bca1f46f.png)

4. 双击数值

显示：WeChatWin.dll+2FFF540

其中**2FFF540**为手机号的基址

![image](https://user-images.githubusercontent.com/33925462/236711702-516d2c73-0c40-4af7-a462-cf6c7e9952c7.png)

### 如何获取KEY的基址？

首先有几种计算方式：

一、偏移地址计算方法：
偏移地址=内存地址-模块基址

二、模块基址计算方法：
模块基址=内存地址-偏移地址

三、内存地址计算方法：
内存地址=模块基址+偏移地址

1. 先获取用户名的基址

![image](https://user-images.githubusercontent.com/33925462/236711818-8d54b562-6250-4a49-935d-024091823c0e.png)

选择第二个基址：WeChatWin.dll+2FFF970
其中**2FFF970**为用户名的基址

2. KEY的基址可通过用户名的基址计算

计算方式：KEY=用户名-000024
KEY的基址即：**2FFF970-000024=2FFF94C**

![image](https://user-images.githubusercontent.com/33925462/236711975-db8b891c-68a6-4a72-820e-af53f57a3e39.png)

十进制地址为：50329932

代码块中的五个十进制按顺序代表：微信昵称、微信账号、微信手机号、微信邮箱（高版本失效，这个随便填）、微信KEY

```jsx
{
	"微信版本号",
	new List<int>
	{
		50320784,
		50321712,
		50320640,
		38986104,
		50321676
	}
}
```

### 目前每个版本都需要自己调，后期会考虑自动化，先忍忍，能用就行
