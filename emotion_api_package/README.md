# DAiSEE情感识别API

🎯 **基于DAiSEE数据集的轻量级情感识别API，提供四个情感维度分析和综合评分**

## ✨ 功能特点

- 🎭 **四个情感维度**: Boredom(无聊)、Engagement(参与)、Confusion(困惑)、Frustration(挫折)
- 📊 **多种输出格式**: 原始分数、归一化概率、百分比占比
- 🎯 **综合评分**: 0-100分的加权情感评分
- ⚡ **高性能**: 平均推理时间 < 1ms，适合实时应用
- 💾 **轻量级**: 模型文件仅2.4MB
- 🔧 **易集成**: 提供Flask HTTP API和Python直接调用两种方式

## 📦 文件说明

```
emotion_api_package/
├── best_fast_daisee_model.pth     # 训练好的模型权重 (2.4MB)
├── emotion_recognition_api.py     # 核心API代码
├── test_emotion_api.py           # 测试验证脚本
├── demo_api_usage.py             # 使用演示脚本
├── start_api.py                  # 快速启动工具
├── requirements.txt              # 环境依赖
├── frontend_examples.md          # 前端集成示例
├── API_集成说明.md              # 详细文档
└── README.md                     # 本文件
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行快速启动工具
```bash
python start_api.py
```

选择操作：
- `1` - 运行API测试
- `2` - 启动API服务  
- `3` - 查看使用示例
- `4` - 运行完整演示

### 3. 直接使用API
```python
from emotion_recognition_api import EmotionRecognitionAPI

# 初始化
api = EmotionRecognitionAPI()

# 分析视频
result = api.predict_emotions('video.mp4', is_base64=False)

# 获取结果
print(f"最终得分: {result['final_score']:.2f}/100")
print(f"主导情感: {result['dominant_emotion']}")
```

## 📊 输出格式

```json
{
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
  "interpretation": "中性状态 - 正常表现"
}
```

## 🌐 HTTP API

### 启动服务
```bash
python emotion_recognition_api.py
# 服务运行在 http://localhost:5000
```

### 调用接口

**文件上传**
```bash
curl -X POST -F "video=@your_video.mp4" http://localhost:5000/predict_file
```

**Base64上传**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"video":"base64_video_data","is_base64":true}' \
  http://localhost:5000/predict
```

**健康检查**
```bash
curl http://localhost:5000/health
```

## 🎭 前端集成

详细的前端集成示例请查看 `frontend_examples.md`，包含：

- ⚛️ **React组件** - 基础版和高级版
- 🔷 **Vue.js组件** - 响应式设计
- 📱 **原生JavaScript** - 无框架依赖
- 🎨 **CSS样式** - 美观的UI组件

## 🔢 评分机制

### 加权算法
```
加权分数 = Σ(情感概率 × 情感权重)
最终得分 = 50 + 加权分数 × 25  # 映射到0-100范围
```

### 情感权重
- **Boredom(无聊)**: -1.0 (负面)
- **Engagement(参与)**: +1.0 (正面)
- **Confusion(困惑)**: -0.5 (轻微负面)
- **Frustration(挫折)**: -1.5 (强烈负面)

### 分数解释
- **75-100分**: 积极状态 - 高度参与和专注
- **60-74分**: 良好状态 - 积极参与
- **40-59分**: 中性状态 - 正常表现
- **25-39分**: 轻微消极 - 可能出现困惑或无聊
- **0-24分**: 消极状态 - 明显的挫折或严重无聊

## ✅ 模型验证

### 性能指标
- ✅ **验证MAE**: 0.6295 (相比基础模型提升10.19%)
- ✅ **推理速度**: 平均0.86ms
- ✅ **模型大小**: 2.4MB
- ✅ **权重有效性**: 已验证非随机初始化

### 各情感MAE
- Boredom: 0.9969
- Engagement: 0.5213  
- Confusion: 0.5659
- Frustration: 0.4341

## 🛠️ 开发工具

### 测试验证
```bash
python test_emotion_api.py
```

### 使用演示
```bash
python demo_api_usage.py
```

### 性能基准
- CPU模式: 可用
- GPU加速: CUDA支持
- 内存占用: < 500MB
- 支持格式: MP4, AVI, MOV, MKV等

## 📋 系统要求

- **Python**: 3.8+
- **PyTorch**: 1.8+
- **OpenCV**: 4.5+
- **Flask**: 2.0+
- **内存**: 至少2GB
- **CUDA**: 可选(GPU加速)

## 🔧 故障排除

### 常见问题

1. **模型加载失败**
   ```
   检查 best_fast_daisee_model.pth 文件是否存在
   ```

2. **CUDA错误**
   ```
   确保PyTorch版本与CUDA版本匹配
   或设置 CUDA_VISIBLE_DEVICES="" 使用CPU
   ```

3. **视频解码错误**
   ```
   pip install opencv-python
   确保视频文件完整且格式支持
   ```

4. **内存不足**
   ```
   减少batch_size或使用CPU模式
   ```

## 📞 技术支持

### 验证安装
```bash
python start_api.py  # 选择 1 - 运行API测试
```

### 查看日志
API运行时会显示详细的处理信息和错误提示

### 性能调优
- 单个视频分析: 1-3秒
- 批量处理: 支持
- 并发请求: 建议 < 10个

## 📄 许可证

本项目基于训练数据集和开源库开发，仅供学习和研究使用。

## 🎉 开始使用

1. **第一次使用**: 运行 `python start_api.py` 选择测试
2. **开发集成**: 查看 `frontend_examples.md`
3. **API文档**: 阅读 `API_集成说明.md`
4. **问题反馈**: 检查模型文件和依赖版本

---

**🚀 现在您拥有了一个完整的、高性能的情感识别API！** 