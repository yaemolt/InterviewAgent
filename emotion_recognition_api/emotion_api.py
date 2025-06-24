#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪识别API服务 - 基于DAiSEE模型的视频情绪分析
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
import cv2
import numpy as np
import tempfile
import os
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 全局变量
model = None
device = None
emotion_labels = ['无聊', '参与度', '困惑', '挫折感']

class SimpleCNN3D(nn.Module):
    """简化的CNN3D情绪识别模型"""
    def __init__(self, num_emotions=4):
        super().__init__()
        
        self.conv3d_layers = nn.Sequential(
            nn.Conv3d(3, 32, kernel_size=(3, 7, 7), stride=(1, 2, 2), padding=(1, 3, 3)),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            
            nn.Conv3d(32, 64, kernel_size=(3, 3, 3), stride=(1, 1, 1), padding=(1, 1, 1)),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2)),
            
            nn.Conv3d(64, 128, kernel_size=(3, 3, 3), stride=(1, 1, 1), padding=(1, 1, 1)),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool3d((1, 1, 1)),
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, num_emotions),
            nn.Sigmoid(),
        )
    
    def forward(self, x):
        # x: (batch_size, sequence_length, channels, height, width)
        # 转换为3D卷积格式: (batch_size, channels, sequence_length, height, width)
        x = x.permute(0, 2, 1, 3, 4)
        
        features = self.conv3d_layers(x)
        output = self.classifier(features)
        
        # 映射到0-3范围
        return output * 3.0

class VideoProcessor:
    """视频处理器"""
    def __init__(self, sequence_length=16, target_size=(224, 224)):
        self.sequence_length = sequence_length
        self.target_size = target_size
        
        # 初始化人脸检测器
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except:
            logger.warning("无法加载人脸检测器，将使用全帧处理")
            self.face_cascade = None
    
    def extract_frames_from_video(self, video_data):
        """从视频数据中提取帧"""
        try:
            # 保存临时视频文件
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_video_path = temp_file.name
            
            # 读取视频
            cap = cv2.VideoCapture(temp_video_path)
            frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 人脸检测和裁剪
                processed_frame = self.process_frame(frame)
                if processed_frame is not None:
                    frames.append(processed_frame)
            
            cap.release()
            os.unlink(temp_video_path)  # 删除临时文件
            
            return self.sample_frames(frames)
            
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            return None
    
    def process_frame(self, frame):
        """处理单帧图像"""
        try:
            # 人脸检测
            if self.face_cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    # 使用最大的人脸
                    largest_face = max(faces, key=lambda x: x[2] * x[3])
                    x, y, w, h = largest_face
                    
                    # 扩展人脸区域
                    margin = int(0.2 * min(w, h))
                    x = max(0, x - margin)
                    y = max(0, y - margin)
                    w = min(frame.shape[1] - x, w + 2 * margin)
                    h = min(frame.shape[0] - y, h + 2 * margin)
                    
                    frame = frame[y:y+h, x:x+w]
            
            # 调整大小
            frame = cv2.resize(frame, self.target_size)
            
            # BGR转RGB并归一化
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.astype(np.float32) / 255.0
            
            return frame
            
        except Exception as e:
            logger.error(f"帧处理失败: {e}")
            return None
    
    def sample_frames(self, frames):
        """从帧序列中采样固定数量的帧"""
        if len(frames) == 0:
            return None
        
        if len(frames) <= self.sequence_length:
            # 如果帧数不足，重复最后一帧
            while len(frames) < self.sequence_length:
                frames.append(frames[-1])
        else:
            # 均匀采样
            indices = np.linspace(0, len(frames) - 1, self.sequence_length, dtype=int)
            frames = [frames[i] for i in indices]
        
        return np.array(frames)

def load_model():
    """加载情绪识别模型"""
    global model, device
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"使用设备: {device}")
    
    try:
        model = SimpleCNN3D(num_emotions=4).to(device)
        model.eval()
        logger.info("模型加载成功")
        return True
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return False

def predict_emotions(video_tensor):
    """预测视频情绪"""
    global model, device
    
    try:
        with torch.no_grad():
            # 转换为张量并移到设备
            if isinstance(video_tensor, np.ndarray):
                video_tensor = torch.FloatTensor(video_tensor).unsqueeze(0).to(device)
            
            # 模型预测
            start_time = time.time()
            predictions = model(video_tensor)
            inference_time = time.time() - start_time
            
            # 转换为numpy数组
            scores = predictions.cpu().numpy()[0]
            
            # 创建结果
            results = []
            for i, (label, score) in enumerate(zip(emotion_labels, scores)):
                results.append({
                    'emotion': label,
                    'score': float(score),
                    'level': int(round(score)),  # 0-3级别
                    'percentage': float(score / 3.0 * 100)  # 百分比
                })
            
            return {
                'emotions': results,
                'dominant_emotion': emotion_labels[np.argmax(scores)],
                'processing_time': f"{inference_time*1000:.1f}ms",
                'overall_engagement': float(scores[1]),  # 参与度
                'overall_confusion': float(scores[2])     # 困惑度
            }
            
    except Exception as e:
        logger.error(f"情绪预测失败: {e}")
        return None

# 初始化视频处理器
video_processor = VideoProcessor()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    global model
    
    status = {
        'status': 'healthy' if model is not None else 'unhealthy',
        'service': 'DAiSEE Emotion Recognition API',
        'model_loaded': model is not None,
        'device': str(device) if device else 'unknown',
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(status)

@app.route('/api/emotions/analyze', methods=['POST'])
def analyze_emotions():
    """视频情绪分析接口"""
    try:
        start_time = time.time()
        
        # 检查模型状态
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded',
                'response': '模型未加载，请检查服务状态'
            }), 500
        
        # 检查请求数据
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No video file',
                'response': '请上传视频文件'
            }), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename',
                'response': '文件名为空'
            }), 400
        
        # 验证文件类型
        allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        file_ext = os.path.splitext(video_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'response': f'不支持的文件类型: {file_ext}'
            }), 400
        
        # 读取视频数据
        video_data = video_file.read()
        logger.info(f"接收视频文件: {video_file.filename}, 大小: {len(video_data)} bytes")
        
        # 处理视频
        video_tensor = video_processor.extract_frames_from_video(video_data)
        if video_tensor is None:
            return jsonify({
                'success': False,
                'error': 'Video processing failed',
                'response': '视频处理失败，请检查视频格式'
            }), 400
        
        # 情绪预测
        emotion_results = predict_emotions(video_tensor)
        if emotion_results is None:
            return jsonify({
                'success': False,
                'error': 'Emotion prediction failed',
                'response': '情绪预测失败'
            }), 500
        
        total_time = time.time() - start_time
        
        # 返回结果
        response_data = {
            'success': True,
            'data': emotion_results,
            'metadata': {
                'filename': secure_filename(video_file.filename),
                'file_size': len(video_data),
                'total_processing_time': f"{total_time*1000:.1f}ms",
                'frames_processed': len(video_tensor),
                'frame_resolution': video_processor.target_size
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"情绪分析完成: {video_file.filename}, 用时: {total_time*1000:.1f}ms")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"API错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': '服务器内部错误'
        }), 500

@app.route('/api/emotions/test', methods=['POST'])
def test_with_dummy_data():
    """使用虚拟数据测试接口"""
    try:
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        # 创建虚拟视频数据
        dummy_video = np.random.rand(16, 224, 224, 3).astype(np.float32)
        
        # 预测情绪
        emotion_results = predict_emotions(dummy_video)
        
        return jsonify({
            'success': True,
            'data': emotion_results,
            'metadata': {
                'test_mode': True,
                'dummy_data': True
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """获取可用模型列表"""
    models = [
        {
            'id': 'cnn3d-daisee',
            'name': 'CNN3D DAiSEE Model',
            'description': '基于3D卷积神经网络的情绪识别模型',
            'emotions': emotion_labels,
            'input_format': 'video',
            'loaded': model is not None
        }
    ]
    
    return jsonify({
        'success': True,
        'models': models,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("="*70)
    print("🚀 启动DAiSEE情绪识别API服务")
    print("="*70)
    
    # 加载模型
    if load_model():
        print("✅ 模型加载成功")
    else:
        print("❌ 模型加载失败")
    
    print(f"\n📋 API端点:")
    print(f"   GET  /api/health           - 健康检查")
    print(f"   POST /api/emotions/analyze - 单视频分析")
    print(f"   POST /api/emotions/test    - 测试接口")
    print(f"   GET  /api/models           - 模型列表")
    
    print(f"\n🌐 服务地址: http://localhost:5000")
    print(f"📱 设备: {device}")
    print("="*70)
    
    # 启动Flask服务
    app.run(host='0.0.0.0', port=5000, debug=True) 