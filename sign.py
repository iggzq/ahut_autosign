import base64

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import hashlib

class LoginInfo:
    def __init__(self, flySourceAuth=None, cookie=None):
        self._flySourceAuth = flySourceAuth
        self._cookie = cookie

    def get_flySourceAuth(self):
        return self._flySourceAuth

    def set_flySourceAuth(self, flySourceAuth):
        self._flySourceAuth = flySourceAuth

    def get_cookie(self):
        return self._cookie

    def set_cookie(self, cookie):
        self._cookie = cookie

def get_login_information(username, password):
    login_info = LoginInfo()
    # 使用md5加密password.32位
    md5encry = hashlib.md5()
    md5encry.update(password.encode('utf-8'))
    encryPassword = md5encry.hexdigest()
    url = (
        'https://xskq.ahut.edu.cn/api/flySource-auth/oauth/token'
    )

    params = {
        'tenantId': '000000',
        'username': username,
        'password': encryPassword,
        'type': 'account',
        'grant_type': 'password',
        'scope': 'all'
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        'Authorization': 'Basic Zmx5c291cmNlX3dpc2VfYXBwOkRBNzg4YXNkVURqbmFzZF9mbHlzb3VyY2VfZHNkYWREQUlVaXV3cWU=',
    }

    response = requests.post(url, data=params, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        # 获取 access_token
        access_token = response.json().get('access_token')
        print(response.json())

        if access_token is not None:
            login_info.set_flySourceAuth(access_token)
            login_info.set_cookie(access_token)
            return login_info
        else:
            print("Error: 'access_token' not found in the response.")
            return None
    else:
        print(f"Request failed with status code: {response.status_code}")
        print("Response content:", response.text)
        if 'Bad credentials' == response.json().get('error_description'):
            print("密码错误！  请重启应用")
            return None


def send_email(subject, content, to_email):
    # ！！！若要设置通知邮箱，下列4个信息必填！！！
    # 邮件发送者的邮箱地址
    from_email = ""
    # 发送者的邮箱密码或授权码
    password = ""
    # SMTP服务器地址
    smtp_server = ""
    # SMTP服务器端口
    smtp_port = 0

    # 创建MIMEText对象，设置HTML格式参数
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = Header(from_email)
    msg['To'] = Header(to_email)
    msg['Subject'] = Header(subject)

    try:
        # 使用SSL连接SMTP服务器
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(from_email, password)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")


def send_request(loginName, password, signLat, signLng, email):
    # 获取用户FlySource-Auth
    login_info = get_login_information(loginName, password)

    print('开始发送签到请求')
    # 获取sign签名
    log_url = '/api/flySource-yxgl/dormSignRecord/add?sign='
    jwt_prefix = login_info.get_flySourceAuth()[:10]
    flySource_auth = 'bearer ' + login_info.get_flySourceAuth()
    cookie = 'access-token=' + login_info.get_cookie()
    # 获取当前时间戳（以毫秒为单位）
    t = int(time.time() * 1000)
    # 第一次 MD5 加密：时间戳 + JWT 前10个字符
    first_md5 = hashlib.md5(str(t).encode('utf-8') + jwt_prefix.encode('utf-8')).hexdigest()
    # 第二次 MD5 加密：API URL + 第一次 MD5 结果
    second_md5 = hashlib.md5(log_url.encode('utf-8') + first_md5.encode('utf-8')).hexdigest()
    # Base64 编码的时间戳
    base64_timestamp = base64.b64encode(str(t).encode('utf-8')).decode('utf-8')
    # 最终签名
    signature = f"{second_md5}1.{base64_timestamp}"
    print("Final signature:", signature)

    # 获取今天的日期
    today_date = datetime.date.today()
    # 获取今天星期几
    today_week = today_date.weekday()
    # 创建一个列表来映射数字到星期几的名称
    days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

    url = "https://xskq.ahut.edu.cn/api/flySource-yxgl/dormSignRecord/add"
    payload = {
        "taskId": "766e47d0401a47016f41278e73b10f82",
        "signAddress": "",
        "locationAccuracy": 0,
        "signLat": signLat, "signLng": signLng, "signType": 0, "fileId": "",
        "imgBase64": "/static/images/dormitory/photo.png", "signDate": f"{today_date}", "signTime": "22:15:36",
        "signWeek": f"{days[today_week]}", "scanCode": ""
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3',
        'Authorization': 'Basic Zmx5U291cmNlOkZseVNvdXJjZV9TREVLT0ZTSURGODIzMjlGOHNkODcyM2RTODdEQVM=',
        'Flysource-Sign': signature,
        'FlySource-Auth': flySource_auth,
        'cookie': cookie
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"今日日期为：{today_date},{days[today_week]}")
        print(f"请求成功发送:{response.text}")
        # 请求成功后发送邮件
        subject = f"安工大宿舍签到通知:{response.json().get('msg')}"
        content = f"签到请求已成功发送，详情如下：\n{response.text}"
    else:
        print(f"今日日期为：{today_date},{days[today_week]}")
        print(f"请求失败，状态码：{response.text}")
        # 请求失败后发送邮件
        subject = "安工大宿舍签到 失败 通知"
        content = f"签到请求已成功发送，详情如下：\n{response.text}"
    if email is not None:
        send_email(subject, content, email)


def schedule_sign_in():
    print("***** 登录账号 *****")
    loginName = str(input("请输入用户名:"))
    password = str(input("请输入密码:"))
    print("可以选择较近时间测试一下，签到是否能成功")
    # 获取用户输入的小时
    hour = int(input("请输入签到时间的小时部分(如21代表21点): "))
    # 获取用户输入的分钟
    minute = int(input("请输入签到时间的分钟部分(如30代表30分钟,若设置为99则会设置完成后立即发送签到请求): "))
    # 获取用户输入经纬度
    print("提示：可用百度拾取坐标系统获取坐标！地址: https://api.map.baidu.com/lbsapi/getpoint/index.html")
    signLat = float(input("请输入签到纬度(如：30.678452): "))
    signLng = float(input("请输入签到经度(如：120.556057): "))
    email = str(input("请输入签到状况通知邮箱(选填,签到情况通过邮箱发送给您):"))
    try:
        # 如果分钟为99，则立刻发送请求
        if minute == 99:
            send_request(loginName, password, signLat, signLng, email)
            return
        # 验证输入是否合法
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("输入的时间不在有效范围内，请重新输入！")
        print(f"将于每天{hour}时-{minute}分自动签到")
        # 创建调度器实例
        scheduler = BlockingScheduler()

        # 添加任务，设置为每天特定时间执行
        scheduler.add_job(send_request, 'cron', args=[loginName, password, signLat, signLng, email], hour=hour,
                          minute=minute)

        # 开始调度
        scheduler.start()
        print("设置成功！")
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    schedule_sign_in()
