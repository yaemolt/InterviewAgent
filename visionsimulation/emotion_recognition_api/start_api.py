#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪识别API启动脚本
"""

import sys
import os
import subprocess

def check_dependencies():
    """检查依赖安装"""
    required_packages = [
        'torch', 'torchvision', 'flask', 'flask_cors', 
        'cv2', 'numpy', 'PIL', 'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                import PIL
            elif package == 'flask_cors':
                import flask_cors
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未安装")
    
    return missing_packages

def install_dependencies():
    """安装缺失的依赖"""
    print("🔧 安装项目依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def main():
    print("="*70)
    print("🚀 DAiSEE情绪识别API启动器")
    print("="*70)
    
    print("\n📋 检查系统依赖...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n⚠️ 发现 {len(missing_packages)} 个缺失的依赖包")
        print("缺失的包:", ", ".join(missing_packages))
        
        install_choice = input("\n是否自动安装缺失的依赖? (y/n): ").lower().strip()
        
        if install_choice in ['y', 'yes', '是']:
            if not install_dependencies():
                print("依赖安装失败，请手动安装后重试")
                return False
        else:
            print("请手动安装依赖后重试:")
            print("pip install -r requirements.txt")
            return False
    
    print("\n✅ 所有依赖已准备就绪")
    print("\n🚀 启动API服务...")
    
    try:
        # 导入并启动API
        from emotion_api import app, load_model
        
        # 加载模型
        if load_model():
            print("✅ 模型加载成功")
        else:
            print("❌ 模型加载失败，但服务仍可启动")
        
        print("\n" + "="*70)
        print("🌐 API服务已启动")
        print("="*70)
        print("📍 服务地址: http://localhost:5000")
        print("📋 API文档: 查看 API接口文档.md")
        print("🔍 健康检查: GET /api/health")
        print("🎬 视频分析: POST /api/emotions/analyze")
        print("="*70)
        print("按 Ctrl+C 停止服务")
        
        # 启动Flask服务
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖都已正确安装")
        return False
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 