# llm-test-trae

## 项目简介

LLM客户端教学项目，演示如何调用OpenAI兼容协议的API。项目采用纯Python标准库实现（http.client），无需安装第三方依赖，非常适合学习理解HTTP请求和API调用的底层原理。

---

## 项目结构

```
llm-test-trae/
├── .env                    # 环境配置文件
├── env.example             # 配置示例文件
├── 白鹿原介绍.txt          # 测试用文本文件
├── practice01/             # 练习1：基础API调用
│   └── llm_client.py       # LLM客户端类
├── practice02/             # 练习2：交互式聊天+工具调用
│   ├── chat_client.py      # 流式聊天客户端
│   ├── tool_chat_client.py # 增强版工具调用客户端
│   └── tools.py            # 工具函数集合
└── practice03/             # 练习3：智能聊天压缩
    ├── chat_compress_client.py  # 带自动压缩功能的聊天客户端
    ├── tools.py            # 工具函数集合
    └── test_compression.py # 压缩功能测试脚本
```

---

## 核心功能模块

### Practice01 - 基础API调用

**主要特性：**
- ✅ 从`.env`文件加载配置（BASE_URL、MODEL、TOKEN）
- ✅ 支持普通文本请求和文件上传
- ✅ 自动处理多种文件编码（UTF-8/GBK/GB2312/UTF-16）
- ✅ Token使用统计（prompt_tokens、completion_tokens、速度等）
- ✅ Qwen3.5专用回答提取器

**运行方式：**
```bash
cd practice01
python llm_client.py
```

---

### Practice02 - 交互式聊天客户端

#### chat_client.py - 流式聊天客户端

**主要特性：**
- ✅ **流式输出**（SSE协议实时显示回复）
- ✅ **上下文管理**（保存最近10条对话历史）
- ✅ **工具调用支持**（5个文件操作工具）
- ✅ **调试模式**（保存对话日志到文件）

**注册的工具：**
- `list_directory` - 列出目录内容
- `rename_file` - 重命名文件
- `delete_file` - 删除文件
- `create_file` - 创建新文件
- `read_file` - 读取文件内容

**运行方式：**
```bash
cd practice02
python chat_client.py
```

#### tool_chat_client.py - 增强版工具调用客户端

**增强特性：**
- ✅ **多轮工具调用**（最多3轮连续工具调用）
- ✅ **增量参数累积**（正确处理流式返回的JSON参数片段）
- ✅ **新增curl工具**（访问网页获取内容）
- ✅ **wttr.in天气预报API支持**

**运行方式：**
```bash
cd practice02
python tool_chat_client.py
```

---

### Practice03 - 智能聊天压缩 ⭐ 新功能

#### chat_compress_client.py - 带自动压缩功能的聊天客户端

**核心功能：**
- ✅ **智能压缩触发**：自动检测对话轮数和上下文长度
  - 超过 **5轮对话** 时触发压缩
  - 上下文长度超过 **3000 tokens** 时触发压缩
  
- ✅ **智能压缩策略**：
  - **前70%** 的历史内容进行LLM总结压缩
  - **后30%** 的内容保留原文，确保近期对话的完整性
  
- ✅ **压缩效果展示**：
  - 实时显示压缩触发原因
  - 显示压缩前后的消息数量对比
  - 提供 `stats` 命令查看当前聊天统计信息

- ✅ **完整工具支持**：继承practice02的所有工具功能
  - 文件操作（list_directory, rename_file, delete_file, create_file, read_file）
  - 网页访问（curl）

**技术亮点：**
1. **Token估算算法**：中文约1字符=1token，英文约4字符=1token
2. **动态分割点计算**：根据compress_ratio（默认0.7）智能计算压缩范围
3. **最小保留保障**：确保至少保留最近一轮对话（user + assistant）
4. **LLM总结优化**：使用低温参数（temperature=0.3）确保总结准确性

**可用命令：**
- `exit` / `quit` - 退出程序
- `clear` - 清空聊天历史
- `debug` - 切换调试模式
- `stats` - 显示聊天统计信息（消息数量、对话轮数、上下文长度）

**运行方式：**
```bash
cd practice03
python chat_compress_client.py
```

**测试脚本：**
```bash
python practice03\test_compression.py
```

**使用示例：**
```
你: 你好
AI: 你好！有什么可以帮助你的吗？

你: stats
[聊天统计]
  消息数量: 2 条
  对话轮数: 1 轮
  上下文长度: 15 tokens
  压缩阈值: 5 轮 或 3000 tokens

... (继续对话超过5轮后) ...

[压缩触发] 对话轮数(6)超过限制(5)
[压缩开始] 总共12条消息，压缩前8条，保留后4条
[压缩中] 正在调用LLM总结历史对话...
[压缩完成] 从12条消息压缩为5条消息
[压缩效果] 保留了最近4条原始消息
```

---

## 配置文件说明

### .env 配置示例

```ini
# OpenAI兼容协议的LLM配置

# API基础URL - LM Studio本地地址
BASE_URL="http://localhost:1234/v1"

# 模型名称
MODEL="qwen/qwen3.5-9b"

# API密钥 (本地LLM通常不需要，但为了兼容需要设置)
TOKEN=""

# 其他可选配置
# MAX_TOKENS=4096
# TEMPERATURE=0.7
```

### env.example - OpenAI官方API配置

```ini
BASE_URL="https://api.openai.com/v1"
MODEL="gpt-3.5-turbo"
TOKEN="your_api_key_here"
```

---

## 技术栈

- **Python标准库**：http.client, json, re, os, time
- **无第三方依赖**：纯标准库实现，降低学习门槛
- **SSE流式处理**：Server-Sent Events协议解析
- **多编码支持**：UTF-8/GBK/GB2312/UTF-16自动检测

---

## 学习价值

1. **HTTP协议理解** - 直接使用http.client构建POST请求
2. **SSE流式处理** - 学习Server-Sent Events协议解析
3. **工具调用机制** - 理解Function Calling的工作原理
4. **上下文管理** - 对话历史的维护和截断策略
5. **智能压缩算法** - 基于轮数和token长度的动态压缩
6. **错误处理** - 多编码文件读取、网络异常处理
7. **正则表达式** - 从复杂文本中提取结构化信息

---

## 环境要求

- Python 3.6+
- 本地LLM服务（如LM Studio）或OpenAI API密钥

---

## 快速开始

1. 复制配置文件：
   ```bash
   copy env.example .env
   ```

2. 编辑 `.env` 文件，配置你的API地址和模型

3. 选择要运行的模块：
   ```bash
   # 基础API调用
   cd practice01
   python llm_client.py
   
   # 交互式聊天
   cd practice02
   python chat_client.py
   
   # 智能聊天压缩
   cd practice03
   python chat_compress_client.py
   ```

---

## 许可证

本项目仅用于学习和教学目的。