# T00ls 签到脚本
t00ls 每日签到脚本 整合了钉钉和邮件通知，本脚本运行环境是 Python3.6 +

**依赖安装**：

```bash
pip install requests
pip install beautifulsoup4
```

# 脚本详情

[Python 实现 T00ls 自动签到脚本（邮件+钉钉通知）](https://www.sqlsec.com/2020/07/t00ls.html)

# 定时任务

看了不少网友也使用了 **腾讯云函数**和 **Github 带的 Actions** 来实现自动触发脚本，的确也很不错，感兴趣的朋友也可研究看看。因为国光我有一台 Web 服务器，所以国光我就采用了在 Linux 下使用原生的 crontab 命令实现定时任务了：

```bash
# 查看定时任务
crontab -l

# 编辑定时任务
crontab -e
```

编辑定时任务，一行一个任务，国光我本次填写的内容如下：

```bash
30 9 * * * /usr/bin/python3 /root/code/t00ls/TuBi.py>&1
```

表示每天 9:30 自动运行下面的命令：

````bash
/usr/bin/python3 /root/code/t00ls/TuBi.py
````

这样看起来是不是很简单呢，如果语法没有问题的话，会得到如下提示：

```
crontab: installing new crontab
```

这表示新建定时任务成功，后面就可以躺着赚去每天的 2 个 TuBi 了。

