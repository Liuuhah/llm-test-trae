"""
测试 5W 提取失败处理的两种情况
"""

print("=" * 80)
print("5W 提取失败处理方案分析")
print("=" * 80)

print("\n📋 当前逻辑分析：")
print("\n当前代码流程（chat_compress_client.py）：")
print("""
1. _check_and_extract_key_info()（第 1035 行）
   └─ 检查是否达到提取条件（每 5 轮）
   └─ 调用 _extract_5w_info()

2. _extract_5w_info()（第 1056 行）
   └─ 获取最近对话历史
   └─ 构建提示词
   └─ 调用 LLM
   └─ 解析响应
   └─ 如果成功 → 保存到日志
   └─ 如果失败 → 只打印 "❌ 提取失败"（第 1088 行）

3. _parse_extraction_response()（第 1172 行）
   └─ 检查响应是否有效
   └─ 验证是否包含 5W 关键字段
   └─ 如果不符合格式 → 返回 None

问题：
  ❌ 失败时只打印 "提取失败"，没有说明原因
  ❌ 用户不知道是内容太少还是其他问题
  ❌ 没有区分不同的失败场景
""")

print("\n" + "=" * 80)
print("🎯 你提出的两个场景")
print("=" * 80)

print("""
场景 1：对话内容信息太少，无法提取 5W
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

示例对话：
  用户：你好
  AI：你好！有什么可以帮你的吗？
  用户：今天天气怎么样？
  AI：请问您想查询哪个城市？
  用户：算了，没什么
  AI：好的，如果还有其他问题随时告诉我。
  用户：嗯
  AI：😊
  用户：好的
  AI：有什么我可以帮您的吗？
  用户：没有了

分析：
  - 这段对话缺乏实质性内容
  - 没有明确的 Who、What、When、Where、Why
  - LLM 可能返回 "未提及" 或格式错误
  
期望行为：
  ✅ 检测到信息不足
  ✅ 输出："不满足 5W 提取条件：对话内容可提取的信息太少，没有值得提取的关键信息"
  ✅ 不保存到日志文件
  ✅ 提示用户这是一次"空提取"

""")

print("""
场景 2：Token 不足或上下文太长导致提取失败
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

可能原因：
  - LLM 返回空响应
  - API 调用超时
  - 网络错误
  - 模型负载过高
  
期望行为：
  ✅ 检测到技术故障
  ✅ 输出："5W 提取失败：技术原因（token 不足/上下文过长/模型错误），请重试"
  ✅ 说明具体错误类型
  ✅ 建议用户如何处理
""")

print("\n" + "=" * 80)
print("✅ 我的建议方案")
print("=" * 80)

print("""
方案 A：智能分类失败原因（推荐）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

修改 _parse_extraction_response() 方法：

1. 检查 LLM 返回的内容
   - 如果全是 "未提及" → 场景 1（信息不足）
   - 如果包含有效信息但不符合格式 → 场景 1（信息不足）
   - 如果返回空或报错 → 场景 2（技术故障）

2. 根据不同场景输出不同消息
   - 场景 1："不满足 5W 提取条件：[具体原因]"
   - 场景 2："5W 提取失败：[技术原因]"

3. 场景 1 也保存到日志（标记为"无法提取"）
   - 便于后续查看哪些对话缺乏关键信息
   - 格式：
     【记录时间】2026-04-24 11:00:00
     【对话轮次】第 5 轮
     【提取状态】❌ 无法提取
     【原因】对话内容可提取的信息太少，没有值得提取的关键信息
     【对话摘要】用户与 AI 进行了简短的问候和闲聊...

""")

print("""
方案 B：LLM 自我判断（更智能）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

修改 Prompt，让 LLM 自己判断是否可提取：

新 Prompt 结构：
```
请分析以下对话内容，按照 5W 规则提取关键信息。

【对话内容】
{conversation_text}

【提取规则】
1. 如果对话中包含足够的实质性信息（讨论、计划、事件等），请提取 5W
2. 如果对话只是问候、闲聊、或信息太少，请输出：
   【无法提取】对话内容可提取的信息太少，没有值得提取的关键信息
3. 如果对话内容过长或超出你的处理能力，请输出：
   【无法提取】上下文太长，无法完整分析

【输出格式】
- 如果可提取：
  - Who: ...
  - What: ...
  - When: ...
  - Where: ...
  - Why: ...

- 如果无法提取：
  【无法提取】[具体原因]
```

优点：
  ✅ LLM 自己判断，更准确
  ✅ 减少误判
  ✅ 可以给出更具体的原因

缺点：
  ✅ 需要修改 Prompt
  ✅ LLM 可能判断不准确

""")

print("\n" + "=" * 80)
print("🧪 测试计划")
print("=" * 80)

print("""
测试用例 1：信息不足的对话
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输入对话：
  用户：你好
  AI：你好！
  用户：在吗？
  AI：在的
  用户：嗯
  AI：有什么事吗？
  用户：没事
  AI：好的
  用户：拜拜
  AI：再见！

期望输出：
  【无法提取】对话内容可提取的信息太少，没有值得提取的关键信息

验证点：
  ✅ 识别出信息不足
  ✅ 输出明确的原因说明
  ✅ 不保存无效数据到日志

""")

print("""
测试用例 2：有实质内容但 5W 不完整
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输入对话：
  用户：我想学习编程
  AI：很好！你想学什么语言？
  用户：Python 吧
  AI：Python 是个好选择
  用户：有什么推荐的学习资源吗？
  AI：推荐官方文档和 Codecademy
  用户：好的谢谢
  AI：不客气
  用户：那我开始学了
  AI：加油！

期望输出：
  - Who: 用户（学习者）
  - What: 计划学习 Python 编程
  - When: 未提及
  - Where: 未提及
  - Why: 个人兴趣/技能提升

验证点：
  ✅ 能提取部分 5W 信息
  ✅ "未提及"的字段正确标注
  ✅ 正常保存到日志

""")

print("""
测试用例 3：技术故障模拟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

模拟场景：
  - API 超时
  - 模型返回空响应
  - 网络错误

期望输出：
  【提取失败】技术原因：[具体错误信息]
  建议：请检查网络连接或稍后重试

验证点：
  ✅ 区分技术故障和信息不足
  ✅ 给出具体错误信息
  ✅ 提供解决建议

""")

print("\n" + "=" * 80)
print("💡 实施建议")
print("=" * 80)

print("""
步骤 1：修改 _parse_extraction_response() 方法
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

添加失败原因分类逻辑：

```python
def _parse_extraction_response(self, response_data):
    # ... 现有解析逻辑 ...
    
    if not content:
        # 场景 2：技术故障
        return None, "technical_error", "LLM 返回空响应，可能是 token 不足或模型错误"
    
    # 检查是否全是"未提及"
    unmentioned_count = content.count("未提及")
    if unmentioned_count >= 4:  # 5 个字段中有 4 个以上是"未提及"
        # 场景 1：信息不足
        return None, "insufficient_info", "对话内容可提取的信息太少，没有值得提取的关键信息"
    
    # 验证格式
    if not has_required:
        # 可能是信息不足或格式错误
        if len(content) < 50:
            return None, "insufficient_info", "返回内容过短，无法提取有效信息"
        else:
            return None, "format_error", "返回内容不符合 5W 格式要求"
    
    return content, "success", None
```

""")

print("""
步骤 2：修改 _extract_5w_info() 方法
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

处理不同的失败类型：

```python
def _extract_5w_info(self):
    # ... 现有逻辑 ...
    
    extracted_info, status, reason = self._parse_extraction_response(response_data)
    
    if status == "success":
        print("[关键信息提取] 提取成功:")
        print(extracted_info)
        self._save_to_log_file(extracted_info, rounds)
    
    elif status == "insufficient_info":
        print(f"[关键信息提取] ⚠️ 不满足提取条件：{reason}")
        # 可选：保存标记记录到日志
        self._save_failed_extraction(rounds, reason, recent_messages)
    
    elif status == "technical_error":
        print(f"[关键信息提取] ❌ 提取失败（技术原因）：{reason}")
        print("[关键信息提取] 建议：请检查网络连接或稍后重试")
    
    else:
        print(f"[关键信息提取] ❌ 提取失败：{reason}")
```

""")

print("""
步骤 3：添加 _save_failed_extraction() 方法（可选）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

保存失败记录到日志（便于追踪）：

```python
def _save_failed_extraction(self, round_number, reason, recent_messages):
    \"\"\"保存无法提取的记录到日志\"\"\"
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 生成对话摘要
    summary = self._generate_dialogue_summary(recent_messages)
    
    log_entry = f"\\n{'='*60}\\n"
    log_entry += f"【记录时间】{timestamp}\\n"
    log_entry += f"【对话轮次】第 {round_number} 轮\\n"
    log_entry += f"【提取状态】❌ 无法提取\\n"
    log_entry += f"【失败原因】{reason}\\n"
    log_entry += f"【对话摘要】{summary}\\n"
    log_entry += f"{'='*60}\\n"
    
    with open(self.log_file_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)
```

""")

print("\n" + "=" * 80)
print("🎯 我的最终建议")
print("=" * 80)

print("""
综合方案（推荐实施）：

1. ✅ 采用方案 A + B 结合
   - 修改 Prompt 让 LLM 自我判断
   - 同时在代码层面做二次验证

2. ✅ 区分 3 种失败场景
   - 信息不足（对话内容太少）
   - 格式错误（LLM 返回不符合要求）
   - 技术故障（API 错误、token 不足等）

3. ✅ 输出详细的原因说明
   - 让用户知道为什么失败
   - 提供解决建议

4. ✅ 可选：保存失败记录到日志
   - 便于后续分析和优化
   - 不会污染正常数据

5. ✅ 保持向后兼容
   - 不影响现有的成功提取逻辑
   - 只优化失败处理

实施优先级：
  P0：修改 _parse_extraction_response() 添加失败分类
  P1：修改 _extract_5w_info() 处理不同失败类型
  P2：优化 Prompt 让 LLM 自我判断
  P3：添加 _save_failed_extraction() 保存失败记录

预期效果：
  ✅ 用户清楚知道为什么无法提取
  ✅ 区分信息不足和技术故障
  ✅ 提供明确的解决建议
  ✅ 提升用户体验和系统可维护性

""")

print("\n" + "=" * 80)
print("❓ 你觉得这个方案如何？需要我做哪些调整？")
print("=" * 80)
