"""调试 wttr.in 的 Content-Type"""
import urllib.request

req = urllib.request.Request(
    'https://wttr.in/Chengdu?format=j1',
    headers={'User-Agent': 'curl'}
)
response = urllib.request.urlopen(req)

print("响应头信息：")
for key, value in response.getheaders():
    print(f"  {key}: {value}")

print(f"\nContent-Type: {response.getheader('Content-Type')}")
