import urllib.request

# 测试不加 format 参数的返回
req = urllib.request.Request(
    'https://wttr.in/Chengdu',
    headers={'User-Agent': 'curl'}
)
response = urllib.request.urlopen(req)
content = response.read().decode('utf-8', errors='ignore')

print("=" * 80)
print("wttr.in 默认格式（无 format 参数）返回内容：")
print("=" * 80)
print(content[:2000])  # 只打印前2000字符
print("=" * 80)
