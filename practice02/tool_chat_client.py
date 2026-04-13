import os
import json
import time
import http.client
from urllib.parse import urlparse
import re
from tools import tools

class ToolChatClient:
    def __init__(self):
        self.config = self._load_config()
        self.base_url = self.config.get('BASE_URL')
        self.model = self.config.get('MODEL')
        self.token = self.config.get('TOKEN')
        self._parse_base_url()
        self.chat_history = []
        self.tools = self._register_tools()
        self.system_prompt = self._generate_system_prompt()
    
    def _generate_system_prompt(self):
        """生成包含工具功能描述的系统提示词"""
        prompt = """
你是一个友好的AI助手，具有文件操作能力。当用户需要进行文件操作时，请使用工具调用格式。

你可以使用以下工具：

1. list_directory
   - 功能：列出指定目录下的所有文件和子目录，包括文件的基本属性（大小、修改时间等）
   - 参数：directory_path（要列出的目录路径）
   - 示例：当用户说"请列出practice02目录下的文件"时，使用此工具

2. rename_file
   - 功能：修改某个目录下某个文件的名字
   - 参数：directory_path（文件所在目录路径）、old_filename（旧文件名）、new_filename（新文件名）
   - 示例：当用户说"请将practice02目录下的test.txt改名为new_test.txt"时，使用此工具

3. delete_file
   - 功能：删除某个目录下某个文件
   - 参数：directory_path（文件所在目录路径）、filename（要删除的文件名）
   - 示例：当用户说"请删除practice02目录下的test.txt文件"时，使用此工具

4. create_file
   - 功能：在某个目录下新建一个文件，并且写入内容
   - 参数：directory_path（要创建文件的目录路径）、filename（要创建的文件名）、content（要写入文件的内容，可选）
   - 示例：当用户说"请在practice02目录下新建一个test.txt文件，内容为'Hello World'"时，使用此工具

5. read_file
   - 功能：读取某个目录下面的某个文件的内容
   - 参数：directory_path（文件所在目录路径）、filename（要读取的文件名）
   - 示例：当用户说"请读取practice02目录下的test.txt文件内容"时，使用此工具

6. curl
   - 功能：通过curl访问网页，并返回网页内容
   - 参数：url（要访问的网页URL）
   - 示例：当用户说"请访问百度首页并返回内容"时，使用此工具

使用工具的格式：
<tool_call>
<function=工具名称>
<参数名1>=参数值1
<参数名2>=参数值2
...</function>
</tool_call>

请根据用户的请求，选择合适的工具并正确填写参数。
"""
        return prompt
    
    def _register_tools(self):
        """注册可用工具"""
        tools_list = [
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "列出指定目录下的所有文件和子目录，包括文件的基本属性（大小、修改时间等）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "要列出的目录路径"
                            }
                        },
                        "required": ["directory_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "rename_file",
                    "description": "修改某个目录下某个文件的名字",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "文件所在目录路径"
                            },
                            "old_filename": {
                                "type": "string",
                                "description": "旧文件名"
                            },
                            "new_filename": {
                                "type": "string",
                                "description": "新文件名"
                            }
                        },
                        "required": ["directory_path", "old_filename", "new_filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "删除某个目录下某个文件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "文件所在目录路径"
                            },
                            "filename": {
                                "type": "string",
                                "description": "要删除的文件名"
                            }
                        },
                        "required": ["directory_path", "filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "在某个目录下新建一个文件，并且写入内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "要创建文件的目录路径"
                            },
                            "filename": {
                                "type": "string",
                                "description": "要创建的文件名"
                            },
                            "content": {
                                "type": "string",
                                "description": "要写入文件的内容"
                            }
                        },
                        "required": ["directory_path", "filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "读取某个目录下面的某个文件的内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "文件所在目录路径"
                            },
                            "filename": {
                                "type": "string",
                                "description": "要读取的文件名"
                            }
                        },
                        "required": ["directory_path", "filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "curl",
                    "description": "通过curl访问网页，并返回网页内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "要访问的网页URL"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        ]
        return tools_list
    
    def execute_tool(self, tool_name, tool_args):
        """执行工具调用"""
        if tool_name == "list_directory":
            return tools.list_directory(tool_args.get("directory_path"))
        elif tool_name == "rename_file":
            return tools.rename_file(
                tool_args.get("directory_path"),
                tool_args.get("old_filename"),
                tool_args.get("new_filename")
            )
        elif tool_name == "delete_file":
            return tools.delete_file(
                tool_args.get("directory_path"),
                tool_args.get("filename")
            )
        elif tool_name == "create_file":
            return tools.create_file(
                tool_args.get("directory_path"),
                tool_args.get("filename"),
                tool_args.get("content", "")
            )
        elif tool_name == "read_file":
            return tools.read_file(
                tool_args.get("directory_path"),
                tool_args.get("filename")
            )
        elif tool_name == "curl":
            return tools.curl(
                tool_args.get("url")
            )
        return {"error": f"未知工具: {tool_name}"}
    
    def _load_config(self):
        config = {}
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if not os.path.exists(env_path):
            print(f"错误: 在 {env_path} 未找到 .env 文件")
            print("请将 env.example 复制为 .env 并填写配置信息")
            exit(1)
        
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"')
        
        return config
    
    def _parse_base_url(self):
        parsed = urlparse(self.base_url)
        self.host = parsed.netloc
        self.path = parsed.path.rstrip('/')
    
    def send_request_stream(self, prompt, max_tokens=262144, debug=False):
        """发送流式请求，实时输出回复内容"""
        start_time = time.time()
        
        if self.base_url.startswith('https://'):
            conn = http.client.HTTPSConnection(self.host)
        else:
            conn = http.client.HTTPConnection(self.host)
        
        headers = {
            'Content-Type': 'application/json'
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': self.system_prompt},
                *self.chat_history,
                {'role': 'user', 'content': prompt}
            ],
            'tools': self.tools,
            'tool_choice': 'auto',
            'max_tokens': max_tokens,
            'temperature': 0.6,
            'stream': True
        }
        
        conn.request('POST', f'{self.path}/chat/completions', json.dumps(data), headers)
        response = conn.getresponse()
        
        full_content = ''
        buffer = ''
        
        # 准备日志文件
        if debug:
            log_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'chat_{time.strftime("%Y%m%d_%H%M%S")}.txt')
            print(f"调试模式已启用，输出将保存到: {log_file}")
        
        tool_calls = []
        tool_call_id = None
        
        try:
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                
                buffer += chunk.decode('utf-8', errors='ignore')
                
                # 处理SSE格式数据
                lines = buffer.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('data: '):
                        json_str = line[6:].strip()
                        if json_str == '[DONE]':
                            continue
                        
                        try:
                            chunk_data = json.loads(json_str)
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                choice = chunk_data['choices'][0]
                                delta = choice.get('delta', {})
                                
                                # 检测工具调用请求
                                if 'tool_calls' in delta:
                                    tool_call = delta['tool_calls'][0]
                                    tool_calls.append(tool_call)
                                    
                                    # 从所有tool_calls中查找工具名称和参数
                                    tool_name = None
                                    tool_args = {}
                                    
                                    # 先检查当前tool_call
                                    if 'function' in tool_call:
                                        if 'name' in tool_call['function']:
                                            tool_name = tool_call['function']['name']
                                        if 'arguments' in tool_call['function'] and tool_call['function']['arguments']:
                                            try:
                                                tool_args = json.loads(tool_call['function']['arguments'])
                                            except:
                                                pass
                                    
                                    # 如果当前tool_call没有名称，从之前的tool_calls中查找
                                    if not tool_name and tool_calls:
                                        for tc in tool_calls:
                                            if 'function' in tc and 'name' in tc['function']:
                                                tool_name = tc['function']['name']
                                                break
                                    
                                    # 确保tool_call_id
                                    tool_call_id = tool_call.get('id') or (tool_calls[0].get('id') if tool_calls else None)
                                    
                                    # 打印原始tool_call数据进行调试
                                    print(f"\n原始tool_call数据: {json.dumps(tool_call, ensure_ascii=False)}")
                                    
                                    print(f"工具调用: {tool_name}")
                                    print(f"参数: {tool_args}")
                                    
                                    # 执行工具（处理大小写）
                                    if tool_name:
                                        # 转换为小写以匹配工具名称
                                        normalized_tool_name = tool_name.lower()
                                        tool_result = self.execute_tool(normalized_tool_name, tool_args)
                                        
                                        print(f"工具执行结果: {tool_result}")
                                        
                                        # 将工具执行结果添加到聊天历史
                                        self.add_to_history('assistant', {
                                            'tool_calls': [{
                                                'id': tool_call_id,
                                                'type': 'function',
                                                'function': {
                                                    'name': tool_name,
                                                    'arguments': json.dumps(tool_args)
                                                }
                                            }]
                                        })
                                        
                                        # 发送工具执行结果
                                        self.add_to_history('tool', {
                                            'tool_call_id': tool_call_id,
                                            'name': tool_name,
                                            'content': json.dumps(tool_result)
                                        })
                                        
                                        # 重新发送请求获取最终响应
                                        print("AI: ", end='', flush=True)
                                        conn.close()
                                        
                                        # 重新构建请求
                                        if self.base_url.startswith('https://'):
                                            conn = http.client.HTTPSConnection(self.host)
                                        else:
                                            conn = http.client.HTTPConnection(self.host)
                                        
                                        # 重新构建请求时禁用工具调用
                                        data['messages'] = [
                                            {'role': 'system', 'content': self.system_prompt},
                                            *self.chat_history,
                                            {'role': 'user', 'content': prompt}
                                        ]
                                        # 禁用工具调用，因为已经执行过了
                                        data['tool_choice'] = 'none'
                                        
                                        conn.request('POST', f'{self.path}/chat/completions', json.dumps(data), headers)
                                        response = conn.getresponse()
                                        buffer = ''
                                        tool_calls = []
                                        tool_call_id = None
                                        continue
                                    else:
                                        # 工具名称为空，忽略这个请求
                                        print(f"工具名称为空，忽略工具调用请求")
                                        continue
                                
                                # 正常文本内容
                                content = delta.get('content', '')
                                if content:
                                    print(content, end='', flush=True)
                                    full_content += content
                                    # 写入日志文件
                                    if debug:
                                        with open(log_file, 'a', encoding='utf-8') as f:
                                            f.write(content)
                        except json.JSONDecodeError as e:
                            pass
                
                # 保留未处理的部分
                if len(lines) > 0:
                    buffer = lines[-1]
                else:
                    buffer = ''
        except KeyboardInterrupt:
            print('\n\n用户中断')
        finally:
            conn.close()
        
        # 完成后写入完整内容到日志
        if debug:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write('\n\n===== 完整对话 =====\n')
                f.write(f'用户: {prompt}\n')
                f.write(f'AI: {full_content}\n')
        
        # 如果没有获取到内容，尝试从完整响应中提取
        if not full_content:
            try:
                # 重新发送非流式请求获取完整响应
                if self.base_url.startswith('https://'):
                    conn = http.client.HTTPSConnection(self.host)
                else:
                    conn = http.client.HTTPConnection(self.host)
                
                data['stream'] = False
                conn.request('POST', f'{self.path}/chat/completions', json.dumps(data), headers)
                response = conn.getresponse()
                response_data = json.loads(response.read().decode())
                conn.close()
                
                if 'error' not in response_data:
                    message = response_data['choices'][0]['message']
                    content = message.get('content', '').strip()
                    if content:
                        full_content = content
                    else:
                        # 尝试从reasoning_content中提取
                        reasoning_content = message.get('reasoning_content', '')
                        if reasoning_content:
                            # 尝试不同的提取模式
                            patterns = [
                                r'Final Selection:.*?["\']([^"\']*?[\u4e00-\u9fff]+[^"\']*?)["\']',
                                r'Final Polish:.*?["\']([^"\']*?[\u4e00-\u9fff]+[^"\']*?)["\']',
                                r'最终选择:.*?["\']([^"\']*?[\u4e00-\u9fff]+[^"\']*?)["\']',
                                r'最终润色:.*?["\']([^"\']*?[\u4e00-\u9fff]+[^"\']*?)["\']'
                            ]
                            for pattern in patterns:
                                match = re.search(pattern, reasoning_content, re.DOTALL)
                                if match:
                                    full_content = match.group(1).strip()
                                    break
                            
                            if not full_content:
                                # 尝试直接提取中文句子
                                chinese_sentences = re.findall(r'[\u4e00-\u9fff][\u4e00-\u9fff，。！？；：""\'\'（）\s]*[。！？]', reasoning_content)
                                if chinese_sentences:
                                    full_content = ''.join(chinese_sentences)
            except Exception as e:
                print(f"获取完整响应失败: {e}")
        
        if not full_content:
            full_content = '抱歉，模型没有返回有效内容。'
        
        print()
        end_time = time.time()
        total_time = end_time - start_time
        
        return full_content, total_time
    
    def add_to_history(self, role, content):
        """添加消息到聊天历史"""
        if role == 'assistant' and isinstance(content, dict) and 'tool_calls' in content:
            self.chat_history.append({'role': role, **content})
        elif role == 'tool' and isinstance(content, dict):
            self.chat_history.append({'role': role, **content})
        else:
            self.chat_history.append({'role': role, 'content': content})
        
        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]
    
    def clear_history(self):
        """清空聊天历史"""
        self.chat_history = []
        print("聊天历史已清空")
    
    def run(self):
        """运行交互式聊天界面"""
        print("=" * 60)
        print("LLM 工具调用聊天客户端")
        print("=" * 60)
        print(f"模型: {self.model}")
        print(f"API地址: {self.base_url}")
        print("=" * 60)
        print("可用工具:")
        print("1. list_directory - 列出目录文件")
        print("2. rename_file - 修改文件名")
        print("3. delete_file - 删除文件")
        print("4. create_file - 新建文件")
        print("5. read_file - 读取文件内容")
        print("6. curl - 访问网页并返回内容")
        print("=" * 60)
        print("输入消息开始聊天，输入 'exit' 或 'quit' 退出")
        print("输入 'clear' 清空聊天历史")
        print("输入 'debug' 启用调试模式（保存输出到文件）")
        print("按 Ctrl+C 随时退出")
        print("=" * 60)
        print()
        
        debug_mode = False
        
        while True:
            try:
                user_input = input("你: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("再见！")
                    break
                
                if user_input.lower() == 'clear':
                    self.clear_history()
                    continue
                
                if user_input.lower() == 'debug':
                    debug_mode = not debug_mode
                    status = "已启用" if debug_mode else "已禁用"
                    print(f"调试模式{status}")
                    continue
                
                self.add_to_history('user', user_input)
                
                print("AI: ", end='', flush=True)
                response, time_taken = self.send_request_stream(user_input, debug=debug_mode)
                
                if response:
                    self.add_to_history('assistant', response)
                    print(f"[耗时: {time_taken:.2f}秒]")
                else:
                    print("\n抱歉，模型没有返回有效内容。")
                    self.chat_history.pop()
                
                print()
                
            except KeyboardInterrupt:
                print("\n\n收到中断信号，退出聊天...")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")
                print("请重试或输入 'exit' 退出")
                print()

if __name__ == "__main__":
    client = ToolChatClient()
    client.run()
