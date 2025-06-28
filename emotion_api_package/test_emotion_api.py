#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试情感识别API和模型权重
"""

import os
import torch
import numpy as np
from emotion_recognition_api import EmotionRecognitionAPI
import json

def test_model_weights():
    """测试模型权重是否已训练"""
    print("🔍 测试模型权重...")
    
    try:
        # 初始化API（会自动验证权重）
        api = EmotionRecognitionAPI()
        print("✅ 模型权重验证通过")
        return api
    except Exception as e:
        print(f"❌ 模型权重验证失败: {e}")
        return None

def test_api_with_sample_video():
    """测试API使用示例视频"""
    print("\n🧪 测试API功能...")
    
    api = test_model_weights()
    if api is None:
        return
    
    # 查找示例视频文件
    sample_video_paths = [
        'daisee_hf/DAiSEE/DataSet/Validation/400022/4000221011/4000221011.avi',
        'daisee_hf/DAiSEE/DataSet/Validation/400023/4000231011/4000231011.avi'
    ]
    
    for video_path in sample_video_paths:
        if os.path.exists(video_path):
            print(f"📹 测试视频: {video_path}")
            
            try:
                # 预测情感
                result = api.predict_emotions(video_path, is_base64=False)
                
                print("✅ 预测成功!")
                print("📊 结果摘要:")
                print(f"   最终得分: {result['final_score']:.2f}/100")
                print(f"   主导情感: {result['dominant_emotion']}")
                print(f"   置信度: {result['confidence']:.3f}")
                print(f"   解释: {result['interpretation']}")
                
                print("\n🎭 各情感占比:")
                for emotion, percentage in result['emotions']['percentages'].items():
                    print(f"   {emotion:12}: {percentage:6.2f}%")
                
                print("\n📈 原始分数:")
                for emotion, score in result['emotions']['raw_scores'].items():
                    print(f"   {emotion:12}: {score:6.3f}")
                
                # 保存结果到文件
                with open('test_result.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"\n💾 详细结果已保存到: test_result.json")
                break
                
            except Exception as e:
                print(f"❌ 预测失败: {e}")
                continue
    else:
        print("❌ 未找到可用的测试视频")

def verify_output_format():
    """验证输出格式符合要求"""
    print("\n📋 验证输出格式...")
    
    api = test_model_weights()
    if api is None:
        return
    
    # 创建虚拟输入测试
    test_input = torch.randn(1, 8, 3, 128, 128).to(api.device)
    
    with torch.no_grad():
        raw_output = api.model(test_input).cpu().numpy()[0]
    
    print(f"✅ 模型输出形状: {raw_output.shape}")
    print(f"✅ 输出值范围: [{raw_output.min():.3f}, {raw_output.max():.3f}]")
    
    # 验证输出格式
    emotions_raw = np.clip(raw_output, 0, 3)
    emotions_exp = np.exp(emotions_raw - np.max(emotions_raw))
    emotions_prob = emotions_exp / np.sum(emotions_exp)
    
    print(f"✅ 归一化概率和: {emotions_prob.sum():.6f}")
    print(f"✅ 各情感概率:")
    for i, emotion in enumerate(api.emotion_names):
        print(f"   {emotion:12}: {emotions_prob[i]:.4f} ({emotions_prob[i]*100:.2f}%)")
    
    # 测试加权评分
    weighted_score = sum(emotions_prob[i] * api.emotion_weights[emotion] 
                        for i, emotion in enumerate(api.emotion_names))
    final_score = 50 + weighted_score * 25
    final_score = np.clip(final_score, 0, 100)
    
    print(f"✅ 加权分数: {weighted_score:.3f}")
    print(f"✅ 最终得分: {final_score:.2f}/100")

def benchmark_performance():
    """性能基准测试"""
    print("\n⚡ 性能基准测试...")
    
    api = test_model_weights()
    if api is None:
        return
    
    import time
    
    # 创建测试输入
    test_input = torch.randn(1, 8, 3, 128, 128).to(api.device)
    
    # 预热
    for _ in range(10):
        with torch.no_grad():
            _ = api.model(test_input)
    
    # 基准测试
    times = []
    for _ in range(100):
        start_time = time.time()
        with torch.no_grad():
            _ = api.model(test_input)
        end_time = time.time()
        times.append((end_time - start_time) * 1000)  # 转换为毫秒
    
    avg_time = np.mean(times)
    std_time = np.std(times)
    
    print(f"✅ 平均推理时间: {avg_time:.2f} ± {std_time:.2f} ms")
    print(f"✅ 最快推理时间: {min(times):.2f} ms")
    print(f"✅ 最慢推理时间: {max(times):.2f} ms")
    
    if avg_time < 50:
        print(f"🚀 性能优秀 - 适合实时应用")
    elif avg_time < 100:
        print(f"✅ 性能良好 - 适合在线应用")
    else:
        print(f"⚠️ 性能一般 - 可能需要优化")

def main():
    """主函数"""
    print("🎯 DAiSEE情感识别模型验证工具")
    print("=" * 60)
    
    # 检查模型文件
    if not os.path.exists('best_fast_daisee_model.pth'):
        print("❌ 模型文件不存在: best_fast_daisee_model.pth")
        return
    
    print(f"📁 模型文件大小: {os.path.getsize('best_fast_daisee_model.pth') / 1024**2:.1f} MB")
    
    # 运行测试
    test_model_weights()
    verify_output_format()
    benchmark_performance()
    test_api_with_sample_video()
    
    print("\n" + "=" * 60)
    print("✅ 验证完成!")
    
    print("\n📋 输出格式说明:")
    print("   - emotions.raw_scores: 原始模型输出 (0-3范围)")
    print("   - emotions.probabilities: 归一化概率 (0-1范围)")
    print("   - emotions.percentages: 百分比表示 (0-100%范围)")
    print("   - final_score: 综合情感评分 (0-100分)")
    print("   - dominant_emotion: 主导情感")
    print("   - confidence: 预测置信度")
    print("   - interpretation: 分数解释")

if __name__ == "__main__":
    main() 