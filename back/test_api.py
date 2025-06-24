#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Chat API 测试脚本
"""
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data['status']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_models():
    """测试获取模型列表"""
    print("\n🔍 测试获取模型列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/models")
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取模型列表成功:")
            for model in data['models']:
                print(f"   - {model['name']}: {model['description']}")
            return True
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取模型列表异常: {e}")
        return False

def test_chat(message="你好，请介绍一下自己"):
    """测试对话接口"""
    print(f"\n🔍 测试对话接口...")
    print(f"用户: {message}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers={"Content-Type": "application/json"},
            json={"message": message}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ AI回复: {data['response'][:100]}...")
                print(f"   模型: {data['model']}")
                if 'usage' in data:
                    usage = data['usage']
                    print(f"   Token使用: {usage}")
                return True
            else:
                print(f"❌ 对话失败: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ 对话请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 对话请求异常: {e}")
        return False

def test_chat_history():
    """测试获取对话历史"""
    print("\n🔍 测试获取对话历史...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/history")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取对话历史成功, 共{data['total']}条记录")
            if data['history']:
                print("   最近3条记录:")
                for i, msg in enumerate(data['history'][-3:]):
                    role = "用户" if msg['role'] == 'user' else "AI"
                    content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                    print(f"   {i+1}. {role}: {content}")
            return True
        else:
            print(f"❌ 获取对话历史失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取对话历史异常: {e}")
        return False

def test_clear_history():
    """测试清空对话历史"""
    print("\n🔍 测试清空对话历史...")
    try:
        response = requests.post(f"{BASE_URL}/api/chat/clear")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 清空对话历史成功: {data['message']}")
            return True
        else:
            print(f"❌ 清空对话历史失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 清空对话历史异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试 DeepSeek Chat API")
    print("="*50)
    
    # 测试序列
    tests = [
        ("健康检查", test_health),
        ("模型列表", test_models),
        ("对话功能", lambda: test_chat("你好，请简单介绍一下自己")),
        ("对话历史", test_chat_history),
        ("再次对话", lambda: test_chat("请用一句话总结Python的特点")),
        ("历史记录", test_chat_history),
        ("清空历史", test_clear_history),
        ("验证清空", test_chat_history)
    ]
    
    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # 避免请求过快
    
    # 汇总结果
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    passed = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有测试都通过了！API服务运行正常。")
    else:
        print("⚠️  有测试失败，请检查API服务状态和配置。")

if __name__ == "__main__":
    main() 