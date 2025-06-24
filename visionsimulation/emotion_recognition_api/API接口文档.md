# 情绪识别API接口文档

## 概述

基于DAiSEE数据集训练的视频情绪识别API服务，能够实时分析视频中的情绪状态，返回四个维度的情绪评分：无聊、参与度、困惑、挫折感。

---

## 服务信息

- **服务名称**: DAiSEE Emotion Recognition API  
- **版本**: v1.0
- **基础URL**: `http://localhost:5000/api`
- **支持格式**: JSON
- **编码**: UTF-8

---

## 1. API接口列表

### 1.1 健康检查接口

**接口描述**: 检查服务运行状态和模型加载状态

```json
{
  "name": "health_check",
  "type": "function",
  "output": "json",
  "description": "健康检查接口，返回服务状态信息",
  "path": "emotion_api.py",
  "line": 172
}
```

**接口详情:**
- **路由**: `GET /api/health`
- **功能**: 检查服务运行状态
- **参数**: 无

**响应格式:**
```json
{
  "status": "healthy|unhealthy",
  "service": "DAiSEE Emotion Recognition API",
  "model_loaded": true,
  "device": "cpu|cuda",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### 1.2 视频情绪分析接口

**接口描述**: 主要功能接口，分析视频中的情绪状态

```json
{
  "name": "analyze_emotions",
  "type": "function", 
  "output": "json",
  "description": "分析视频情绪，返回四维度情绪评分",
  "path": "emotion_api.py",
  "line": 185
}
```

**接口详情:**
- **路由**: `POST /api/emotions/analyze`
- **功能**: 分析上传视频的情绪状态
- **请求格式**: `multipart/form-data`
- **参数**: 
  - `video` (file): 视频文件

**支持的视频格式:**
- `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

**响应格式 (成功):**
```json
{
  "success": true,
  "data": {
    "emotions": [
      {
        "emotion": "无聊",
        "score": 1.25,
        "level": 1,
        "percentage": 41.7
      },
      {
        "emotion": "参与度", 
        "score": 2.35,
        "level": 2,
        "percentage": 78.3
      },
      {
        "emotion": "困惑",
        "score": 0.85,
        "level": 1,
        "percentage": 28.3
      },
      {
        "emotion": "挫折感",
        "score": 1.15,
        "level": 1,
        "percentage": 38.3
      }
    ],
    "dominant_emotion": "参与度",
    "processing_time": "137.5ms",
    "overall_engagement": 2.35,
    "overall_confusion": 0.85
  },
  "metadata": {
    "filename": "test_video.mp4",
    "file_size": 2048576,
    "total_processing_time": "245.8ms",
    "frames_processed": 16,
    "frame_resolution": [224, 224]
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**响应格式 (失败):**
```json
{
  "success": false,
  "error": "错误类型",
  "response": "用户友好的错误信息"
}
```

### 1.3 测试接口

**接口描述**: 使用虚拟数据测试模型功能

```json
{
  "name": "test_with_dummy_data",
  "type": "function",
  "output": "json", 
  "description": "使用虚拟数据测试模型",
  "path": "emotion_api.py",
  "line": 267
}
```

**接口详情:**
- **路由**: `POST /api/emotions/test`
- **功能**: 测试模型推理功能
- **参数**: 无

**响应格式:**
```json
{
  "success": true,
  "data": {
    "emotions": [...],
    "dominant_emotion": "参与度",
    "processing_time": "45.2ms"
  },
  "metadata": {
    "test_mode": true,
    "dummy_data": true
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### 1.4 模型信息接口

**接口描述**: 获取可用模型列表和信息

```json
{
  "name": "get_available_models",
  "type": "function",
  "output": "json",
  "description": "获取可用的AI模型列表",
  "path": "emotion_api.py",
  "line": 289
}
```

**接口详情:**
- **路由**: `GET /api/models`
- **功能**: 获取可用模型信息
- **参数**: 无

**响应格式:**
```json
{
  "success": true,
  "models": [
    {
      "id": "cnn3d-daisee",
      "name": "CNN3D DAiSEE Model",
      "description": "基于3D卷积神经网络的情绪识别模型",
      "emotions": ["无聊", "参与度", "困惑", "挫折感"],
      "input_format": "video",
      "loaded": true
    }
  ],
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

---

## 2. 错误处理

### 2.1 错误码说明

| HTTP状态码 | 错误类型 | 描述 |
|-----------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 500 | Internal Server Error | 服务器内部错误 |

### 2.2 常见错误示例

**模型未加载:**
```json
{
  "success": false,
  "error": "Model not loaded",
  "response": "模型未加载，请检查服务状态"
}
```

**文件格式不支持:**
```json
{
  "success": false,
  "error": "Invalid file type",
  "response": "不支持的文件类型: .txt"
}
```

**视频处理失败:**
```json
{
  "success": false,
  "error": "Video processing failed",
  "response": "视频处理失败，请检查视频格式"
}
```

---

## 3. 使用示例

### 3.1 Python客户端示例

```python
import requests

# 健康检查
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# 上传视频分析
with open('test_video.mp4', 'rb') as video_file:
    files = {'video': video_file}
    response = requests.post(
        'http://localhost:5000/api/emotions/analyze', 
        files=files
    )
    result = response.json()
    
    if result['success']:
        emotions = result['data']['emotions']
        for emotion in emotions:
            print(f"{emotion['emotion']}: {emotion['score']:.2f} ({emotion['percentage']:.1f}%)")
    else:
        print(f"分析失败: {result['response']}")
```

### 3.2 cURL示例

```bash
# 健康检查
curl -X GET http://localhost:5000/api/health

# 视频分析
curl -X POST \
  -F "video=@test_video.mp4" \
  http://localhost:5000/api/emotions/analyze

# 测试接口
curl -X POST http://localhost:5000/api/emotions/test

# 获取模型信息
curl -X GET http://localhost:5000/api/models
```

### 3.3 JavaScript示例

```javascript
// 视频分析
async function analyzeVideo(videoFile) {
    const formData = new FormData();
    formData.append('video', videoFile);
    
    try {
        const response = await fetch('/api/emotions/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('主导情绪:', result.data.dominant_emotion);
            console.log('参与度:', result.data.overall_engagement);
            console.log('处理时间:', result.data.processing_time);
        } else {
            console.error('分析失败:', result.response);
        }
    } catch (error) {
        console.error('请求失败:', error);
    }
}
```

---

## 4. 性能指标

### 4.1 处理性能

| 配置 | 处理时间 | 实时倍数 | 适用场景 |
|------|----------|----------|----------|
| 8帧 + 112x112 | ~35ms | 57x | 实时应用 |
| 16帧 + 224x224 | ~137ms | 15x | 标准配置 |
| 32帧 + 224x224 | ~239ms | 8x | 高精度分析 |

### 4.2 系统要求

**最低要求:**
- CPU: 双核2.0GHz
- 内存: 2GB RAM
- Python: 3.7+
- PyTorch: 1.8+

**推荐配置:**
- CPU: 四核3.0GHz 或 GPU
- 内存: 8GB RAM
- Python: 3.8+
- PyTorch: 2.0+

---

## 5. 部署说明

### 5.1 依赖安装

```bash
pip install flask flask-cors torch torchvision opencv-python numpy
```

### 5.2 启动服务

```bash
cd face_recognize/PyTorch-DSSN-MER-main
python emotion_api.py
```

### 5.3 服务配置

- **端口**: 5000 (可在代码中修改)
- **主机**: 0.0.0.0 (允许外部访问)
- **调试模式**: True (生产环境建议关闭)

---

**文档版本**: v1.0  
**更新时间**: 2024年  
**维护者**: 情绪识别系统开发团队 