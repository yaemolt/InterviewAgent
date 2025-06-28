#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DAiSEE模型性能测试 - 2秒视频处理时间测试
"""

import torch
import torch.nn as nn
import time
import numpy as np

print("="*70)
print("⏱️  DAiSEE模型性能测试 - 2秒视频处理时间")
print("="*70)

# 简化的CNN3D模型（避免torchvision依赖）
class SimpleCNN3D(nn.Module):
    def __init__(self, num_emotions=4):
        super().__init__()
        
        self.conv3d_layers = nn.Sequential(
            # 第一层3D卷积
            nn.Conv3d(3, 64, kernel_size=(3, 7, 7), stride=(1, 2, 2), padding=(1, 3, 3)),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            
            # 第二层3D卷积
            nn.Conv3d(64, 128, kernel_size=(3, 3, 3), stride=(1, 1, 1), padding=(1, 1, 1)),
            nn.BatchNorm3d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2)),
            
            # 第三层3D卷积
            nn.Conv3d(128, 256, kernel_size=(3, 3, 3), stride=(1, 1, 1), padding=(1, 1, 1)),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2)),
            
            # 全局平均池化
            nn.AdaptiveAvgPool3d((1, 1, 1))
        )
        
        # 情感分类头
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_emotions),
            nn.Sigmoid()  # 将输出映射到0-1，然后乘以3得到0-3范围
        )
        
    def forward(self, x):
        # x: (batch_size, sequence_length, channels, height, width)
        # 转换为3D卷积格式: (batch_size, channels, sequence_length, height, width)
        x = x.permute(0, 2, 1, 3, 4)
        
        features = self.conv3d_layers(x)
        output = self.classifier(features)
        
        # 映射到0-3范围
        return output * 3.0

# 简化的2D CNN + LSTM模型
class SimpleResNetLSTM(nn.Module):
    def __init__(self, num_emotions=4, hidden_dim=256):
        super().__init__()
        
        # 简化的2D CNN特征提取器
        self.feature_extractor = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten()
        )
        
        # LSTM时序建模
        self.lstm = nn.LSTM(
            input_size=256,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=0.3
        )
        
        # 分类头
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_emotions),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        batch_size, seq_len, c, h, w = x.size()
        
        # 逐帧提取特征
        frame_features = []
        for i in range(seq_len):
            frame = x[:, i, :, :, :]  # (batch_size, c, h, w)
            features = self.feature_extractor(frame)  # (batch_size, 256)
            frame_features.append(features)
        
        # 堆叠为序列
        sequence_features = torch.stack(frame_features, dim=1)  # (batch_size, seq_len, 256)
        
        # LSTM处理
        lstm_out, _ = self.lstm(sequence_features)  # (batch_size, seq_len, hidden_dim)
        
        # 使用最后一帧的输出
        final_output = lstm_out[:, -1, :]  # (batch_size, hidden_dim)
        
        # 分类
        emotion_scores = self.classifier(final_output) * 3.0
        
        return emotion_scores

def benchmark_model(model, input_tensor, model_name, num_runs=10):
    """性能基准测试"""
    model.eval()
    
    # 预热
    with torch.no_grad():
        for _ in range(3):
            _ = model(input_tensor)
    
    # 计时测试
    times = []
    with torch.no_grad():
        for i in range(num_runs):
            start_time = time.time()
            output = model(input_tensor)
            end_time = time.time()
            times.append(end_time - start_time)
    
    avg_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)
    max_time = np.max(times)
    
    print(f"\n📊 {model_name} 性能测试结果:")
    print(f"   平均时间: {avg_time*1000:.1f} ± {std_time*1000:.1f} ms")
    print(f"   最快时间: {min_time*1000:.1f} ms")
    print(f"   最慢时间: {max_time*1000:.1f} ms")
    print(f"   输出示例: {output[0].numpy()}")
    
    return avg_time

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n💻 测试设备: {device}")
    print(f"   PyTorch版本: {torch.__version__}")
    
    # 2秒视频参数
    fps = 30  # 每秒30帧
    video_duration = 2  # 2秒
    total_frames = fps * video_duration  # 60帧
    sequence_length = 16  # 模型输入序列长度
    height, width = 224, 224  # 图像分辨率
    
    print(f"\n📹 2秒视频参数:")
    print(f"   视频时长: {video_duration}秒")
    print(f"   帧率: {fps} fps")
    print(f"   总帧数: {total_frames}帧")
    print(f"   采样帧数: {sequence_length}帧")
    print(f"   图像分辨率: {height}x{width}")
    
    # 创建模拟2秒视频数据（批量大小为1）
    batch_size = 1
    video_tensor = torch.randn(batch_size, sequence_length, 3, height, width).to(device)
    
    print(f"   输入张量形状: {video_tensor.shape}")
    print(f"   数据大小: {video_tensor.numel() * 4 / 1024 / 1024:.2f} MB")
    
    # 测试CNN3D模型
    print(f"\n🧠 测试模型 1: 简化CNN3D")
    cnn3d_model = SimpleCNN3D(num_emotions=4).to(device)
    params_3d = sum(p.numel() for p in cnn3d_model.parameters())
    print(f"   参数量: {params_3d:,} ({params_3d/1e6:.1f}M)")
    
    time_3d = benchmark_model(cnn3d_model, video_tensor, "CNN3D")
    
    # 测试ResNet+LSTM模型
    print(f"\n🧠 测试模型 2: 简化ResNet+LSTM")
    lstm_model = SimpleResNetLSTM(num_emotions=4, hidden_dim=256).to(device)
    params_lstm = sum(p.numel() for p in lstm_model.parameters())
    print(f"   参数量: {params_lstm:,} ({params_lstm/1e6:.1f}M)")
    
    time_lstm = benchmark_model(lstm_model, video_tensor, "ResNet+LSTM")
    
    # 分析不同分辨率的影响
    print(f"\n📐 分辨率影响测试:")
    resolutions = [(112, 112), (224, 224), (448, 448)]
    
    for h, w in resolutions:
        test_tensor = torch.randn(1, sequence_length, 3, h, w).to(device)
        data_size = test_tensor.numel() * 4 / 1024 / 1024
        
        start_time = time.time()
        with torch.no_grad():
            _ = cnn3d_model(test_tensor)
        end_time = time.time()
        
        print(f"   {h}x{w}: {(end_time-start_time)*1000:.1f} ms (数据量: {data_size:.1f} MB)")
    
    # 总结
    print(f"\n" + "="*70)
    print(f"📋 2秒视频处理时间总结")
    print(f"="*70)
    print(f"🔸 CNN3D模型:")
    print(f"   处理时间: {time_3d*1000:.1f} ms")
    print(f"   处理速度: {video_duration/time_3d:.1f}x 实时速度")
    print(f"   参数量: {params_3d/1e6:.1f}M")
    
    print(f"\n🔸 ResNet+LSTM模型:")
    print(f"   处理时间: {time_lstm*1000:.1f} ms")
    print(f"   处理速度: {video_duration/time_lstm:.1f}x 实时速度")
    print(f"   参数量: {params_lstm/1e6:.1f}M")
    
    print(f"\n💡 性能分析:")
    if time_3d < 0.1:  # 小于100ms
        print(f"   ✅ CNN3D可以实时处理 (< 100ms)")
    else:
        print(f"   ⚠️ CNN3D处理较慢 (> 100ms)")
    
    if time_lstm < 0.2:  # 小于200ms
        print(f"   ✅ ResNet+LSTM可以准实时处理 (< 200ms)")
    else:
        print(f"   ⚠️ ResNet+LSTM处理较慢 (> 200ms)")
    
    print(f"\n🚀 优化建议:")
    print(f"   - 降低输入分辨率 (224→112) 可提速约 4x")
    print(f"   - 减少序列长度 (16→8) 可提速约 2x") 
    print(f"   - 使用GPU可提速 10-50x")
    print(f"   - 模型量化可提速 2-4x")
    
    fps_3d = 1.0 / time_3d
    fps_lstm = 1.0 / time_lstm
    print(f"\n📈 理论处理能力:")
    print(f"   CNN3D: {fps_3d:.1f} 个2秒视频/秒")
    print(f"   ResNet+LSTM: {fps_lstm:.1f} 个2秒视频/秒")

if __name__ == "__main__":
    main() 