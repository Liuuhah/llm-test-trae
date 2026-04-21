#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AnythingLLM 查询功能测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools import tools

def test_basic_query():
    """测试基本查询"""
    print("=" * 60)
    print("测试1: 基本查询")
    print("=" * 60)
    
    result = tools.anythingllm_query("你好，请介绍一下你自己")
    
    if result.get('success'):
        print(f"✅ 查询成功")
        print(f"回答: {result['answer'][:200]}...")  # 只显示前200字符
        if result.get('sources'):
            print(f"来源数量: {len(result['sources'])}")
    else:
        print(f"❌ 查询失败: {result.get('error')}")
    
    print()

def test_document_query():
    """测试文档相关查询"""
    print("=" * 60)
    print("测试2: 文档查询")
    print("=" * 60)
    
    result = tools.anythingllm_query("公司有哪些规章制度？")
    
    if result.get('success'):
        print(f"✅ 查询成功")
        print(f"回答: {result['answer'][:300]}...")
    else:
        print(f"❌ 查询失败: {result.get('error')}")
    
    print()

def test_error_handling():
    """测试错误处理"""
    print("=" * 60)
    print("测试3: 空消息测试")
    print("=" * 60)
    
    result = tools.anythingllm_query("")
    print(f"结果: {result}")
    print()

if __name__ == "__main__":
    print("\n开始测试 AnythingLLM 查询功能...\n")
    
    test_basic_query()
    test_document_query()
    test_error_handling()
    
    print("\n测试完成！")
