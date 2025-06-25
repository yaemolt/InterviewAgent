#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAiSEE情感识别API使用演示
展示四个情感标签、占比和最终打分
"""

import requests
import json
import base64
import os
from emotion_recognition_api import EmotionRecognitionAPI

def demo_direct_api():
    """直接使用API类的演示"""
    print("🎯 方式1: 直接使用API类")
    print("=" * 50)
    
    # 初始化API
    api = EmotionRecognitionAPI()
    
    # 找一个测试视频
    test_video = 'daisee_hf/DAiSEE/DataSet/Validation/400022/4000221011/4000221011.avi'
    
    if not os.path.exists(test_video):
        print("❌ 测试视频不存在")
        return
    
    print(f"📹 测试视频: {test_video}")
    
    # 预测情感
    result = api.predict_emotions(test_video, is_base64=False)
    
    # 展示结果
    print_emotion_result(result)

def demo_flask_api():
    """Flask API服务演示"""
    print("\n🎯 方式2: Flask API服务")
    print("=" * 50)
    
    # 启动说明
    print("要使用Flask API，请运行:")
    print("python emotion_recognition_api.py")
    print("\n然后使用以下代码调用API:")
    print("""
# POST /predict 接口示例
import requests
import base64

# 读取视频文件
with open('video.mp4', 'rb') as f:
    video_base64 = base64.b64encode(f.read()).decode()

# 调用API
response = requests.post('http://localhost:5000/predict', 
                        json={
                            'video': video_base64,
                            'is_base64': True
                        })

result = response.json()
print(result)
""")

def print_emotion_result(result):
    """格式化打印情感识别结果"""
    print("\n✨ 情感识别结果")
    print("-" * 30)
    
    # 基本信息
    print(f"🕐 时间戳: {result['timestamp']}")
    print(f"🎯 最终得分: {result['final_score']:.2f}/100")
    print(f"🏆 主导情感: {result['dominant_emotion']}")
    print(f"📊 置信度: {result['confidence']:.3f}")
    print(f"💭 解释: {result['interpretation']}")
    
    # 详细情感分析
    print(f"\n🎭 四个情感维度分析:")
    print(f"{'情感':12} {'原始分数':>10} {'概率':>8} {'占比':>8}")
    print("-" * 45)
    
    emotions = result['emotions']
    for emotion in ['Boredom', 'Engagement', 'Confusion', 'Frustration']:
        raw = emotions['raw_scores'][emotion]
        prob = emotions['probabilities'][emotion]
        pct = emotions['percentages'][emotion]
        
        # 使用表情符号
        emoji = {
            'Boredom': '😴',
            'Engagement': '😊', 
            'Confusion': '😕',
            'Frustration': '😤'
        }[emotion]
        
        print(f"{emoji} {emotion:10} {raw:8.3f} {prob:8.3f} {pct:7.1f}%")
    
    # 情感分布可视化
    print(f"\n📈 情感占比可视化:")
    for emotion in ['Boredom', 'Engagement', 'Confusion', 'Frustration']:
        pct = emotions['percentages'][emotion]
        bar_length = int(pct / 2)  # 50% = 25字符
        bar = "█" * bar_length + "░" * (25 - bar_length)
        print(f"{emotion:12} |{bar}| {pct:5.1f}%")
    
    # 加权评分说明
    print(f"\n⚖️ 加权评分机制:")
    print(f"   无聊(Boredom):     权重 -1.0  (负面情绪)")
    print(f"   参与(Engagement):  权重 +1.0  (正面情绪)")
    print(f"   困惑(Confusion):   权重 -0.5  (轻微负面)")
    print(f"   挫折(Frustration): 权重 -1.5  (强烈负面)")
    
    # 分数区间解释
    print(f"\n📊 分数区间含义:")
    print(f"   75-100分: 积极状态 - 高度参与和专注")
    print(f"   60-74分:  良好状态 - 积极参与")
    print(f"   40-59分:  中性状态 - 正常表现")
    print(f"   25-39分:  轻微消极 - 可能出现困惑或无聊")
    print(f"   0-24分:   消极状态 - 明显的挫折或严重无聊")
    
    # 应用建议
    score = result['final_score']
    print(f"\n💡 应用建议:")
    if score >= 75:
        print(f"   🎉 状态极佳！继续保持当前的学习/工作节奏")
    elif score >= 60:
        print(f"   ✅ 状态良好，可适当增加挑战性内容")
    elif score >= 40:
        print(f"   📝 状态正常，可继续当前活动")
    elif score >= 25:
        print(f"   ⚠️ 注意力下降，建议调整内容或休息")
    else:
        print(f"   🚨 状态不佳，强烈建议休息或改变活动")

def demo_json_output():
    """展示标准JSON输出格式"""
    print("\n🎯 标准JSON输出格式")
    print("=" * 50)
    
    # 示例输出
    example_output = {
        "timestamp": "2025-06-25T16:05:41.411037",
        "emotions": {
            "raw_scores": {
                "Boredom": 0.792,
                "Engagement": 2.315,
                "Confusion": 0.257,
                "Frustration": 0.155
            },
            "probabilities": {
                "Boredom": 0.149,
                "Engagement": 0.684,
                "Confusion": 0.087,
                "Frustration": 0.079
            },
            "percentages": {
                "Boredom": 14.9,
                "Engagement": 68.4,
                "Confusion": 8.7,
                "Frustration": 7.9
            }
        },
        "final_score": 59.33,
        "dominant_emotion": "Engagement",
        "confidence": 0.684,
        "interpretation": "中性状态 - 正常表现",
        "model_info": {
            "mae": 0.6295,
            "accuracy_improvement": "+10.19%"
        }
    }
    
    print("📄 JSON格式:")
    print(json.dumps(example_output, indent=2, ensure_ascii=False))
    
    print("\n📋 字段说明:")
    print("- timestamp: 预测时间戳")
    print("- emotions.raw_scores: 原始模型输出 (0-3范围)")
    print("- emotions.probabilities: 软件max归一化概率 (0-1)")
    print("- emotions.percentages: 百分比表示 (0-100%)")
    print("- final_score: 综合情感评分 (0-100分)")
    print("- dominant_emotion: 占比最高的情感")
    print("- confidence: 主导情感的置信度")
    print("- interpretation: 分数的文字解释")
    print("- model_info: 模型性能信息")

def main():
    """主函数"""
    print("🎉 DAiSEE情感识别API使用演示")
    print("=" * 60)
    
    # 检查模型文件
    if not os.path.exists('best_fast_daisee_model.pth'):
        print("❌ 模型文件不存在: best_fast_daisee_model.pth")
        print("请先运行 quick_optimized_training.py 训练模型")
        return
    
    # 演示直接API使用
    demo_direct_api()
    
    # 演示Flask API
    demo_flask_api()
    
    # 展示JSON格式
    demo_json_output()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成!")
    
    print("\n🔗 集成指南:")
    print("1. 直接使用: from emotion_recognition_api import EmotionRecognitionAPI")
    print("2. HTTP API: python emotion_recognition_api.py (启动Flask服务)")
    print("3. 输出格式: 四个情感标签 + 占比 + 最终打分")
    print("4. 性能: 平均推理时间 < 1ms，适合实时应用")

if __name__ == "__main__":
    main() 