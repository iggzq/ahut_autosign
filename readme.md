# 安工大自动签到

## 1. 仅供学习使用！！！

## 2. 一台服务器是必须的，总不能电脑一直开着吧

## 3. 使用

### 须有python环境，然后下载或复制sign.py代码，然后运行下列指令

```python
pip install apscheduler requests
python3 sign.py
```

其中authorization和FlySource-Auth有两种方法：1.抓包（麻烦）fiddler+手机或模拟器 2.浏览器调试查看http获取

登录pc版微信，然后打开签到小程序，右上角用浏览器打开，登录，打开浏览器调试，查看request header，就可以了