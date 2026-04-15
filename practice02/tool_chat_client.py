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
   
   ⚠️ wttr.in天气预报API使用说明（非常重要，请仔细阅读）：
   - 获取3天天气预报（今天、明天、后天）：https://wttr.in/城市名?format=j1
   - 返回JSON格式，包含weather数组：
     * weather[0] = 今天的天气
     * weather[1] = 明天的天气 ← 用户问"明天"时用这个！
     * weather[2] = 后天的天气
   - 每天的数据包含：
     * maxtempC: 最高温度（°C）
     * mintempC: 最低温度（°C）
     * avgtempC: 平均温度（°C）
   - 当用户询问"明天"的天气预报时，必须使用?format=j1，然后从weather[1]中读取数据
   - 示例：https://wttr.in/Chengdu?format=j1

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
        full_content = ''
        
        # 支持多轮工具调用的循环
        max_tool_rounds = 3  # 最多处理3轮工具调用
        
        for round_num in range(max_tool_rounds):
            if round_num > 0:
                if debug:
                    print(f"\n[调试] 第{round_num + 1}轮工具调用...")
            
            content, has_tool_call = self._send_single_stream(
                prompt, max_tokens, debug, round_num == 0
            )
            
            if content:
                full_content = content
            
            # 如果没有工具调用，或者已经达到最大轮数，退出循环
            if not has_tool_call or round_num >= max_tool_rounds - 1:
                break
        
        print()
        end_time = time.time()
        total_time = end_time - start_time
        
        return full_content, total_time
    
    def _send_single_stream(self, prompt, max_tokens, debug, is_first_round):
        """发送单次流式请求，返回(内容, 是否有工具调用)"""
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
        
        # 工具调用缓冲区
        tool_calls_buffer = {}  # 按index存储tool_call的累积数据
        pending_tool_calls = []  # 存储完整的tool_call，等待执行
        tool_call_response = ''  # 存储工具调用后AI的最终响应
        
        # 准备日志文件
        if debug:
            log_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'chat_{time.strftime("%Y%m%d_%H%M%S")}.txt')
            print(f"调试模式已启用，输出将保存到: {log_file}")
        
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
                            # 流式响应结束，检查并执行待处理的工具调用
                            if pending_tool_calls:
                                for tool_call_data in pending_tool_calls:
                                    response_content = self._execute_pending_tool_call(
                                        tool_call_data, 
                                        data, 
                                        conn, 
                                        headers, 
                                        prompt
                                    )
                                    if response_content:
                                        tool_call_response = response_content
                                # 有工具调用，返回工具执行后的响应
                                return tool_call_response if tool_call_response else full_content, True
                            else:
                                # 没有工具调用，正常结束
                                return full_content, False
                            continue
                        
                        try:
                            chunk_data = json.loads(json_str)
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                choice = chunk_data['choices'][0]
                                delta = choice.get('delta', {})
                                
                                # 检测工具调用请求
                                if 'tool_calls' in delta:
                                    for tc in delta['tool_calls']:
                                        index = tc.get('index', 0)
                                        
                                        # 初始化该index的tool_call缓冲区
                                        if index not in tool_calls_buffer:
                                            tool_calls_buffer[index] = {
                                                'id': None,
                                                'type': 'function',
                                                'function': {
                                                    'name': None,
                                                    'arguments': ''
                                                }
                                            }
                                        
                                        # 累积tool_call数据
                                        if 'id' in tc:
                                            tool_calls_buffer[index]['id'] = tc['id']
                                        
                                        if 'function' in tc:
                                            if 'name' in tc['function']:
                                                tool_calls_buffer[index]['function']['name'] = tc['function']['name']
                                            if 'arguments' in tc['function']:
                                                # 累积arguments片段
                                                tool_calls_buffer[index]['function']['arguments'] += tc['function']['arguments']
                                        
                                        # 尝试解析完整的arguments
                                        tool_args_str = tool_calls_buffer[index]['function']['arguments']
                                        if tool_args_str:
                                            try:
                                                tool_args = json.loads(tool_args_str)
                                                tool_name = tool_calls_buffer[index]['function']['name']
                                                
                                                # 如果成功解析，说明参数完整，加入待执行队列
                                                if tool_name:
                                                    pending_tool_calls.append({
                                                        'id': tool_calls_buffer[index]['id'],
                                                        'name': tool_name,
                                                        'arguments': tool_args
                                                    })
                                            except json.JSONDecodeError:
                                                # arguments还不完整，继续等待后续chunk
                                                pass
                                
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
            return full_content, False
        finally:
            conn.close()
        
        # 流结束后的兜底检查
        if pending_tool_calls:
            for tool_call_data in pending_tool_calls:
                response_content = self._execute_pending_tool_call(
                    tool_call_data, 
                    data, 
                    conn, 
                    headers, 
                    prompt
                )
                if response_content:
                    tool_call_response = response_content
            return tool_call_response if tool_call_response else full_content, True
        
        return full_content, False
    
    def _execute_pending_tool_call(self, tool_call_data, data, conn, headers, prompt):
        """执行累积完整的工具调用"""
        tool_id = tool_call_data['id']
        tool_name = tool_call_data['name']
        tool_args = tool_call_data['arguments']
        
        print(f"\n完整工具调用: {tool_name}")
        print(f"完整参数: {json.dumps(tool_args, ensure_ascii=False)}")
        
        # 执行工具
        normalized_tool_name = tool_name.lower()
        tool_result = self.execute_tool(normalized_tool_name, tool_args)
        
        print(f"工具执行结果: {json.dumps(tool_result, ensure_ascii=False)}")
        
        # 将工具执行结果添加到聊天历史
        self.add_to_history('assistant', {
            'tool_calls': [{
                'id': tool_id,
                'type': 'function',
                'function': {
                    'name': tool_name,
                    'arguments': json.dumps(tool_args, ensure_ascii=False)
                }
            }]
        })
        
        # 发送工具执行结果
        self.add_to_history('tool', {
            'tool_call_id': tool_id,
            'name': tool_name,
            'content': json.dumps(tool_result, ensure_ascii=False)
        })
        
        # 重新发送请求获取最终响应
        print("\nAI: ", end='', flush=True)
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
        
        # 重新读取响应流
        full_content = ''
        buffer = ''
        
        try:
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                
                buffer += chunk.decode('utf-8', errors='ignore')
                
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
                                delta = chunk_data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    print(content, end='', flush=True)
                                    full_content += content
                        except json.JSONDecodeError:
                            pass
                
                if len(lines) > 0:
                    buffer = lines[-1]
                else:
                    buffer = ''
        finally:
            conn.close()
        
        return full_content
    
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
