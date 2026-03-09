import os
import requests
from datetime import datetime

PUSH_KEY = os.getenv("PUSH_KEY")
CITY = os.getenv("CITY", "北京")

def get_today():
    return datetime.now().strftime("%Y年%m月%d日 %A")

def get_weather(city):
    try:
        url = f"https://api.oioweb.cn/api/weather/weather?city={city}"
        res = requests.get(url, timeout=10).json()
        if res.get("code") != 200:
            return "天气信息获取失败"

        d = res["result"]
        city = d.get("city", "")
        weather = d.get("weather", "")
        temp = d.get("temperature", "")
        wind = d.get("wind", "")
        humidity = d.get("humidity", "")
        air = d.get("air", "")  # 空气质量
        sunrise = d.get("sunrise", "")
        sunset = d.get("sunset", "")

        # 穿衣建议
        try:
            low, high = temp.replace("℃", "").split("~")
            low = int(low)
            high = int(high)
            avg = (low + high) / 2
            if avg >= 28:
                dress = "炎热，穿短袖、短裤、裙子"
            elif avg >= 20:
                dress = "温暖，短袖/薄长袖即可"
            elif avg >= 10:
                dress = "凉爽，建议薄外套"
            elif avg >= 0:
                dress = "偏冷，需要外套/卫衣"
            else:
                dress = "寒冷，羽绒服/厚大衣"
        except:
            dress = "温度异常，按需穿衣"

        # 是否带伞
        need_umbrella = "需要带伞🌂" if "雨" in weather else "不用带伞☔"

        msg = (
            f"📅 {get_today()}\n\n"
            f"🌆 城市：{city}\n"
            f"⛅ 天气：{weather}\n"
            f"🌡 温度：{temp}\n"
            f"💨 风力：{wind}\n"
            f"💧 湿度：{humidity}\n"
            f"🌀 空气质量：{air}\n"
            f"🌅 日出：{sunrise}\n"
            f"🌇 日落：{sunset}\n\n"
            f"👕 穿衣建议：{dress}\n"
            f"☂ 带伞建议：{need_umbrella}"
        )
        return msg

    except Exception as e:
        return "获取天气信息失败"

def push(title, content):
    if not PUSH_KEY:
        print(content)
        return
    url = "https://api.pushplus.plus/send"
    data = {
        "token": PUSH_KEY,
        "title": title,
        "content": content
    }
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

if __name__ == "__main__":
    weather_info = get_weather(CITY)
    push("☀️ 每日早安提醒", weather_info)
    print("发送完成")
