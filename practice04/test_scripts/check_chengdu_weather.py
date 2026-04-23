import urllib.request
import json
from datetime import datetime

# 查询成都天气
req = urllib.request.Request(
    'https://wttr.in/Chengdu?format=j1',
    headers={'User-Agent': 'curl'}
)
response = urllib.request.urlopen(req)
data = json.loads(response.read().decode('utf-8'))

# 获取明天的天气（索引1）
tomorrow = data['weather'][1]
date_str = tomorrow['date']

# 提取四个时间段的数据（每6小时一个时段）
hourly_data = tomorrow['hourly']

# 映射时间段
time_periods = {
    '00:00': '🌙 夜间',
    '03:00': '🌙 凌晨',
    '06:00': '🌅 早晨',
    '09:00': '☀️ 上午',
    '12:00': '🌤️ 中午',
    '15:00': '⛅ 下午',
    '18:00': '🌆 傍晚',
    '21:00': '🌃 夜间'
}

# 选择四个关键时段
morning = hourly_data[2]   # 06:00 早晨
noon = hourly_data[4]      # 12:00 中午
evening = hourly_data[6]   # 18:00 傍晚
night = hourly_data[7]     # 21:00 夜间

def format_period(period_data, period_name):
    """格式化单个时段的信息"""
    time = period_data['time']
    temp = period_data['tempC']
    weather_desc = period_data['weatherDesc'][0]['value']
    wind_speed = period_data['windspeedKmph']
    humidity = period_data['humidity']
    precip_chance = period_data.get('chanceofrain', '0')
    
    return {
        'name': period_name,
        'time': time,
        'weather': weather_desc,
        'temp': f"{temp}°C",
        'wind': f"{wind_speed} km/h",
        'humidity': f"{humidity}%",
        'precip': f"{precip_chance}%"
    }

# 生成四个时段的信息
periods = [
    format_period(morning, '🌅 早晨'),
    format_period(noon, '🌤️ 中午'),
    format_period(evening, '🌆 傍晚'),
    format_period(night, '🌃 夜间')
]

# 计算整体温度范围
all_temps = [int(h['tempC']) for h in hourly_data]
max_temp = max(all_temps)
min_temp = min(all_temps)
avg_temp = sum(all_temps) // len(all_temps)

# 输出格式化结果
print(f"📅 明天成都天气预报 ({date_str})")
print(f"{'='*60}")
print(f"\n🌡️  整体概况：")
print(f"   平均温度: {avg_temp}°C | 最高: {max_temp}°C | 最低: {min_temp}°C")
print(f"\n{'='*60}")
print(f"\n🕐 分时段详情：\n")

for p in periods:
    print(f"{p['name']} ({p['time']})")
    print(f"   天气: {p['weather']}")
    print(f"   温度: {p['temp']} | 风力: {p['wind']} | 湿度: {p['humidity']}")
    print(f"   降水概率: {p['precip']}")
    print()

print(f"{'='*60}")
print(f"\n💡 出行建议：")

# 根据天气生成建议
if int(morning['chanceofrain']) > 50:
    print("   ☔️  早晨有雨，建议携带雨伞")
else:
    print("   ✅ 早晨天气良好")

if avg_temp < 20:
    print("   🧥 温度较低，建议穿外套")
elif avg_temp > 25:
    print("   👕 温度较高，建议穿短袖")
else:
    print("   👔 温度舒适，建议穿长袖T恤或薄外套")

if int(evening['windspeedKmph']) > 15:
    print("   💨 傍晚风力较大，注意防风")
else:
    print("   💨 风力较小，体感舒适")

print(f"\n{'='*60}")
