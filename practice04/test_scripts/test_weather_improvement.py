"""测试改进后的 curl 天气查询功能"""
import sys
sys.path.insert(0, 'f:/administrator/desktop/llm-test-trae/practice04')

from tools import Tools

# 创建工具实例
tools = Tools()

print("=" * 80)
print("测试 1: 使用 format=j1 查询明天成都天气")
print("=" * 80)

result = tools.curl("https://wttr.in/Chengdu?format=j1")

if result.get('success'):
    print("\n✅ 查询成功！\n")
    print(result['content'])
else:
    print(f"\n❌ 查询失败: {result.get('error')}")

print("\n" + "=" * 80)
print("测试 2: 不使用 format 参数（默认文本格式）")
print("=" * 80)

result2 = tools.curl("https://wttr.in/Chengdu")

if result2.get('success'):
    print("\n✅ 查询成功！返回内容前500字符：\n")
    print(result2['content'][:500])
else:
    print(f"\n❌ 查询失败: {result2.get('error')}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
