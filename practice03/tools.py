import os
import json
from datetime import datetime
import stat
import urllib.request
import urllib.error
import re
from urllib.parse import quote, urlparse, urlunparse

class Tools:
    def list_directory(self, directory_path):
        """列出指定目录下的所有文件和子目录，包括文件的基本属性（大小、修改时间等）"""
        try:
            # 如果directory_path为None，返回错误
            if directory_path is None:
                return {"error": "未提供目录路径参数"}
            
            # 处理相对路径
            if not os.path.isabs(directory_path):
                directory_path = os.path.abspath(directory_path)
            
            if not os.path.exists(directory_path):
                return {"error": f"目录不存在: {directory_path}"}
            
            if not os.path.isdir(directory_path):
                return {"error": f"路径不是目录: {directory_path}"}
            
            items = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                item_stat = os.stat(item_path)
                
                item_info = {
                    "name": item,
                    "path": item_path,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": item_stat.st_size,
                    "last_modified": datetime.fromtimestamp(item_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "mode": stat.filemode(item_stat.st_mode)
                }
                items.append(item_info)
            
            return {"items": items, "total": len(items)}
        except Exception as e:
            return {"error": f"执行错误: {str(e)}"}
    
    def rename_file(self, directory_path, old_filename, new_filename):
        """修改某个目录下某个文件的名字"""
        try:
            # 检查参数
            if not directory_path or not old_filename or not new_filename:
                return {"error": "缺少必要参数"}
            
            # 处理相对路径
            if not os.path.isabs(directory_path):
                directory_path = os.path.abspath(directory_path)
            
            # 构建完整路径
            old_path = os.path.join(directory_path, old_filename)
            new_path = os.path.join(directory_path, new_filename)
            
            # 检查文件是否存在
            if not os.path.exists(old_path):
                return {"error": f"文件不存在: {old_path}"}
            
            # 检查新文件名是否已存在
            if os.path.exists(new_path):
                return {"error": f"新文件名已存在: {new_path}"}
            
            # 执行重命名
            os.rename(old_path, new_path)
            
            return {"success": True, "message": f"文件已重命名为: {new_filename}", "old_path": old_path, "new_path": new_path}
        except Exception as e:
            return {"error": f"执行错误: {str(e)}"}
    
    def delete_file(self, directory_path, filename):
        """删除某个目录下某个文件"""
        try:
            # 检查参数
            if not directory_path or not filename:
                return {"error": "缺少必要参数"}
            
            # 处理相对路径
            if not os.path.isabs(directory_path):
                directory_path = os.path.abspath(directory_path)
            
            # 构建完整路径
            file_path = os.path.join(directory_path, filename)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}
            
            # 检查是否为文件
            if not os.path.isfile(file_path):
                return {"error": f"路径不是文件: {file_path}"}
            
            # 执行删除
            os.remove(file_path)
            
            return {"success": True, "message": f"文件已删除: {filename}", "deleted_path": file_path}
        except Exception as e:
            return {"error": f"执行错误: {str(e)}"}
    
    def create_file(self, directory_path, filename, content):
        """在某个目录下新建一个文件，并且写入内容"""
        try:
            # 检查参数
            if not directory_path or not filename:
                return {"error": "缺少必要参数"}
            
            # 处理相对路径
            if not os.path.isabs(directory_path):
                directory_path = os.path.abspath(directory_path)
            
            # 检查目录是否存在
            if not os.path.exists(directory_path):
                return {"error": f"目录不存在: {directory_path}"}
            
            if not os.path.isdir(directory_path):
                return {"error": f"路径不是目录: {directory_path}"}
            
            # 构建完整路径
            file_path = os.path.join(directory_path, filename)
            
            # 检查文件是否已存在
            if os.path.exists(file_path):
                return {"error": f"文件已存在: {file_path}"}
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content if content else '')
            
            return {"success": True, "message": f"文件已创建: {filename}", "file_path": file_path}
        except Exception as e:
            return {"error": f"执行错误: {str(e)}"}
    
    def read_file(self, directory_path, filename):
        """读取某个目录下面的某个文件的内容"""
        try:
            # 检查参数
            if not directory_path or not filename:
                return {"error": "缺少必要参数"}
            
            # 处理相对路径
            if not os.path.isabs(directory_path):
                directory_path = os.path.abspath(directory_path)
            
            # 构建完整路径
            file_path = os.path.join(directory_path, filename)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}
            
            # 检查是否为文件
            if not os.path.isfile(file_path):
                return {"error": f"路径不是文件: {file_path}"}
            
            # 读取文件内容
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return {"error": f"无法读取文件: {file_path}"}
            
            # 获取文件信息
            file_stat = os.stat(file_path)
            file_info = {
                "name": filename,
                "path": file_path,
                "size": file_stat.st_size,
                "last_modified": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "mode": stat.filemode(file_stat.st_mode)
            }
            
            return {"success": True, "content": content, "file_info": file_info}
        except Exception as e:
            return {"error": f"执行错误: {str(e)}"}
    
    def curl(self, url):
        """通过curl访问网页，并返回网页内容"""
        try:
            # 检查参数
            if not url:
                return {"error": "缺少URL参数"}
            
            original_url = url
            
            # wttr.in 天气预报网站：不添加 format 参数，返回默认的3天文本表格预报
            # 如果用户或 AI 指定了 format 参数，移除它以避免只返回当前天气
            if 'wttr.in' in url:
                # 移除可能存在的 format 参数（如果 AI 错误地添加了 format=1/2/3/j1等）
                url = re.sub(r'[&?]format=[123jJ][0-9]*', '', url)
                # 清理多余的 & 或 ?
                url = re.sub(r'\?&', '?', url)
                url = re.sub(r'\?$', '', url)
                url = re.sub(r'&$', '', url)
            
            # 对 URL 进行编码，处理中文字符（如"成都" → "%E6%88%90%E9%83%BD"）
            parsed = urlparse(url)
            # 只对 path 部分进行编码，保留 query 参数
            encoded_path = quote(parsed.path, safe='/')
            encoded_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                encoded_path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            url = encoded_url
            
            # 执行HTTP请求
            # 对于 wttr.in，需要设置 User-Agent 为 "curl" 以获取文本格式而非 HTML
            if 'wttr.in' in url:
                req = urllib.request.Request(url, headers={'User-Agent': 'curl'})
                with urllib.request.urlopen(req) as response:
                    # 获取响应状态码
                    status_code = response.getcode()
                    # 获取响应头
                    headers = dict(response.getheaders())
                    # 获取内容类型
                    content_type = headers.get('Content-Type', '')
                    # 读取响应内容
                    content = response.read().decode('utf-8', errors='ignore')
            else:
                with urllib.request.urlopen(url) as response:
                    # 获取响应状态码
                    status_code = response.getcode()
                    # 获取响应头
                    headers = dict(response.getheaders())
                    # 获取内容类型
                    content_type = headers.get('Content-Type', '')
                    # 读取响应内容
                    content = response.read().decode('utf-8', errors='ignore')
                        
            # wttr.in 不加 format 参数时返回3天文本表格预报（约500-800 tokens）
            # 保持与其他 URL 一致的截断逻辑
            if 'wttr.in' in original_url and 'text/plain' in content_type:
                # wttr.in 文本格式不截断，保留完整内容（通常只有2-3KB）
                pass
            elif 'json' in content_type:
                # JSON格式保留更多
                content = content[:5000]
            elif 'html' in content_type:
                # HTML格式只保留前2000字符
                content = content[:2000] + '\n...[HTML内容已截断]...'
            else:
                # 其他格式保疙3000字符
                content = content[:3000]
                        
            return {
                "success": True,
                "url": url,
                "status_code": status_code,
                "content_type": content_type,
                "content": content
            }
        except urllib.error.URLError as e:
            return {"error": f"URL错误: {str(e)}"}
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP错误: {e.code} - {e.reason}"}
        except Exception as e:
            return {"error": f"执行错误: {str(e)}"}
    
    def _clean_extraction_content(self, content):
        """清理提取内容，移除 Thinking Process，保留5W部分和基本信息"""
        if not content:
            return content
        
        # 先提取基本信息（记录时间和对话轮次）
        basic_info = []
        time_match = re.search(r'【记录时间】.*', content)
        round_match = re.search(r'【对话轮次】.*', content)
        if time_match:
            basic_info.append(time_match.group(0))
        if round_match:
            basic_info.append(round_match.group(0))
        
        # 查找 - Who: 开始的位置
        who_match = re.search(r'-\s*Who:', content)
        if who_match:
            # 保留基本信息 + 5W内容
            five_w_content = content[who_match.start():].strip()
            if basic_info:
                return '\n'.join(basic_info) + '\n' + five_w_content
            return five_w_content
        
        # 如果找不到 - Who:，尝试移除常见的思考过程标记
        thinking_markers = [
            'Thinking Process:',
            '思考过程',
            '分析过程',
            'Let me think',
            'First,',
            'Second,',
            'Finally,'
        ]
        
        for marker in thinking_markers:
            if marker in content:
                # 找到标记后，尝试提取后面的内容
                parts = content.split(marker, 1)
                if len(parts) > 1:
                    remaining = parts[1].strip()
                    # 检查剩余内容是否包含5W
                    if re.search(r'-\s*(Who|What|When|Where|Why):', remaining):
                        if basic_info:
                            return '\n'.join(basic_info) + '\n' + remaining.strip()
                        return remaining.strip()
        
        # 如果都没有匹配，返回原始内容（至少保留基本信息）
        if basic_info:
            return '\n'.join(basic_info)
        return content
    
    def search_chat_history(self, query):
        """搜索聊天历史记录，查找与查询相关的历史对话信息"""
        try:
            # 检查参数
            if not query:
                return {"error": "缺少查询参数，请提供搜索关键词"}
            
            log_file_path = r"D:\chat-log\log.txt"
            
            # 检查日志文件是否存在
            if not os.path.exists(log_file_path):
                return {
                    "success": False,
                    "message": "聊天记录文件不存在",
                    "details": f"文件路径: {log_file_path}",
                    "suggestion": "聊天记录尚未生成。请先进行至少5轮对话，系统会自动提取关键信息并保存。"
                }
            
            # 读取日志文件内容
            try:
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                with open(log_file_path, 'r', encoding='gbk') as f:
                    log_content = f.read()
            
            # 检查文件是否为空
            if not log_content.strip():
                return {
                    "success": False,
                    "message": "聊天记录为空",
                    "details": "日志文件存在但没有内容",
                    "suggestion": "请先进行至少5轮对话，系统会自动提取关键信息并保存。"
                }
            
            # 统计记录条数
            record_count = log_content.count('【记录时间】')
            
            # 按记录分割
            records = log_content.split('\n============================================================')
            records = [r.strip() for r in records if r.strip()]
            
            # 清理每条记录的内容（移除 Thinking Process）
            cleaned_records = []
            for record in records:
                clean_record = self._clean_extraction_content(record)
                if clean_record:
                    cleaned_records.append(clean_record)
            records = cleaned_records
            
            # 检查是否包含序号关键词
            target_records = []
            target_message = ""
            
            if '第一条' in query or '第1条' in query or '最早' in query or '首次' in query:
                # 返回第一条记录
                if len(records) > 0:
                    target_records = records[:1]
                    target_message = f"找到 {record_count} 条历史记录，以下是第一条："
                else:
                    return {
                        "success": False,
                        "message": "没有找到任何历史记录",
                        "total_records": 0
                    }
            elif '第二条' in query or '第2条' in query:
                # 返回第二条记录
                if len(records) > 1:
                    target_records = records[1:2]
                    target_message = f"找到 {record_count} 条历史记录，以下是第二条："
                else:
                    return {
                        "success": False,
                        "message": f"记录不足2条，当前只有 {len(records)} 条记录",
                        "total_records": record_count
                    }
            elif '第三条' in query or '第3条' in query:
                # 返回第三条记录
                if len(records) > 2:
                    target_records = records[2:3]
                    target_message = f"找到 {record_count} 条历史记录，以下是第三条："
                else:
                    return {
                        "success": False,
                        "message": f"记录不足3条，当前只有 {len(records)} 条记录",
                        "total_records": record_count
                    }
            else:
                # 默认返回最近3条记录
                target_records = records[-3:] if len(records) > 3 else records
                target_message = f"找到 {record_count} 条历史记录，以下是最近的 {len(target_records)} 条："
            
            target_content = '\n'.join(target_records)
            
            return {
                "success": True,
                "message": target_message,
                "total_records": record_count,
                "returned_records": len(target_records),
                "content": target_content
            }
        
        except FileNotFoundError:
            return {
                "error": "聊天记录文件不存在",
                "details": f"文件路径: {log_file_path}",
                "suggestion": "请先进行至少5轮对话，系统会自动提取关键信息并保存。"
            }
        except Exception as e:
            return {"error": f"搜索执行错误: {str(e)}"}

# 工具实例
tools = Tools()
