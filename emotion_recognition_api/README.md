# 情绪识别API - 前端对接包

## 🚀 快速开始

### 1. 环境准备
```bash
python --version  # 确保Python 3.7+
```

### 2. 启动服务
```bash
python start_api.py
```

### 3. 测试服务
```bash
python test_api.py
```

## 📋 文件说明

| 文件 | 用途 |
|------|------|
| `emotion_api.py` | **主要API服务器** |
| `start_api.py` | **启动脚本** (推荐使用) |
| `requirements.txt` | Python依赖包 |
| `test_api.py` | API测试脚本 |
| `API接口文档.md` | **详细接口文档** |
| `前端对接打包清单.md` | **前端集成指南** |

## 🌐 API接口

- **服务地址**: `http://localhost:5000`
- **核心接口**: `POST /api/emotions/analyze` - 视频情绪分析
- **健康检查**: `GET /api/health`
- **测试接口**: `POST /api/emotions/test`

## 📱 前端调用示例

```javascript
// 上传视频分析情绪
const formData = new FormData();
formData.append('video', videoFile);

fetch('http://localhost:5000/api/emotions/analyze', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(result => {
    if (result.success) {
        console.log('主导情绪:', result.data.dominant_emotion);
        console.log('参与度:', result.data.overall_engagement);
        console.log('处理时间:', result.data.processing_time);
    }
});
```

## 📊 返回数据格式

```json
{
  "success": true,
  "data": {
    "emotions": [
      {"emotion": "无聊", "score": 1.25, "percentage": 41.7},
      {"emotion": "参与度", "score": 2.35, "percentage": 78.3},
      {"emotion": "困惑", "score": 0.85, "percentage": 28.3},
      {"emotion": "挫折感", "score": 1.15, "percentage": 38.3}
    ],
    "dominant_emotion": "参与度",
    "processing_time": "137.5ms"
  }
}
```

---

**详细使用说明请查看**：`前端对接打包清单.md` 