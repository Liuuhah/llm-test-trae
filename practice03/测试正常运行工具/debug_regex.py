import re

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

# 测试正则表达式
dialogue_match = re.search(r'(?:2\.\s*)?\*?\*?Analyze the Dialogue (?:Content)?:', test_content_2)
print("找到对话分析:", dialogue_match is not None)
if dialogue_match:
    print("位置:", dialogue_match.start())
    print("匹配内容:", repr(dialogue_match.group()))

five_w_match = re.search(r'(?:^|\n)\s*-\s*(Who|What|When|Where|Why):', test_content_2, re.MULTILINE)
print("\n找到带 - 的5W:", five_w_match is not None)

if not five_w_match:
    five_w_match = re.search(r'(?:^|\n)(Who|What|When|Where|Why):', test_content_2, re.MULTILINE)
    print("找到不带 - 的5W:", five_w_match is not None)
    if five_w_match:
        print("位置:", five_w_match.start())
        print("匹配内容:", repr(five_w_match.group()))

print("\n对话分析位置:", dialogue_match.start() if dialogue_match else "None")
print("5W结果位置:", five_w_match.start() if five_w_match else "None")

if dialogue_match and five_w_match:
    print("\n对话分析在5W之前:", dialogue_match.start() < five_w_match.start())
