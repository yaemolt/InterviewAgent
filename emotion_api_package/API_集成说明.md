# DAiSEE情感识别API - 完整集成说明

## 🎯 概述

本API基于优化后的DAiSEE情感识别模型，提供四个情感维度的分析和综合评分：

- **四个情感标签**: Boredom(无聊)、Engagement(参与)、Confusion(困惑)、Frustration(挫折)
- **占比计算**: 每个情感的归一化概率和百分比
- **最终打分**: 0-100分的综合情感评分
- **实时性能**: 平均推理时间 < 1ms

## ✅ 模型验证结果

### 权重有效性验证
- ✅ 模型权重已训练（权重差异: 0.059）
- ✅ 验证MAE: 0.6295 （相比基础模型提升10.19%）
- ✅ 训练轮数: 4个epoch
- ✅ 模型大小: 2.4MB（轻量化设计）

### 性能基准
- ⚡ 平均推理时间: 0.86ms
- 🚀 性能等级: 优秀 - 适合实时应用
- 📊 GPU加速: 支持CUDA
- 💾 内存占用: 低

## 🎭 输出格式

### 完整JSON响应结构
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
  "interpretation": "中性状态 - 正常表现",
  "model_info": {
    "mae": 0.6295,
    "accuracy_improvement": "+10.19%"
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | string | 预测时间戳 |
| `emotions.raw_scores` | object | 原始模型输出 (0-3范围) |
| `emotions.probabilities` | object | 软max归一化概率 (0-1) |
| `emotions.percentages` | object | 百分比表示 (0-100%) |
| `final_score` | float | 综合情感评分 (0-100分) |
| `dominant_emotion` | string | 占比最高的情感 |
| `confidence` | float | 主导情感的置信度 |
| `interpretation` | string | 分数的文字解释 |
| `model_info` | object | 模型性能信息 |

## 🔢 评分机制

### 加权评分算法
```
加权分数 = Σ(情感概率 × 情感权重)
最终得分 = 50 + 加权分数 × 25  # 映射到0-100范围
```

### 情感权重设置
- **Boredom(无聊)**: -1.0 (负面情绪)
- **Engagement(参与)**: +1.0 (正面情绪)  
- **Confusion(困惑)**: -0.5 (轻微负面)
- **Frustration(挫折)**: -1.5 (强烈负面)

### 分数区间含义
- **75-100分**: 积极状态 - 高度参与和专注
- **60-74分**: 良好状态 - 积极参与
- **40-59分**: 中性状态 - 正常表现
- **25-39分**: 轻微消极 - 可能出现困惑或无聊
- **0-24分**: 消极状态 - 明显的挫折或严重无聊

## 🚀 使用方式

### 方式1: 直接导入使用

```python
from emotion_recognition_api import EmotionRecognitionAPI

# 初始化API
api = EmotionRecognitionAPI()

# 预测情感（视频文件路径）
result = api.predict_emotions('video.mp4', is_base64=False)

# 获取结果
final_score = result['final_score']
emotions = result['emotions']['percentages']
print(f"最终得分: {final_score:.2f}/100")
print(f"情感占比: {emotions}")
```

### 方式2: Flask HTTP API

#### 启动服务
```bash
python emotion_recognition_api.py
# 服务将在 http://localhost:5000 启动
```

#### 调用API

**POST /predict** (Base64视频)
```python
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
```

**POST /predict_file** (文件上传)
```python
import requests

# 上传视频文件
files = {'video': open('video.mp4', 'rb')}
response = requests.post('http://localhost:5000/predict_file', files=files)

result = response.json()
```

**GET /health** (健康检查)
```python
response = requests.get('http://localhost:5000/health')
status = response.json()
```

## 📊 示例结果展示

### 文字可视化
```
🎭 四个情感维度分析:
😴 Boredom       0.792    0.149    14.9%
😊 Engagement    2.315    0.684    68.4%
😕 Confusion     0.257    0.087     8.7%
😤 Frustration   0.155    0.079     7.9%

📈 情感占比可视化:
Boredom      |███████░░░░░░░░░░░░░░░░░░|  14.9%
Engagement   |██████████████████████████████████|  68.4%
Confusion    |████░░░░░░░░░░░░░░░░░░░░░|   8.7%
Frustration  |███░░░░░░░░░░░░░░░░░░░░░░|   7.9%
```

### 应用建议
根据最终得分自动生成建议：
- 📝 状态正常，可继续当前活动 (40-59分)
- ✅ 状态良好，可适当增加挑战性内容 (60-74分)
- 🎉 状态极佳！继续保持当前的学习/工作节奏 (75-100分)

## 🛠️ 部署要求

### 环境依赖
```bash
pip install torch torchvision opencv-python flask numpy
```

### 系统要求
- Python 3.8+
- PyTorch 1.8+
- CUDA支持（可选，CPU也可运行）
- 内存: 至少2GB
- 存储: 模型文件约2.4MB

### 文件清单
- `best_fast_daisee_model.pth` - 训练好的模型权重
- `emotion_recognition_api.py` - API核心代码
- `test_emotion_api.py` - 测试验证脚本
- `demo_api_usage.py` - 使用演示
- `API_集成说明.md` - 本文档

## 🔧 集成指南

### 前端集成示例

#### React组件
```jsx
import React, { useState } from 'react';

function EmotionAnalyzer() {
  const [result, setResult] = useState(null);
  
  const analyzeVideo = async (videoFile) => {
    const formData = new FormData();
    formData.append('video', videoFile);
    
    const response = await fetch('/predict_file', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    setResult(data);
  };
  
  return (
    <div>
      {result && (
        <div>
          <h3>情感分析结果</h3>
          <p>最终得分: {result.final_score.toFixed(2)}/100</p>
          <p>主导情感: {result.dominant_emotion}</p>
          <p>解释: {result.interpretation}</p>
          
          <h4>情感占比:</h4>
          {Object.entries(result.emotions.percentages).map(([emotion, pct]) => (
            <div key={emotion}>
              {emotion}: {pct.toFixed(1)}%
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

#### Vue组件
```vue
<template>
  <div>
    <input type="file" @change="handleVideoUpload" accept="video/*">
    
    <div v-if="result">
      <h3>情感分析结果</h3>
      <p>最终得分: {{ result.final_score.toFixed(2) }}/100</p>
      <p>主导情感: {{ result.dominant_emotion }}</p>
      <p>解释: {{ result.interpretation }}</p>
      
      <div v-for="(pct, emotion) in result.emotions.percentages" :key="emotion">
        {{ emotion }}: {{ pct.toFixed(1) }}%
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      result: null
    }
  },
  methods: {
    async handleVideoUpload(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('video', file);
      
      const response = await fetch('/predict_file', {
        method: 'POST',
        body: formData
      });
      
      this.result = await response.json();
    }
  }
}
</script>
```

### 后端集成示例

#### Express.js中间件
```javascript
const multer = require('multer');
const axios = require('axios');

const upload = multer({ dest: 'uploads/' });

app.post('/analyze-emotion', upload.single('video'), async (req, res) => {
  try {
    const formData = new FormData();
    formData.append('video', fs.createReadStream(req.file.path));
    
    const response = await axios.post('http://localhost:5000/predict_file', formData);
    
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

#### Django视图
```python
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def analyze_emotion(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        
        files = {'video': video_file}
        response = requests.post('http://localhost:5000/predict_file', files=files)
        
        return JsonResponse(response.json())
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
```

## 📈 性能优化建议

### 1. 批量处理
```python
# 处理多个视频时，可以批量加载模型
api = EmotionRecognitionAPI()
results = []
for video_path in video_list:
    result = api.predict_emotions(video_path, is_base64=False)
    results.append(result)
```

### 2. 异步处理
```python
import asyncio
import aiofiles

async def analyze_video_async(video_path):
    # 异步视频处理
    api = EmotionRecognitionAPI()
    return api.predict_emotions(video_path, is_base64=False)
```

### 3. 缓存机制
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_predict(video_hash):
    api = EmotionRecognitionAPI()
    return api.predict_emotions(video_path, is_base64=False)
```

## 🚨 注意事项

### 1. 视频格式支持
- 支持格式: MP4, AVI, MOV, MKV等常见格式
- 建议分辨率: 不低于128×128
- 建议时长: 3-30秒（用于提取8帧）

### 2. 错误处理
```python
try:
    result = api.predict_emotions(video_path)
except FileNotFoundError:
    print("视频文件不存在")
except ValueError as e:
    print(f"视频处理错误: {e}")
except RuntimeError as e:
    print(f"模型预测错误: {e}")
```

### 3. 资源管理
- API实例可重复使用，避免频繁初始化
- 大文件处理时注意内存清理
- 临时文件会自动清理

## 📞 技术支持

### 验证脚本
运行以下脚本验证安装和配置：
```bash
python test_emotion_api.py      # 完整验证
python demo_api_usage.py       # 使用演示
```

### 常见问题
1. **模型加载失败**: 检查 `best_fast_daisee_model.pth` 文件是否存在
2. **CUDA错误**: 确保PyTorch版本与CUDA版本匹配
3. **视频解码错误**: 安装 `opencv-python` 并确保视频文件完整
4. **内存不足**: 减少批次大小或使用CPU模式

---

🎉 **集成完成！现在您可以获得:**
- ✅ 四个情感标签的详细分析
- ✅ 各情感的精确占比
- ✅ 0-100分的综合评分
- ✅ 智能化的状态解释
- ✅ 实时性能保证 