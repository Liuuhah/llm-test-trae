"""测试 _clean_extraction_content 方法的清理效果"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools import Tools

# 模拟 LLM 返回的完整内容（包含 Thinking Process）
test_content_1 = """Thinking Process:

1.  **Analyze the Request:**
    *   Task: Analyze the provided dialogue and extract key information using the 5W rule (Who, What, When, Where, Why).
    *   Input: A conversation between a User and an AI Assistant.
    *   Output Format: Strictly follow the specified format (each field on one line, specific labels).
    *   Constraints:
        *   Only extract explicitly mentioned information (no speculation).
        *   Keep it concise (max 50 characters per field).
        *   Extract the most important information if repeated.
        *   Use Chinese.
        *   No extra explanations.

2.  **Analyze the Dialogue Content:**
    *   User: "我来自成都东软学院" (I come from Chengdu Neusoft University)
    *   AI: Greeting, introduces capabilities.
    *   User: "我姓刘" (My surname is Liu)
    *   AI: Acknowledges surname Liu.
    *   User: "我爱打篮球" (I love playing basketball)
    *   AI: Discusses basketball positions, asks about preferences.
    *   User: "我是中锋" (I am a center)
    *   AI: Responds about center position.
    *   User: "我是男的" (I am male)
    *   AI: Greeting, summarizes profile.

3.  **Extract Information based on 5W:**
    Based on the dialogue:
    - Who: The user is Mr. Liu (刘先生), male, from Chengdu Neusoft University.
    - What: Self-introduction and seeking assistant's help.
    - When: Not mentioned.
    - Where: Chengdu Neusoft (成都东软).
    - Why: Not explicitly mentioned.

- Who: 刘先生
- What: 用户进行自我介绍并寻求助手协助
- When: 未提及
- Where: 成都东软
- Why: 未提及"""

# 测试用例2：只有对话分析，没有标准格式的5W
test_content_2 = """Thinking Process:

1.  **Analyze the Request:**
    *   Task description...

2.  **Analyze the Dialogue:**
    *   Msg 1 (User): I am from Chengdu Neusoft University (我来自成都东软学院).
    *   Msg 2 (AI): Greeting, confirms user is a student there, offers help.
    *   Msg 3 (User): My surname is Liu (我姓刘).
    *   Msg 4 (AI): Greets Mr. Liu/Student Liu, offers help.
    *   Msg 5 (User): I love playing basketball (我爱打篮球).
    *   Msg 6 (AI): Responds to basketball interest, asks where they play.
    *   Msg 7 (User): I am a Center (我是中锋).
    *   Msg 8 (AI): Acknowledges position, offers help with files/weather/etc.
    *   Msg 9 (User): I am male (我是男的).
    *   Msg 10 (AI): Greets Mr. Liu again, asks about other hobbies/needs.

3.  **Extract 5W Information:**
    *   **Who:** The user is identified as "Liu" (刘) and a student from Chengdu Neusoft University (成都东软学院). Role: Student/User.
    *   **What:** The core topic is the user introducing themselves.
    *   **When:** Not mentioned.
    *   **Where:** Chengdu Neusoft University.
    *   **Why:** Seeking assistance.

Who: 刘先生
What: 用户进行自我介绍
When: 未提及
Where: 成都东软学院
Why: 寻求助手协助"""

# 测试用例3：标准格式（带 - 前缀）
test_content_3 = """Thinking Process:
Some analysis here...

- Who: 张三
- What: 询问天气情况
- When: 今天下午
- Where: 北京
- Why: 准备出门"""

def test_clean_extraction():
    """测试清理提取内容的功能"""
    tools = Tools()
    
    print("=" * 80)
    print("测试1：完整的 Thinking Process（包含对话分析和5W结果）")
    print("=" * 80)
    result1 = tools._clean_extraction_content(test_content_1)
    print("\n清理后的内容：")
    print(result1)
    print("\n" + "-" * 80)
    print(f"原始长度: {len(test_content_1)} 字符")
    print(f"清理后长度: {len(result1)} 字符")
    print(f"压缩率: {(1 - len(result1)/len(test_content_1)) * 100:.1f}%")
    
    # 检查是否保留了关键信息
    checks = [
        ("对话上下文", "Analyze the Dialogue Content" in result1 or "Analyze the Dialogue:" in result1),
        ("5W结果 - Who", "Who:" in result1),
        ("5W结果 - What", "What:" in result1),
        ("冗余思考过程", "Analyze the Request" not in result1),
    ]
    
    print("\n检查结果：")
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}: {'通过' if passed else '失败'}")
    
    print("\n" + "=" * 80)
    print("测试2：非标准格式的5W结果（Who: 而不是 - Who:）")
    print("=" * 80)
    result2 = tools._clean_extraction_content(test_content_2)
    print("\n清理后的内容：")
    print(result2)
    print("\n" + "-" * 80)
    print(f"原始长度: {len(test_content_2)} 字符")
    print(f"清理后长度: {len(result2)} 字符")
    print(f"压缩率: {(1 - len(result2)/len(test_content_2)) * 100:.1f}%")
    
    checks2 = [
        ("对话上下文", "Analyze the Dialogue" in result2),
        ("5W结果 - Who", "Who:" in result2),
        ("冗余思考过程", "Analyze the Request" not in result2),
    ]
    
    print("\n检查结果：")
    for check_name, passed in checks2:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}: {'通过' if passed else '失败'}")
    
    print("\n" + "=" * 80)
    print("测试3：标准格式的5W结果（带 - 前缀）")
    print("=" * 80)
    result3 = tools._clean_extraction_content(test_content_3)
    print("\n清理后的内容：")
    print(result3)
    print("\n" + "-" * 80)
    print(f"原始长度: {len(test_content_3)} 字符")
    print(f"清理后长度: {len(result3)} 字符")
    print(f"压缩率: {(1 - len(result3)/len(test_content_3)) * 100:.1f}%")
    
    checks3 = [
        ("5W结果 - Who", "- Who:" in result3 or "Who:" in result3),
        ("5W结果 - What", "- What:" in result3 or "What:" in result3),
        ("冗余思考过程", "Thinking Process" not in result3),
    ]
    
    print("\n检查结果：")
    for check_name, passed in checks3:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}: {'通过' if passed else '失败'}")
    
    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    test_clean_extraction()
