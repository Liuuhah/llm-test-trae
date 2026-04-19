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

- ✅ **聊天历史搜索功能**：
  - 每5轮对话自动提取关键信息并保存到 `D:\chat-log\log.txt`
  - 支持通过 `/search` 命令或自然语言查询历史记录
  - AI能够结合对话上下文和5W信息进行智能总结
  - 精准匹配序号查询（如"第一条记录"、"最近三条"）

**技术亮点：**
1. **Token估算算法**：中文约1字符=1token，英文约4字符=1token
2. **动态分割点计算**：根据compress_ratio（默认0.7）智能计算压缩范围
3. **最小保留保障**：确保至少保留最近一轮对话（user + assistant）
4. **LLM总结优化**：使用低温参数（temperature=0.3）确保总结准确性
5. **Qwen3.5适配**：支持从reasoning_content提取内容，三层降级容错机制
6. **wttr.in性能优化**：移除错误的format=2参数，返回默认3天文本表格，响应时间从100秒降至10秒（提升10倍）
7. **消息序列清理**：自动合并连续相同角色的消息，避免LM Studio Jinja模板报错
8. **智能记录分割**：以 `【记录时间】` 为标记分割日志记录，保证每条记录的完整性

**开发注意事项：**
- 📖 详细文档：[practice03/开发注意事项.md](./practice03/开发注意事项.md)
- 🔍 核心问题：Qwen3.5模型的Reasoning Content特性、Prompt优化、调试技巧等
- 💡 最佳实践：推理型模型的内容提取策略、多层容错机制设计
- 🌤️ **wttr.in优化经验**：使用默认3天文本表格而非format=2（当前天气），添加User-Agent: curl和URL编码支持
- 🔧 **已解决问题**：
  - ✅ LM Studio Jinja模板报错：压缩摘要改为user角色，添加消息序列清理函数
  - ✅ 聊天历史搜索上下文丢失：以 `【记录时间】` 为标记分割记录，保证完整性
  - ✅ 搜索序号不匹配：实现精准的序号识别逻辑（第一条、第二条等）

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
8. **API性能优化** - wttr.in案例：正确的API参数选择、User-Agent设置、URL编码

---

## 性能优化记录 ⭐

### wttr.in 天气查询优化（2026-04-17）

**问题描述：**
- 访问 `https://wttr.in/` 时AI响应极慢（70-100秒）
- AI多次调用工具（4次），每次都只获取当前天气
- 最终没有返回明天的天气预报数据

**根本原因：**
1. 代码强制添加了 `format=2` 参数，但 `format=2` 只返回当前时刻的天气（1行数据）
2. AI发现数据不够，反复尝试不同参数组合（format=3, forecast=2等）
3. 中文城市名导致 ASCII 编码错误

**解决方案：**
1. 移除强制添加 `format=2` 的逻辑，让 wttr.in 返回默认的3天文本表格
2. 添加 `User-Agent: curl` 请求头，获取简洁文本格式
3. 添加 URL 编码支持，处理中文城市名

**优化效果：**
| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 工具调用次数 | 4次 | 1次 | ✅ 减少75% |
| 响应时间 | 70-100秒 | 5-10秒 | ✅ 快7-10倍 |
| Token数量 | ~15000 | ~500-800 | ✅ 减少95% |
| 数据准确性 | 只有当前天气 | 完整3天预报 | ✅ 完全准确 |

**wttr.in API 参数说明：**
- **无参数**：3天文本表格预报（推荐）✅
- `format=1`：当前天气（简洁，1行）
- `format=2`：当前天气（详细，带emoji，1行）❌
- `format=3`：当前天气（带ASCII图表）
- `format=j1`：3天JSON预报（数据量巨大）❌

---

### 聊天历史搜索功能优化（2026-04-19）

**问题描述：**
- 用户查询"第一条历史记录"时，AI无法看到完整的对话上下文
- 工具返回的结果只有时间戳和轮次，丢失了对话内容
- AI无法总结用户的个人信息（如"我爱打篮球"）

**根本原因：**
1. 使用 `split('\n====...====')` 分割记录，导致同一条记录被拆分成多个片段
2. 当选择"第一条"时，只取了第一个片段（只有时间戳），丢失了包含对话上下文的片段

**解决方案：**
1. 以 `【记录时间】` 为标记分割记录，保证每条记录的完整性
2. 优化工具描述，告诉AI需要结合对话上下文和5W信息生成总结
3. 实现精准的序号识别逻辑（第一条、第二条、第三条等）
4. 添加 `_clean_extraction_content` 方法，清理冗余的思考过程

**优化效果：**
- ✅ 记录完整性：每条记录包含时间戳、对话上下文、5W结果
- ✅ 精准匹配："第一条"正确返回第一条，而不是最近的三条
- ✅ 智能总结：AI能够提取并总结用户的个人信息
- ✅ 性能良好：当前阶段（<100条记录）完全够用

**未来优化方向：**
- 延迟清理：只清理用户需要的记录（适合100-1000条记录）
- 索引文件：创建索引文件，按需读取（适合1000+条记录）

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