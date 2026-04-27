"""
技能系统自动化测试脚本

测试用例：
A. 默认部门测试 - 用户未提供部门，应使用"XX部"
B. 指定部门测试 - 用户提供部门，应使用指定部门
"""

import sys
import os

# 添加 practice05 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_compress_client import ChatCompressClient


def test_case_a():
    """用例 A：默认部门测试"""
    print("\n" + "="*60)
    print("测试用例 A：默认部门测试")
    print("="*60)
    
    client = ChatCompressClient()
    
    # 模拟用户输入
    user_input = "帮我写一个五一劳动节放假的通知。"
    print(f"\n[用户输入] {user_input}")
    
    # 发送请求
    response, time_taken = client.send_request_stream(user_input, debug=False)
    
    print(f"\n[AI 回复]\n{response}")
    print(f"\n[耗时] {time_taken:.2f}秒")
    
    # 验证结果
    if "**XX部通知**" in response or "XX部通知" in response:
        print("\n✅ 测试通过：使用了默认部门'XX部'")
        return True
    else:
        print("\n❌ 测试失败：未找到'XX部通知'")
        return False


def test_case_b():
    """用例 B：指定部门测试"""
    print("\n" + "="*60)
    print("测试用例 B：指定部门测试")
    print("="*60)
    
    client = ChatCompressClient()
    
    # 模拟用户输入
    user_input = "我是销售部的，请帮我写一个五一劳动节放假的通知。"
    print(f"\n[用户输入] {user_input}")
    
    # 发送请求
    response, time_taken = client.send_request_stream(user_input, debug=False)
    
    print(f"\n[AI 回复]\n{response}")
    print(f"\n[耗时] {time_taken:.2f}秒")
    
    # 验证结果
    if "**销售部通知**" in response or "销售部通知" in response:
        print("\n✅ 测试通过：使用了指定部门'销售部'")
        return True
    else:
        print("\n❌ 测试失败：未找到'销售部通知'")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Practice05: 动态技能加载系统 - 自动化测试")
    print("="*60)
    
    try:
        # 运行测试用例 A
        result_a = test_case_a()
        
        # 运行测试用例 B
        result_b = test_case_b()
        
        # 总结
        print("\n" + "="*60)
        print("测试结果总结")
        print("="*60)
        print(f"用例 A（默认部门）: {'✅ 通过' if result_a else '❌ 失败'}")
        print(f"用例 B（指定部门）: {'✅ 通过' if result_b else '❌ 失败'}")
        print("="*60)
        
        if result_a and result_b:
            print("\n🎉 所有测试通过！")
            sys.exit(0)
        else:
            print("\n⚠️  部分测试失败，请检查日志")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
