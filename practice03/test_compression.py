"""
聊天压缩功能测试脚本
用于自动测试聊天记录压缩功能
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from practice03.chat_compress_client import ChatCompressClient

def test_compression():
    """测试聊天压缩功能"""
    print("=" * 60)
    print("聊天压缩功能测试")
    print("=" * 60)
    
    client = ChatCompressClient()
    
    # 测试1: 检查初始状态
    print("\n[测试1] 初始状态检查")
    client.show_history_stats()
    
    # 测试2: 添加多条消息模拟对话
    print("\n[测试2] 模拟多轮对话（超过5轮）")
    test_messages = [
        ("你好，我想了解一下Python编程", "Python是一种广泛使用的高级编程语言..."),
        ("Python有哪些主要特点？", "Python的主要特点包括：简洁易读、跨平台..."),
        ("能介绍一下Python的应用领域吗？", "Python广泛应用于Web开发、数据科学..."),
        ("我想学习数据分析，应该怎么开始？", "学习Python数据分析可以从以下几个步骤开始..."),
        ("推荐一些学习资源吧", "推荐的学习资源包括：官方文档、Coursera课程..."),
        ("谢谢你的建议", "不客气！祝你学习顺利！"),
        ("还有一个问题，Python和Java有什么区别？", "Python和Java的主要区别在于..."),
    ]
    
    for i, (user_msg, ai_response) in enumerate(test_messages, 1):
        client.add_to_history('user', user_msg)
        client.add_to_history('assistant', ai_response)
        print(f"  第{i}轮对话已添加")
        
        # 检查是否需要压缩
        if client._should_compress():
            print(f"\n  >>> 触发压缩条件！")
            client._compress_chat_history()
            client.show_history_stats()
    
    # 测试3: 显示最终状态
    print("\n[测试3] 压缩后最终状态")
    client.show_history_stats()
    
    # 测试4: 验证保留的消息
    print("\n[测试4] 验证保留的最近消息")
    if len(client.chat_history) > 0:
        print(f"聊天历史中共有 {len(client.chat_history)} 条消息")
        # 显示最后几条消息
        for i, msg in enumerate(client.chat_history[-4:], max(0, len(client.chat_history)-3)):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            if isinstance(content, str) and len(content) > 50:
                content = content[:50] + "..."
            print(f"  消息{i+1} [{role}]: {content}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_compression()
