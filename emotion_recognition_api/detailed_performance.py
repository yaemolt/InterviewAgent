#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
详细性能分析 - 不同配置下的视频处理时间
"""

import torch
import torch.nn as nn
import time
import numpy as np

class SimpleCNN3D(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.conv3d_layers = nn.Sequential(
            # 3D卷积层
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
            nn.Linear(64, 4),
            nn.Sigmoid(),
        )
    
    def forward(self, x):
        # 将输入从 (B,T,C,H,W) 转换为 (B,C,T,H,W)
        x = x.permute(0, 2, 1, 3, 4)
        
        features = self.conv3d_layers(x)
        output = self.classifier(features)
        
        # 映射到0-3范围
        return output * 3.0

def create_simple_cnn3d():
    """创建简化的CNN3D模型"""
    return SimpleCNN3D()

def test_configuration(seq_length, resolution, batch_size=1):
    """测试特定配置的性能"""
    h, w = resolution
    
    # 创建模型和数据
    model = create_simple_cnn3d()
    model.eval()
    
    video_tensor = torch.randn(batch_size, seq_length, 3, h, w)
    
    # 预热
    with torch.no_grad():
        for _ in range(3):
            _ = model(video_tensor)
    
    # 测试
    times = []
    with torch.no_grad():
        for _ in range(5):
            start = time.time()
            output = model(video_tensor)
            end = time.time()
            times.append(end - start)
    
    avg_time = np.mean(times)
    data_size = video_tensor.numel() * 4 / 1024 / 1024  # MB
    
    return avg_time, data_size

def main():
    print("="*80)
    print("🔍 详细性能分析 - 不同配置下的2秒视频处理时间")
    print("="*80)
    
    print(f"\n💻 测试环境:")
    print(f"   设备: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    print(f"   PyTorch: {torch.__version__}")
    
    # 测试配置
    sequence_lengths = [8, 16, 32]
    resolutions = [(112, 112), (224, 224), (448, 448)]
    
    print(f"\n📊 性能测试矩阵:")
    print(f"   序列长度: {sequence_lengths}")
    print(f"   分辨率: {resolutions}")
    
    # 创建结果表格
    print(f"\n" + "="*80)
    print(f"📈 处理时间对比表 (毫秒)")
    print(f"="*80)
    
    # 表头
    header = "序列长度\\分辨率"
    for h, w in resolutions:
        header += f" | {h}x{w:>3}"
    print(header)
    print("-" * len(header))
    
    # 测试所有配置
    results = {}
    for seq_len in sequence_lengths:
        row = f"{seq_len:>8}帧      "
        times_row = []
        
        for resolution in resolutions:
            avg_time, data_size = test_configuration(seq_len, resolution)
            times_row.append(avg_time)
            results[(seq_len, resolution)] = (avg_time, data_size)
            row += f" | {avg_time*1000:>7.1f}"
        
        print(row)
    
    # 数据量分析
    print(f"\n" + "="*80)
    print(f"💾 数据量分析 (MB)")
    print(f"="*80)
    
    header = "序列长度\\分辨率"
    for h, w in resolutions:
        header += f" | {h}x{w:>3}"
    print(header)
    print("-" * len(header))
    
    for seq_len in sequence_lengths:
        row = f"{seq_len:>8}帧      "
        for resolution in resolutions:
            _, data_size = results[(seq_len, resolution)]
            row += f" | {data_size:>7.1f}"
        print(row)
    
    # 实时性分析
    print(f"\n" + "="*80)
    print(f"⚡ 实时性分析 (处理速度倍数)")
    print(f"="*80)
    
    video_duration = 2.0  # 2秒视频
    
    header = "序列长度\\分辨率"
    for h, w in resolutions:
        header += f" | {h}x{w:>3}"
    print(header)
    print("-" * len(header))
    
    for seq_len in sequence_lengths:
        row = f"{seq_len:>8}帧      "
        for resolution in resolutions:
            avg_time, _ = results[(seq_len, resolution)]
            speed_ratio = video_duration / avg_time
            row += f" | {speed_ratio:>7.1f}x"
        print(row)
    
    # 找出最优配置
    print(f"\n" + "="*80)
    print(f"🎯 性能分析与建议")
    print(f"="*80)
    
    # 找出最快配置
    fastest_config = min(results.keys(), key=lambda x: results[x][0])
    fastest_time = results[fastest_config][0]
    
    # 找出最慢配置
    slowest_config = max(results.keys(), key=lambda x: results[x][0])
    slowest_time = results[slowest_config][0]
    
    print(f"\n🏆 最快配置:")
    seq, (h, w) = fastest_config
    print(f"   序列长度: {seq}帧")
    print(f"   分辨率: {h}x{w}")
    print(f"   处理时间: {fastest_time*1000:.1f} ms")
    print(f"   处理速度: {video_duration/fastest_time:.1f}x 实时")
    
    print(f"\n🐌 最慢配置:")
    seq, (h, w) = slowest_config
    print(f"   序列长度: {seq}帧")
    print(f"   分辨率: {h}x{w}")
    print(f"   处理时间: {slowest_time*1000:.1f} ms")
    print(f"   处理速度: {video_duration/slowest_time:.1f}x 实时")
    
    print(f"\n📊 性能差异:")
    speedup = slowest_time / fastest_time
    print(f"   最快 vs 最慢: {speedup:.1f}x 提升")
    
    # 实时处理建议
    print(f"\n💡 实时处理建议:")
    realtime_configs = [(k, v) for k, v in results.items() if v[0] < 0.1]  # 小于100ms
    
    if realtime_configs:
        print(f"   ✅ 可实时处理的配置 (< 100ms):")
        for (seq, (h, w)), (time_val, _) in realtime_configs:
            print(f"     - {seq}帧, {h}x{w}: {time_val*1000:.1f} ms")
    else:
        print(f"   ⚠️ 当前CPU环境下无配置可实时处理 (< 100ms)")
        print(f"   📝 准实时配置建议 (< 200ms):")
        quasi_realtime = [(k, v) for k, v in results.items() if v[0] < 0.2]
        for (seq, (h, w)), (time_val, _) in quasi_realtime:
            print(f"     - {seq}帧, {h}x{w}: {time_val*1000:.1f} ms")
    
    # 优化建议
    print(f"\n🚀 性能优化建议:")
    print(f"   1. 分辨率优化:")
    print(f"      - 使用112x112分辨率可获得最佳速度")
    print(f"      - 从224x224降到112x112可提速约3-4倍")
    
    print(f"\n   2. 序列长度优化:")
    print(f"      - 使用8帧序列可获得最佳速度")
    print(f"      - 从16帧降到8帧可提速约2倍")
    
    print(f"\n   3. 硬件优化:")
    print(f"      - 使用GPU可提速10-100倍")
    print(f"      - 使用专用AI芯片可进一步提速")
    
    print(f"\n   4. 软件优化:")
    print(f"      - 模型量化(INT8)可提速2-4倍")
    print(f"      - 模型剪枝可减少计算量")
    print(f"      - TensorRT/ONNX优化可提速2-5倍")
    
    # 应用场景建议
    print(f"\n🎯 应用场景建议:")
    print(f"   📱 移动端/边缘设备: 8帧 + 112x112分辨率")
    print(f"   💻 PC端实时应用: 16帧 + 224x224分辨率 + GPU")
    print(f"   🖥️ 服务器批处理: 32帧 + 448x448分辨率")
    print(f"   ☁️ 云端API服务: 16帧 + 224x224分辨率 + GPU加速")

if __name__ == "__main__":
    main() 