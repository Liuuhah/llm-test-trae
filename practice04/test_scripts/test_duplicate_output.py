"""
重现AI重复输出问题的诊断脚本
"""
import json

# 模拟问题场景：工具调用后的消息历史
chat_history = [
    {'role': 'user', 'content': '明天成都的天气怎么样？'},
    {
        'role': 'assistant', 
        'tool_calls': [{
            'id': 'call_123',
            'type': 'function',
            'function': {
                'name': 'curl',
                'arguments': '{"url": "https://wttr.in/成都?format=j1"}'
            }
        }]
    },
    {
        'role': 'tool',
        'tool_call_id': 'call_123',
        'name': 'curl',
        'content': '{"weather_data": "...格式化后的天气信息..."}'
    }
]

print("=" * 80)
print("问题诊断：AI 重复输出的根本原因")
print("=" * 80)

print("\n📋 当前的聊天历史结构：")
for i, msg in enumerate(chat_history):
    print(f"\n[{i}] role: {msg['role']}")
    if msg['role'] == 'assistant' and 'tool_calls' in msg:
        print(f"    tool_calls: {json.dumps(msg['tool_calls'], ensure_ascii=False, indent=6)}")
    elif msg['role'] == 'tool':
        print(f"    tool_call_id: {msg.get('tool_call_id')}")
        print(f"    name: {msg.get('name')}")
        print(f"    content: {msg.get('content')[:100]}...")
    else:
        print(f"    content: {msg.get('content')[:50]}...")

print("\n\n" + "=" * 80)
print("🔍 问题分析")
print("=" * 80)

print("""
当工具调用执行后，代码会：

1. 在 chat_history 中添加 assistant 的 tool_calls 消息（第881-890行）
2. 在 chat_history 中添加 tool 的执行结果消息（第893-897行）
3. 重新发送请求时，使用 self.chat_history 构建 messages_list（第921行）
4. 同时还会添加 {'role': 'user', 'content': prompt}（第922行）

关键问题在于：
❌ 第二次请求时，messages_list 包含了：
   - system message
   - 完整的 chat_history（包含 user、assistant+tool_calls、tool）
   - 再次添加的 user prompt

这导致 LLM 看到的上下文是：
   User: 明天成都的天气怎么样？
   Assistant: [tool_calls]
   Tool: [weather data]
   User: 明天成都的天气怎么样？  ← 重复了！

LLM 可能会认为需要重新回答整个问题，导致重复输出。
""")

print("\n" + "=" * 80)
print("✅ 解决方案")
print("=" * 80)

print("""
方案1：在重新构建请求时，不重复添加 user prompt
   - 检查 chat_history 最后一条是否已经是当前 prompt
   - 如果是，就不再添加

方案2：在 _execute_pending_tool_call 中，使用与 _send_single_stream 相同的逻辑
   - 复用 _clean_message_sequence
   - 复用重复检测逻辑

方案3（推荐）：统一消息构建逻辑
   - 提取一个公共方法 build_messages(prompt)
   - 所有地方都调用这个方法，确保一致性
""")

print("\n" + "=" * 80)
print("🎯 立即修复建议")
print("=" * 80)

print("""
修改 _execute_pending_tool_call 方法（第910-923行）：

将：
    data['messages'] = [
        {'role': 'system', 'content': '...'},
        *self.chat_history,
        {'role': 'user', 'content': prompt}  # ❌ 可能重复
    ]

改为：
    cleaned_history = self._clean_message_sequence(self.chat_history)
    
    messages_list = [{'role': 'system', 'content': '...'}]
    
    # 检查是否已包含当前 prompt
    if cleaned_history and cleaned_history[-1].get('role') == 'user' and cleaned_history[-1].get('content') == prompt:
        messages_list.extend(cleaned_history)
    else:
        messages_list.extend(cleaned_history)
        messages_list.append({'role': 'user', 'content': prompt})
    
    data['messages'] = messages_list
""")
