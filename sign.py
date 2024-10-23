import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime


def send_request(authorization, flySourceAuth, signLat, signLng):
    # 获取今天的日期
    today_date = datetime.date.today()
    # 获取今天星期几
    today_week = datetime.date.today().weekday()
    # 创建一个列表来映射数字到星期几的名称
    days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

    url = "https://xskq.ahut.edu.cn/api/flySource-yxgl/dormSignRecord/add"
    payload = {
        "taskId": "ec7f0f0fb0f6702f61da122ebf0eb592",
        "signAddress": "",
        "locationAccuracy": "289.4",
        "signLat": signLat, "signLng": signLng, "signType": 0, "fileId": "",
        "imgBase64": "/static/images/dormitory/photo.png", "signDate": f"{today_date}", "signTime": "22:15:36",
        "signWeek": f"{days[today_week]}", "scanCode": ""
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Authorization': authorization,
        'FlySource-Auth': flySourceAuth,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"今日日期为：{today_date},{days[today_week]}")
        print(f"请求成功发送:{response.text}")
    else:
        print(f"今日日期为：{today_date},{days[today_week]}")
        print(f"请求失败，状态码：{response.text}")


def schedule_sign_in():
    # 获取用户输入的小时
    hour_input = input("请输入签到时间的小时部分(如21代表21点): ")
    # 获取用户输入的分钟
    minute_input = input("请输入签到时间的分钟部分(如30代表30分钟): ")
    # 获取用户输入经纬度
    print("提示：可用百度拾取坐标系统获取坐标！")
    print("可以选择较近时间测试一下，签到是否能成功，如msg返回“未到签到时间”，则表明经纬度正常")
    sign_lat = input("请输入签到纬度(如：30.678452): ")
    sign_lng = input("请输入签到经度(如：120.556057): ")
    # 获取用户Authorization
    authorization_input = input("请输入您的authorization:")
    # 获取用户FlySource-Auth
    fly_source_auth_input = input("请输入您的FlySource-Auth:")
    try:
        # 将输入的字符串转换为整数
        hour = int(hour_input)
        minute = int(minute_input)
        authorization = str(authorization_input)
        flySourceAuth = str(fly_source_auth_input)
        signLat = float(sign_lat)
        signLng = float(sign_lng)
        # 验证输入是否合法
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("输入的时间不在有效范围内，请重新输入！")
        print(f"将于每天{hour}时-{minute}分自动签到")
        # 创建调度器实例
        scheduler = BlockingScheduler()

        # 添加任务，设置为每天特定时间执行
        scheduler.add_job(send_request, 'cron', args=[authorization, flySourceAuth, signLat, signLng], hour=hour, minute=minute)

        # 开始调度
        scheduler.start()
        print("设置成功！")
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    schedule_sign_in()
