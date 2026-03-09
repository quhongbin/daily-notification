import requests
import json
import os
import sys

# 配置信息（敏感信息将从环境变量读取）
QWEATHER_KEY = os.environ.get("QWEATHER_KEY")
LOCATION_ID = os.environ.get("LOCATION_ID")  # 城市ID
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY")

def get_weather():
    """获取天气、空气质量和日出日落"""
    # 天气实况 API
    weather_url = f"https://devapi.qweather.com/v7/weather/now?location={LOCATION_ID}&key={QWEATHER_KEY}"
    # 空气质量 API
    air_url = f"https://devapi.qweather.com/v7/air/now?location={LOCATION_ID}&key={QWEATHER_KEY}"
    # 日出日落 API (需要和风天气另外开通，若不开通可用默认值，这里用计算逻辑模拟或直接请求)
    # 注意：日出日落接口可能需要付费订阅，免费版可用天文API或简单模拟，这里演示请求方式
    sun_url = f"https://devapi.qweather.com/v7/astronomy/sun?location={LOCATION_ID}&key={QWEATHER_KEY}"

    try:
        weather_res = requests.get(weather_url).json()
        air_res = requests.get(air_url).json()
        
        if weather_res["code"] != "200":
            return None, f"天气接口错误: {weather_res['code']}"

        now = weather_res["now"]
        aqi = air_res.get("now", {}).get("aqi", "未知")
        category = air_res.get("now", {}).get("category", "未知")
        
        # 尝试获取日出日落，如果接口报错则使用默认提示
        sun_data = requests.get(sun_url).json().get("sun", None)
        sunrise = sun_data.get("rise", "需升级API") if sun_data else "需查看权限"
        sunset = sun_data.get("set", "需升级API") if sun_data else "需查看权限"

        return {
            "temp": now["temp"],
            "text": now["text"],
            "windDir": now["windDir"],
            "windScale": now["windScale"],
            "aqi": aqi,
            "aqi_category": category,
            "sunrise": sunrise,
            "sunset": sunset
        }, None
    except Exception as e:
        return None, str(e)

def get_clothing_advice(temp):
    """根据温度生成穿衣建议"""
    temp = int(temp)
    if temp <= 5:
        return "羽绒服、棉裤、围巾手套，注意防寒！"
    elif 5 < temp <= 15:
        return "风衣、厚外套、毛衣，适宜穿秋裤。"
    elif 15 < temp <= 22:
        return "薄外套、卫衣、牛仔裤，天气舒适。"
    elif 22 < temp <= 28:
        return "T恤、短裙、短裤，比较热。"
    else:
        return "高温预警！短袖、短裤、裙子，注意防暑降温。"

def need_umbrella(text):
    """判断是否需要带伞"""
    rain_keywords = ["雨", "雪", "阵雨", "雷阵雨", "小雨", "中雨", "大雨", "暴雨"]
    if any(keyword in text for keyword in rain_keywords):
        return "☔ 记得带伞！今天有降水。"
    return "无需带伞。"

def send_wechat(title, desp):
    """推送到微信"""
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    data = {"title": title, "desp": desp}
    response = requests.post(url, data=data)
    return response.json()

def main(push_type):
    if push_type == "morning":
        # 早上 7:00 的推送
        weather, error = get_weather()
        if error:
            send_wechat("天气获取失败", error)
            return

        advice = get_clothing_advice(weather['temp'])
        umbrella = need_umbrella(weather['text'])

        title = f"早安！今日{weather['text']}，温度{weather['temp']}℃"
        desp = f"""
### 🌤️ 今日天气
* **天气状况**：{weather['text']}
* **当前温度**：{weather['temp']}℃
* **风向风力**：{weather['windDir']} {weather['windScale']}级
* **空气质量**：{weather['aqi_category']} (AQI: {weather['aqi']})

### ☀️ 日出日落
* **日出**：{weather['sunrise']}
* **日落**：{weather['sunset']}

### 👔 穿衣指南
{advice}

### 💡 温馨提示
{umbrella}
        """
        send_wechat(title, desp)
        print("早安消息已推送")

    elif push_type == "work_am":
        # 早上 9:20 的推送
        title = "打卡提醒！"
        desp = """
### ⏰ 上班打卡提醒
别忘记打卡！迟到扣钱哦~

* **时间**：9:30前
* **事项**：打卡、查看今日待办
        """
        send_wechat(title, desp)
        print("上班打卡消息已推送")

    elif push_type == "work_pm":
        # 下午 18:00 的推送
        title = "下班打卡提醒！"
        desp = """
### 🏠 下班打卡提醒
下班啦！别忘记打卡回家~

* **时间**：18:00
* **事项**：打卡、收拾东西、注意回家安全
        """
        send_wechat(title, desp)
        print("下班打卡消息已推送")

if __name__ == "__main__":
    # 从命令行参数获取推送类型：morning, work_am, work_pm
    if len(sys.argv) > 1:
        push_type = sys.argv[1]
        main(push_type)
    else:
        print("未指定推送类型")

