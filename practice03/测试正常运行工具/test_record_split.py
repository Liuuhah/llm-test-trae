"""测试记录分割逻辑的修复"""
import re

# 模拟 log.txt 文件内容
log_content = """============================================================
【记录时间】2026-04-19 11:25:52
【对话轮次】第 5 轮
============================================================
Thinking Process:

1. **Analyze the Request:**
   Task: Analyze the provided dialogue and extract key information using the 5W rule.

2. **Analyze the Dialogue Content:**
    *   User: "我来自成都东软学院" (I come from Chengdu Neusoft University)
        AI: Greeting, introduces capabilities.
    *   User: "我姓刘" (My surname is Liu)
        AI: Acknowledges surname Liu.
    *   User: "我爱打篮球" (I love playing basketball)
        AI: Discusses basketball positions, asks about preferences.

3. **Extract 5W Information:**
    - Who: 刘先生（用户）
    - What: 自我介绍，提到学校、姓氏和爱好
    - When: 初次对话
    - Where: 线上聊天
    - Why: 建立初步了解
============================================================

============================================================
【记录时间】2026-04-19 11:30:15
【对话轮次】第 10 轮
============================================================
Thinking Process:

1. **Analyze the Request:**
   Task: Continue conversation about basketball.

2. **Analyze the Dialogue Content:**
    *   User: "我经常打中锋位置"
        AI: Discusses center position strategies.
    *   User: "我喜欢看NBA比赛"
        AI: Talks about favorite NBA teams.

3. **Extract 5W Information:**
    - Who: 刘先生
    - What: 讨论篮球位置和NBA
    - When: 第二次对话
    - Where: 线上聊天
    - Why: 深入交流篮球话题
============================================================
"""

print("=" * 80)
print("测试修复后的记录分割逻辑")
print("=" * 80)

# 使用修复后的分割逻辑
records = []
current_record = []

for line in log_content.split('\n'):
    if '【记录时间】' in line:
        # 新记录开始
        if current_record:
            records.append('\n'.join(current_record).strip())
        current_record = []
    current_record.append(line)

# 添加最后一条记录
if current_record:
    records.append('\n'.join(current_record).strip())

# 过滤空记录
records = [r for r in records if r.strip() and '【记录时间】' in r]

print(f"\n✅ 分割后得到 {len(records)} 条记录\n")

# 检查每条记录是否完整
for idx, record in enumerate(records):
    print(f"--- 记录 {idx+1} ---")
    print(f"长度: {len(record)} 字符")
    
    # 检查是否包含关键部分
    has_time = '【记录时间】' in record
    has_round = '【对话轮次】' in record
    has_dialogue = 'Analyze the Dialogue Content' in record or 'Analyze the Dialogue:' in record
    has_5w = bool(re.search(r'(?:^|\n)\s*(?:-\s*)?(Who|What|When|Where|Why):', record, re.MULTILINE))
    
    print(f"  ✅ 包含时间戳: {has_time}")
    print(f"  ✅ 包含对话轮次: {has_round}")
    print(f"  ✅ 包含对话上下文: {has_dialogue}")
    print(f"  ✅ 包含5W结果: {has_5w}")
    
    # 显示前200字符
    preview = record[:200].replace('\n', '\\n')
    print(f"  预览: {preview}...")
    print()

# 验证第一条记录是否包含对话上下文
if len(records) > 0:
    first_record = records[0]
    if '我来自成都东软学院' in first_record or '我姓刘' in first_record or '我爱打篮球' in first_record:
        print("✅ 第一条记录包含完整的对话上下文！")
    else:
        print("❌ 第一条记录缺少对话上下文！")
        
    if 'Who:' in first_record or '- Who:' in first_record:
        print("✅ 第一条记录包含5W结果！")
    else:
        print("❌ 第一条记录缺少5W结果！")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
