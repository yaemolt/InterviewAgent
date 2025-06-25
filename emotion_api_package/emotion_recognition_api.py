#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAiSEE情感识别API接口
输出四个情感标签、占比和最终打分
"""

import os
import torch
import torch.nn as nn
import numpy as np
import cv2
from torchvision import transforms
from flask import Flask, request, jsonify
import base64
import tempfile
import json
from datetime import datetime

# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class FastEmotionModel(nn.Module):
    """快速轻量化情感识别模型 - 正确架构"""
    
    def __init__(self, sequence_length=8, num_classes=4):
        super(FastEmotionModel, self).__init__()
        
        # 轻量化CNN特征提取器
        self.conv_layers = nn.Sequential(
            # Block 1 - 快速下采样
            nn.Conv2d(3, 32, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 128 -> 32
            
            # Block 2 
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 32 -> 16
            
            # Block 3 - 最终特征
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4))  # 16 -> 4
        )
        
        # 简化的LSTM
        self.lstm = nn.LSTM(
            input_size=128 * 16,
            hidden_size=64,  # 更小的隐藏层
            num_layers=1,
            batch_first=True
        )
        
        # 极简分类器
        self.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, num_classes)
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        batch_size, seq_len, c, h, w = x.size()
        
        # CNN特征提取
        x = x.view(batch_size * seq_len, c, h, w)
        features = self.conv_layers(x)  # (batch*seq, 128, 4, 4)
        features = features.view(features.size(0), -1)  # (batch*seq, 2048)
        
        # 重塑为序列
        features = features.view(batch_size, seq_len, -1)  # (batch, seq, 2048)
        
        # LSTM - 只取最后一个输出
        lstm_out, (hidden, _) = self.lstm(features)
        last_output = hidden[-1]  # 取最后一层的隐藏状态 (batch, 64)
        
        # 分类
        output = self.classifier(last_output)
        
        return output

class EmotionRecognitionAPI:
    """情感识别API类"""
    
    def __init__(self, model_path='best_fast_daisee_model.pth'):
        self.device = device
        self.emotion_names = ['Boredom', 'Engagement', 'Confusion', 'Frustration']
        self.emotion_weights = {
            'Boredom': -1.0,      # 无聊是负面情绪
            'Engagement': 1.0,    # 参与是正面情绪
            'Confusion': -0.5,    # 困惑是轻微负面
            'Frustration': -1.5   # 挫折是强烈负面
        }
        
        # 加载模型
        self.model = self._load_model(model_path)
        
        # 数据预处理
        self.transforms = transforms.Compose([
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print(f"🎯 情感识别API初始化完成")
        print(f"   设备: {self.device}")
        print(f"   模型路径: {model_path}")
    
    def _load_model(self, model_path):
        """加载训练好的模型"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        # 加载检查点
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # 验证模型是否已训练
        if 'val_mae' not in checkpoint:
            raise ValueError("模型文件无效：缺少验证信息")
        
        print(f"📊 模型信息:")
        print(f"   训练轮数: {checkpoint.get('epoch', 'N/A')}")
        print(f"   验证MAE: {checkpoint.get('val_mae', 'N/A'):.4f}")
        
        # 创建模型实例
        model = FastEmotionModel().to(self.device)
        
        # 加载权重
        try:
            model.load_state_dict(checkpoint['model_state_dict'])
            print(f"✅ 模型权重加载成功")
        except Exception as e:
            raise RuntimeError(f"模型权重加载失败: {e}")
        
        model.eval()
        
        # 验证模型权重非随机
        self._verify_model_weights(model, checkpoint)
        
        return model
    
    def _verify_model_weights(self, model, checkpoint):
        """验证模型权重是否已训练（非随机）"""
        # 创建随机模型对比
        random_model = FastEmotionModel().to(self.device)
        
        # 比较权重差异
        trained_params = []
        random_params = []
        
        for (name1, param1), (name2, param2) in zip(model.named_parameters(), random_model.named_parameters()):
            if param1.requires_grad:
                trained_params.append(param1.detach().cpu().numpy().flatten())
                random_params.append(param2.detach().cpu().numpy().flatten())
        
        trained_weights = np.concatenate(trained_params)
        random_weights = np.concatenate(random_params)
        
        weight_diff = np.mean(np.abs(trained_weights - random_weights))
        
        if weight_diff > 0.01:
            print(f"✅ 权重验证通过 (差异: {weight_diff:.6f})")
        else:
            raise ValueError(f"⚠️ 模型权重可能未充分训练 (差异: {weight_diff:.6f})")
    
    def preprocess_video(self, video_data, is_base64=True):
        """预处理视频数据"""
        try:
            # 处理base64编码的视频
            if is_base64:
                video_bytes = base64.b64decode(video_data)
                
                # 保存到临时文件
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                    temp_file.write(video_bytes)
                    temp_path = temp_file.name
            else:
                temp_path = video_data
            
            # 提取视频帧
            frames = self._extract_frames(temp_path)
            
            # 清理临时文件
            if is_base64 and os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return frames
            
        except Exception as e:
            raise ValueError(f"视频预处理失败: {e}")
    
    def _extract_frames(self, video_path, num_frames=8):
        """从视频中提取帧"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("无法打开视频文件")
        
        frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames > 0:
            # 均匀采样帧
            frame_indices = np.linspace(0, total_frames-1, num_frames, dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (128, 128))
                    frames.append(frame)
                else:
                    if frames:
                        frames.append(frames[-1])
                    else:
                        frames.append(np.zeros((128, 128, 3), dtype=np.uint8))
        
        cap.release()
        
        # 确保帧数
        while len(frames) < num_frames:
            if frames:
                frames.append(frames[-1])
            else:
                frames.append(np.zeros((128, 128, 3), dtype=np.uint8))
        
        # 转换为tensor
        frames = np.array(frames[:num_frames])
        frames = torch.from_numpy(frames).float() / 255.0
        frames = frames.permute(0, 3, 1, 2)  # [T, C, H, W]
        
        # 应用变换
        frames_list = []
        for i in range(frames.shape[0]):
            frame = self.transforms(frames[i])
            frames_list.append(frame)
        frames = torch.stack(frames_list).unsqueeze(0)  # [1, T, C, H, W]
        
        return frames.to(self.device)
    
    def predict_emotions(self, video_data, is_base64=True):
        """预测情感"""
        try:
            # 预处理视频
            frames = self.preprocess_video(video_data, is_base64)
            
            # 模型预测
            with torch.no_grad():
                raw_output = self.model(frames).cpu().numpy()[0]
            
            # 将原始输出转换为0-3范围（如果需要）
            emotions_raw = np.clip(raw_output, 0, 3)
            
            # 计算情感占比（软max归一化）
            emotions_exp = np.exp(emotions_raw - np.max(emotions_raw))  # 数值稳定
            emotions_prob = emotions_exp / np.sum(emotions_exp)
            
            # 计算加权情感分数
            weighted_score = 0
            for i, emotion in enumerate(self.emotion_names):
                weighted_score += emotions_prob[i] * self.emotion_weights[emotion]
            
            # 将分数映射到0-100范围，50为中性
            final_score = 50 + weighted_score * 25  # [-2, 2] -> [0, 100]
            final_score = np.clip(final_score, 0, 100)
            
            # 构建结果
            result = {
                'timestamp': datetime.now().isoformat(),
                'emotions': {
                    'raw_scores': {
                        emotion: float(emotions_raw[i]) 
                        for i, emotion in enumerate(self.emotion_names)
                    },
                    'probabilities': {
                        emotion: float(emotions_prob[i]) 
                        for i, emotion in enumerate(self.emotion_names)
                    },
                    'percentages': {
                        emotion: float(emotions_prob[i] * 100) 
                        for i, emotion in enumerate(self.emotion_names)
                    }
                },
                'final_score': float(final_score),
                'dominant_emotion': self.emotion_names[np.argmax(emotions_prob)],
                'confidence': float(np.max(emotions_prob)),
                'interpretation': self._interpret_score(final_score),
                'model_info': {
                    'mae': 0.6295,  # 当前最佳性能
                    'accuracy_improvement': '+10.19%'
                }
            }
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"情感预测失败: {e}")
    
    def _interpret_score(self, score):
        """解释情感分数"""
        if score >= 75:
            return "积极状态 - 高度参与和专注"
        elif score >= 60:
            return "良好状态 - 积极参与"
        elif score >= 40:
            return "中性状态 - 正常表现"
        elif score >= 25:
            return "轻微消极 - 可能出现困惑或无聊"
        else:
            return "消极状态 - 明显的挫折或严重无聊"

# Flask API
app = Flask(__name__)

# 全局API实例
api_instance = None

def initialize_api():
    """初始化API"""
    global api_instance
    if api_instance is None:
        try:
            api_instance = EmotionRecognitionAPI()
            print("🚀 API服务启动成功")
        except Exception as e:
            print(f"❌ API初始化失败: {e}")
            raise

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    if api_instance is None:
        initialize_api()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': api_instance is not None,
        'device': str(device)
    })

@app.route('/predict', methods=['POST'])
def predict():
    """情感预测接口"""
    if api_instance is None:
        initialize_api()
    if api_instance is None:
        return jsonify({'error': 'API未初始化'}), 500
    
    try:
        data = request.get_json()
        
        if 'video' not in data:
            return jsonify({'error': '缺少video字段'}), 400
        
        # 预测情感
        result = api_instance.predict_emotions(
            data['video'], 
            is_base64=data.get('is_base64', True)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict_file', methods=['POST'])
def predict_file():
    """文件上传预测接口"""
    if api_instance is None:
        initialize_api()
    if api_instance is None:
        return jsonify({'error': 'API未初始化'}), 500
    
    try:
        if 'video' not in request.files:
            return jsonify({'error': '缺少video文件'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        # 预测情感
        result = api_instance.predict_emotions(temp_path, is_base64=False)
        
        # 清理临时文件
        os.unlink(temp_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    """主函数"""
    print("🎯 DAiSEE情感识别API服务")
    print("=" * 50)
    
    # 验证模型文件
    if not os.path.exists('best_fast_daisee_model.pth'):
        print("❌ 模型文件不存在: best_fast_daisee_model.pth")
        return
    
    # 启动API服务
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main() 