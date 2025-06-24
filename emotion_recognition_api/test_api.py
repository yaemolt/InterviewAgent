#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API测试脚本
"""

import requests
import time
import json

def test_api():
    """测试API服务"""
    base_url = "http://localhost:5000/api"
    
    print("="*60)
    print("🧪 情绪识别API测试")
    print("="*60)
    
    # 等待服务启动
    print("⏳ 等待API服务启动...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API服务已启动")
                break
        except:
            time.sleep(2)
            print(f"   等待中... ({i+1}/10)")
    else:
        print("❌ API服务启动失败或超时")
        return False
    
    # 测试健康检查
    print("\n1️⃣ 测试健康检查接口")
    try:
        response = requests.get(f"{base_url}/health")
        result = response.json()
        print(f"   状态: {result['status']}")
        print(f"   模型加载: {result['model_loaded']}")
        print(f"   设备: {result['device']}")
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
        return False
    
    # 测试模型信息
    print("\n2️⃣ 测试模型信息接口")
    try:
        response = requests.get(f"{base_url}/models")
        result = response.json()
        if result['success']:
            model_info = result['models'][0]
            print(f"   模型ID: {model_info['id']}")
            print(f"   模型名称: {model_info['name']}")
            print(f"   支持情绪: {model_info['emotions']}")
        else:
            print(f"   ❌ 获取模型信息失败")
    except Exception as e:
        print(f"   ❌ 模型信息接口失败: {e}")
    
    # 测试虚拟数据分析
    print("\n3️⃣ 测试虚拟数据分析")
    try:
        response = requests.post(f"{base_url}/emotions/test")
        result = response.json()
        if result['success']:
            emotions = result['data']['emotions']
            print(f"   主导情绪: {result['data']['dominant_emotion']}")
            print(f"   处理时间: {result['data']['processing_time']}")
            print("   情绪分析结果:")
            for emotion in emotions:
                print(f"     {emotion['emotion']}: {emotion['score']:.2f} ({emotion['percentage']:.1f}%)")
        else:
            print(f"   ❌ 虚拟数据分析失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 虚拟数据分析接口失败: {e}")
    
    print("\n" + "="*60)
    print("✅ API测试完成")
    print("📍 API地址: http://localhost:5000")
    print("📋 接口文档: 查看 API接口文档.md")
    print("="*60)
    
    return True

if __name__ == "__main__":
    test_api() 