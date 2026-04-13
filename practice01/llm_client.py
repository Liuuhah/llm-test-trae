import os
import json
import time
import http.client
from urllib.parse import urlparse
import re

class LLMClient:
    def __init__(self):
        self.config = self._load_config()
        self.base_url = self.config.get('BASE_URL')
        self.model = self.config.get('MODEL')
        self.token = self.config.get('TOKEN')
        self._parse_base_url()
    
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
    
    def _read_txt_file(self, file_path):
        """读取txt文件内容，自动处理常见编码问题"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        print(f"错误: 无法读取文件 {file_path}，请检查文件编码")
        return None
    
    def send_request(self, prompt, max_tokens=262144):
        """发送普通文本请求"""
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
                {'role': 'system', 'content': '请根据提供的信息回答问题，不要编造内容。'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.6
        }
        
        conn.request('POST', f'{self.path}/chat/completions', json.dumps(data), headers)
        response = conn.getresponse()
        response_data = json.loads(response.read().decode())
        conn.close()
        
        end_time = time.time()
        
        if 'error' in response_data:
            print(f"错误: {response_data['error']['message']}")
            return None
        
        usage = response_data['usage']
        message = response_data['choices'][0]['message']
        
        # Qwen3.5专用回答提取器
        completion = ''
        content = message.get('content', '').strip()
        if content:
            completion = content
        else:
            reasoning_content = message.get('reasoning_content', '')
            if reasoning_content:
                patterns = [
                    r'Final Selection:.*?["\']([^"\']*?[\u4e00-\u9fff]+[^"\']*?)["\']',
                    r'Final Polish:.*?["\']([^"\']*?[\u4e00-\u9fff]+[^"\']*?)["\']'
                ]
                for pattern in patterns:
                    match = re.search(pattern, reasoning_content, re.DOTALL)
                    if match:
                        completion = match.group(1).strip()
                        break
                
                if not completion:
                    chinese_sentences = re.findall(r'[\u4e00-\u9fff]+[^.\n]*?[。！？]', reasoning_content)
                    if chinese_sentences:
                        completion = chinese_sentences[-1].strip()
        
        if not completion:
            completion = '抱歉，模型没有返回有效内容。'
        
        total_time = end_time - start_time
        total_tokens = usage['total_tokens']
        token_speed = total_tokens / total_time if total_time > 0 else 0
        
        stats = {
            'prompt_tokens': usage['prompt_tokens'],
            'completion_tokens': usage['completion_tokens'],
            'total_tokens': total_tokens,
            'time_taken': total_time,
            'token_speed': token_speed
        }
        
        return completion, stats
    
    def send_request_with_file(self, file_path, question, max_tokens=1024):
        """发送txt文件+问题的请求，模拟LM Studio的文件上传功能"""
        # 1. 读取文件内容
        file_content = self._read_txt_file(file_path)
        if not file_content:
            return None
        
        # 2. 拼接成完整的提示词（和LM Studio的格式完全一致）
        full_prompt = f"""
以下是文件《{os.path.basename(file_path)}》的内容：
---
{file_content}
---

请根据以上文件内容回答问题：{question}
"""
            
        # 3. 发送请求
        return self.send_request(full_prompt, max_tokens)

if __name__ == "__main__":
    client = LLMClient()
    
    # 测试发送txt文件
    file_path = "白鹿原介绍.txt"  # 这里改成你的txt文件路径
    question = "根据文章分析我最爱的老师是谁？"
    
    print(f"正在读取文件: {file_path}")
    print(f"问题: {question}")
    
    result = client.send_request_with_file(file_path, question)
    if result:
        completion, stats = result
        print("\n回复:")
        print(completion)
        print("\n统计信息:")
        print(f"提示词 token 数: {stats['prompt_tokens']}")
        print(f"回复 token 数: {stats['completion_tokens']}")
        print(f"总 token 数: {stats['total_tokens']}")
        print(f"耗时: {stats['time_taken']:.2f} 秒")
        print(f"速度: {stats['token_speed']:.2f} token/秒")