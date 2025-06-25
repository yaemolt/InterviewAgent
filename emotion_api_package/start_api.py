#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAiSEE情感识别API - 快速启动脚本
"""

import os
import sys

def check_dependencies():
    """检查依赖库"""
    print("🔍 检查依赖库...")
    
    required_packages = [
        'torch',
        'torchvision', 
        'cv2',
        'flask',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ 缺少依赖库: {', '.join(missing_packages)}")
        print(f"请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖库已安装")
    return True

def check_model_file():
    """检查模型文件"""
    print("\n🔍 检查模型文件...")
    
    model_file = 'best_fast_daisee_model.pth'
    if os.path.exists(model_file):
        size_mb = os.path.getsize(model_file) / 1024**2
        print(f"   ✅ {model_file} ({size_mb:.1f}MB)")
        return True
    else:
        print(f"   ❌ {model_file} 不存在")
        return False

def run_tests():
    """运行测试"""
    print("\n🧪 运行API测试...")
    
    try:
        from test_emotion_api import test_model_weights, verify_output_format
        
        # 测试模型加载
        api = test_model_weights()
        if api is None:
            return False
        
        # 验证输出格式
        verify_output_format()
        
        print("✅ API测试通过")
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def start_api_server():
    """启动API服务"""
    print("\n🚀 启动API服务...")
    
    try:
        from emotion_recognition_api import main
        print("📡 API服务将在 http://localhost:5000 启动")
        print("🔗 接口地址:")
        print("   POST /predict - 预测情感 (Base64视频)")
        print("   POST /predict_file - 预测情感 (文件上传)")
        print("   GET /health - 健康检查")
        print("\n按 Ctrl+C 停止服务")
        
        main()
        
    except KeyboardInterrupt:
        print("\n👋 API服务已停止")
    except Exception as e:
        print(f"❌ API服务启动失败: {e}")

def show_usage_example():
    """显示使用示例"""
    print("\n📖 API使用示例:")
    print("=" * 50)
    
    print("1. 直接导入使用:")
    print("""
from emotion_recognition_api import EmotionRecognitionAPI

api = EmotionRecognitionAPI()
result = api.predict_emotions('video.mp4', is_base64=False)
print(f"最终得分: {result['final_score']:.2f}/100")
""")
    
    print("2. HTTP API调用:")
    print("""
import requests

# 文件上传
files = {'video': open('video.mp4', 'rb')}
response = requests.post('http://localhost:5000/predict_file', files=files)
result = response.json()
print(result)
""")

def main():
    """主函数"""
    print("🎯 DAiSEE情感识别API - 快速启动工具")
    print("=" * 60)
    
    # 检查环境
    if not check_dependencies():
        return
    
    if not check_model_file():
        return
    
    # 选择操作
    print("\n🎮 请选择操作:")
    print("1. 运行API测试")
    print("2. 启动API服务")
    print("3. 查看使用示例")
    print("4. 运行完整演示")
    
    try:
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            run_tests()
        elif choice == '2':
            start_api_server()
        elif choice == '3':
            show_usage_example()
        elif choice == '4':
            print("\n🎬 运行完整演示...")
            from demo_api_usage import main as demo_main
            demo_main()
        else:
            print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 退出")
    except Exception as e:
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    main() 