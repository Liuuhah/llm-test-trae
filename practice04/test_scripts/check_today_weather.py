import urllib.request
import json

# 获取天气数据
url = 'https://wttr.in/Chengdu?format=j1'
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))

# 当前天气
current = data['current_condition'][0]
print("=" * 60)
print("📅 成都今天天气")
print("=" * 60)
print(f"观测时间: {current['observation_time']}")
print(f"温度: {current['temp_C']}°C")
print(f"体感温度: {current['FeelsLikeC']}°C")
print(f"天气: {current['weatherDesc'][0]['value']}")
print(f"湿度: {current['humidity']}%")
print(f"风力: {current['windspeedKmph']} km/h")
print(f"风向: {current['winddir16Point']}")
print(f"能见度: {current['visibility']} km")
print(f"气压: {current['pressure']} mb")
print()

# 今天的预报
today_forecast = data['weather'][0]
print("📊 今日预报:")
print(f"最高温度: {today_forecast['maxtempC']}°C")
print(f"最低温度: {today_forecast['mintempC']}°C")
print()

# 分时段
print("🕐 分时段详情:")
for hourly in today_forecast['hourly']:
    time_str = hourly['time']
    hour = int(time_str) // 100
    if hour < 6:
        period = "🌃 凌晨"
    elif hour < 12:
        period = "🌅 早晨"
    elif hour < 18:
        period = "🌤️ 中午"
    else:
        period = "🌆 傍晚"
    
    print(f"{period} ({hour}:00):")
    print(f"  温度: {hourly['tempC']}°C")
    print(f"  天气: {hourly['weatherDesc'][0]['value']}")
    print(f"  降水概率: {hourly['chanceofrain']}%")
    print()
