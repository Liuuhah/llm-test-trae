import urllib.request
import json

# 获取天气数据
url = 'https://wttr.in/Chengdu?format=j1'
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))

# 明天的预报（weather[1] 是明天）
tomorrow_forecast = data['weather'][1]
date = tomorrow_forecast['date']

print("=" * 60)
print(f"📅 成都明天天气 ({date})")
print("=" * 60)
print(f"最高温度: {tomorrow_forecast['maxtempC']}°C")
print(f"最低温度: {tomorrow_forecast['mintempC']}°C")
print(f"平均温度: {tomorrow_forecast['avgtempC']}°C")
print()

# 分时段详情
print("🕐 分时段详情:")
print("-" * 60)

for hourly in tomorrow_forecast['hourly']:
    time_str = hourly['time']
    hour = int(time_str) // 100
    
    # 判断时段
    if 6 <= hour < 12:
        period = "🌅 早晨"
    elif 12 <= hour < 18:
        period = "🌤️ 中午"
    else:
        continue  # 只显示早中晚
    
    weather_desc = hourly['weatherDesc'][0]['value']
    temp = hourly['tempC']
    feels_like = hourly['FeelsLikeC']
    humidity = hourly['humidity']
    wind_speed = hourly['windspeedKmph']
    wind_dir = hourly['winddir16Point']
    chance_of_rain = hourly['chanceofrain']
    
    print(f"\n{period} ({hour}:00):")
    print(f"  🌡️  温度: {temp}°C (体感 {feels_like}°C)")
    print(f"  ☁️  天气: {weather_desc}")
    print(f"  💧 湿度: {humidity}%")
    print(f"  💨 风力: {wind_speed} km/h ({wind_dir})")
    print(f"  🌧️  降水概率: {chance_of_rain}%")

print("\n" + "=" * 60)

# 出行建议
print("\n💡 出行建议:")
max_temp = int(tomorrow_forecast['maxtempC'])
min_temp = int(tomorrow_forecast['mintempC'])

if max_temp > 30:
    print("  👕 温度较高，建议穿轻薄透气的衣物")
elif max_temp > 25:
    print("  👕 温度温暖，建议穿短袖或薄长袖")
elif max_temp > 20:
    print("  👕 温度舒适，建议穿长袖或薄外套")
else:
    print("  🧥 温度较低，建议穿厚外套")

# 检查是否有雨
has_rain = any(int(h['chanceofrain']) > 50 for h in tomorrow_forecast['hourly'])
if has_rain:
    print("  ☂️  部分地区有降雨可能，建议携带雨伞")
else:
    print("  ✅ 全天无雨，适合户外活动")

print("=" * 60)
