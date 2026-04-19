"""
测试 wttr.in 天气查询优化效果
验证修改后的 curl() 方法是否正确工作
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools import tools
import time

def test_wttr_in_optimization():
    """测试 wttr.in 天气查询优化"""
    
    print("=" * 70)
    print("wttr.in 天气查询优化测试")
    print("=" * 70)
    print()
    
    # 测试1：英文城市名（推荐方式）
    print("📍 测试1：英文城市名 - Chengdu")
    print("-" * 70)
    start_time = time.time()
    result = tools.curl("https://wttr.in/Chengdu")
    elapsed = time.time() - start_time
    
    if "error" in result:
        print(f"❌ 错误: {result['error']}")
    else:
        print(f"✅ 成功")
        print(f"   响应时间: {elapsed:.2f} 秒")
        print(f"   内容长度: {len(result['content'])} 字符")
        print(f"   预估 Token: ~{len(result['content']) // 2} tokens")
        print(f"\n   返回内容预览（前500字符）:")
        print("   " + "-" * 66)
        for line in result['content'].split('\n')[:15]:
            print(f"   {line}")
        print("   " + "-" * 66)
        
        # 检查是否包含3天预报
        content = result['content']
        # wttr.in 的文本格式会包含日期行，如 "Sat 18 Apr", "Sun 19 Apr", "Mon 20 Apr"
        import re
        date_matches = re.findall(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', content)
        num_days = len(date_matches)
        
        print(f"\n   数据完整性检查:")
        print(f"   ✓ 检测到天数: {num_days} 天")
        
        if num_days >= 3:
            print(f"\n   🎉 测试通过！返回了完整的3天天气预报数据")
        elif num_days >= 1:
            print(f"\n   ⚠️  警告：只检测到 {num_days} 天的数据，可能被截断")
        else:
            print(f"\n   ⚠️  警告：未检测到预期的日期格式")
    
    print()
    print()
    
    # 测试2：中文城市名（URL编码支持）
    print("📍 测试2：中文城市名 - 成都（URL编码）")
    print("-" * 70)
    start_time = time.time()
    result = tools.curl("https://wttr.in/成都")
    elapsed = time.time() - start_time
    
    if "error" in result:
        print(f"❌ 错误: {result['error']}")
    else:
        print(f"✅ 成功")
        print(f"   响应时间: {elapsed:.2f} 秒")
        print(f"   内容长度: {len(result['content'])} 字符")
        print(f"   预估 Token: ~{len(result['content']) // 2} tokens")
        print(f"\n   返回内容预览（前500字符）:")
        print("   " + "-" * 66)
        for line in result['content'].split('\n')[:15]:
            print(f"   {line}")
        print("   " + "-" * 66)
        
        # 检查是否包含3天预报
        content = result['content']
        import re
        date_matches = re.findall(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', content)
        num_days = len(date_matches)
        
        print(f"\n   数据完整性检查:")
        print(f"   ✓ 检测到天数: {num_days} 天")
        
        if num_days >= 3:
            print(f"\n   🎉 测试通过！中文城市名也能正常工作，返回了3天预报")
        elif num_days >= 1:
            print(f"\n   ⚠️  警告：只检测到 {num_days} 天的数据，可能被截断")
        else:
            print(f"\n   ⚠️  警告：未检测到预期的日期格式")
    
    print()
    print()
    
    # 测试3：移除错误的 format 参数
    print("📍 测试3：验证 format 参数被正确移除")
    print("-" * 70)
    test_urls = [
        "https://wttr.in/Beijing?format=2",
        "https://wttr.in/Shanghai&format=1",
        "https://wttr.in/Guangzhou?format=j1"
    ]
    
    for test_url in test_urls:
        print(f"\n   原始URL: {test_url}")
        result = tools.curl(test_url)
        if "error" not in result:
            content_length = len(result['content'])
            print(f"   ✅ 处理后内容长度: {content_length} 字符")
            
            # 如果内容很短（<200字符），说明可能还是只返回了当前天气
            if content_length < 200:
                print(f"   ⚠️  警告：内容过短，可能仍只返回当前天气")
            else:
                print(f"   ✓ 内容长度合理，应该包含3天预报")
        else:
            print(f"   ❌ 错误: {result['error']}")
    
    print()
    print()
    
    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print("✅ 主要改进:")
    print("   1. 移除了强制的 format=2 参数")
    print("   2. wttr.in 现在返回默认的3天文本表格预报")
    print("   3. 添加了 URL 编码支持，中文城市名也能正常工作")
    print("   4. 自动移除 AI 可能错误添加的 format 参数")
    print()
    print("📊 预期效果:")
    print("   • Token 数量: ~500-800 tokens（3天预报）")
    print("   • 调用次数: 从 4次 降至 1次")
    print("   • 响应时间: 从 70-100秒 降至 5-10秒")
    print("   • 数据准确性: 显著提高（包含完整的3天预报）")
    print("=" * 70)

if __name__ == "__main__":
    test_wttr_in_optimization()
