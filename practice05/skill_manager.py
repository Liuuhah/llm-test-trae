"""
Skill Manager - 动态技能加载系统核心模块

负责技能的扫描、解析、缓存和加载。
使用 Python 标准库实现，不依赖第三方包。
"""

import os
import re
import json


class SkillManager:
    """技能管理器，负责管理本地技能文件"""
    
    def __init__(self, skills_root_path: str):
        """
        初始化技能管理器
        
        Args:
            skills_root_path: 技能根目录路径（例如：.agents/skills）
        """
        self.skills_root_path = os.path.abspath(skills_root_path)
        self.skills_cache = []  # 缓存技能元数据列表
        self._scan_completed = False
    
    def scan_and_cache(self) -> list:
        """
        扫描技能目录并缓存技能元数据
        
        Returns:
            list[dict]: 技能元数据列表，每个元素包含 name 和 description
        """
        self.skills_cache = []
        
        if not os.path.exists(self.skills_root_path):
            print(f"[SkillManager] 警告：技能目录不存在 - {self.skills_root_path}")
            return self.skills_cache
        
        # 遍历技能目录
        for skill_name in os.listdir(self.skills_root_path):
            skill_dir = os.path.join(self.skills_root_path, skill_name)
            
            # 只处理目录
            if not os.path.isdir(skill_dir):
                continue
            
            skill_md_path = os.path.join(skill_dir, 'SKILL.md')
            
            # 检查 SKILL.md 是否存在
            if not os.path.exists(skill_md_path):
                print(f"[SkillManager] 跳过：{skill_name} 目录下未找到 SKILL.md")
                continue
            
            # 解析技能元数据
            try:
                metadata = self._parse_skill_metadata(skill_md_path)
                if metadata:
                    metadata['directory'] = skill_name  # 保存目录名用于后续加载
                    self.skills_cache.append(metadata)
                    print(f"[SkillManager] 已加载技能：{metadata['name']}")
            except Exception as e:
                print(f"[SkillManager] 错误：解析 {skill_name} 失败 - {str(e)}")
        
        self._scan_completed = True
        print(f"[SkillManager] 扫描完成，共加载 {len(self.skills_cache)} 个技能")
        return self.skills_cache
    
    def _parse_skill_metadata(self, file_path: str) -> dict:
        """
        解析 SKILL.md 文件的 YAML Front Matter
        
        Args:
            file_path: SKILL.md 文件路径
            
        Returns:
            dict: 包含 name 和 description 的字典，解析失败返回 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 只读取前 100 行
                lines = []
                for i, line in enumerate(f):
                    if i >= 100:
                        break
                    lines.append(line)
                
                content = ''.join(lines)
                
                # 使用正则表达式匹配 --- 之间的内容
                pattern = r'^---\s*\n(.*?)\n\s*---'
                match = re.search(pattern, content, re.DOTALL)
                
                if not match:
                    print(f"[SkillManager] 警告：{file_path} 未找到有效的 Front Matter")
                    return None
                
                front_matter = match.group(1)
                
                # 提取 name
                name_match = re.search(r'name:\s*(.+)', front_matter)
                if not name_match:
                    print(f"[SkillManager] 警告：{file_path} 缺少 name 字段")
                    return None
                name = name_match.group(1).strip().strip('"').strip("'")
                
                # 提取 description
                desc_match = re.search(r'description:\s*(.+)', front_matter)
                if not desc_match:
                    print(f"[SkillManager] 警告：{file_path} 缺少 description 字段")
                    return None
                description = desc_match.group(1).strip().strip('"').strip("'")
                
                return {
                    'name': name,
                    'description': description
                }
                
        except Exception as e:
            print(f"[SkillManager] 解析文件失败：{file_path} - {str(e)}")
            return None
    
    def get_skill_json(self) -> str:
        """
        返回符合要求的 JSON 格式字符串
        
        Returns:
            str: JSON 格式的技能列表
        """
        if not self._scan_completed:
            self.scan_and_cache()
        
        return json.dumps(self.skills_cache, ensure_ascii=False, indent=2)
    
    def load_full_content(self, skill_name: str) -> str:
        """
        加载并返回技能的正文内容（不含 Front Matter）
        
        Args:
            skill_name: 技能的唯一标识符（对应目录名）
            
        Returns:
            str: 技能正文内容，失败时返回错误信息
        """
        # 安全性检查：防止路径遍历攻击
        if '..' in skill_name or '/' in skill_name or '\\' in skill_name:
            return f"错误：非法的技能名称 '{skill_name}'，包含不安全字符"
        
        skill_dir = os.path.join(self.skills_root_path, skill_name)
        skill_md_path = os.path.join(skill_dir, 'SKILL.md')
        
        # 检查路径是否在允许的范围内
        real_path = os.path.realpath(skill_md_path)
        real_root = os.path.realpath(self.skills_root_path)
        if not real_path.startswith(real_root):
            return f"错误：技能路径超出允许范围"
        
        if not os.path.exists(skill_md_path):
            return f"错误：技能 '{skill_name}' 的 SKILL.md 文件不存在"
        
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 移除 Front Matter（--- 之间的内容）
                pattern = r'^---\s*\n.*?\n\s*---\s*\n?'
                body = re.sub(pattern, '', content, flags=re.DOTALL)
                
                return body.strip()
                
        except Exception as e:
            return f"错误：读取技能文件失败 - {str(e)}"
