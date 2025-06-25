# 前端集成示例

## 🎯 API输出格式

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

## 🚀 React 组件示例

### 基础组件
```jsx
import React, { useState } from 'react';

function EmotionAnalyzer() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeVideo = async (videoFile) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('video', videoFile);
      
      const response = await fetch('http://localhost:5000/predict_file', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('分析失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="emotion-analyzer">
      <input 
        type="file" 
        accept="video/*"
        onChange={(e) => analyzeVideo(e.target.files[0])}
        disabled={loading}
      />
      
      {loading && <div>分析中...</div>}
      
      {result && (
        <div className="result">
          <h3>情感分析结果</h3>
          <div className="score">
            最终得分: {result.final_score.toFixed(2)}/100
          </div>
          <div className="dominant">
            主导情感: {result.dominant_emotion}
          </div>
          <div className="interpretation">
            {result.interpretation}
          </div>
          
          <h4>各情感占比:</h4>
          <div className="emotions">
            {Object.entries(result.emotions.percentages).map(([emotion, pct]) => (
              <div key={emotion} className="emotion-item">
                <span>{emotion}:</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span>{pct.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default EmotionAnalyzer;
```

### 高级组件 (带动画和图表)
```jsx
import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from 'recharts';

function AdvancedEmotionAnalyzer() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const emotionColors = {
    'Boredom': '#ff6b6b',
    'Engagement': '#4ecdc4',
    'Confusion': '#45b7d1',
    'Frustration': '#f9ca24'
  };

  const emotionEmojis = {
    'Boredom': '😴',
    'Engagement': '😊',
    'Confusion': '😕',
    'Frustration': '😤'
  };

  const analyzeVideo = async (videoFile) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('video', videoFile);
      
      const response = await fetch('http://localhost:5000/predict_file', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('分析失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return '#27ae60';
    if (score >= 60) return '#2ecc71';
    if (score >= 40) return '#f39c12';
    if (score >= 25) return '#e67e22';
    return '#e74c3c';
  };

  const chartData = result ? Object.entries(result.emotions.percentages).map(([emotion, pct]) => ({
    name: emotion,
    value: pct,
    color: emotionColors[emotion]
  })) : [];

  return (
    <div className="advanced-emotion-analyzer">
      <div className="upload-section">
        <input 
          type="file" 
          accept="video/*"
          onChange={(e) => analyzeVideo(e.target.files[0])}
          disabled={loading}
          className="file-input"
        />
        {loading && <div className="loading">🔄 分析中...</div>}
      </div>

      {result && (
        <div className="results animate-fade-in">
          {/* 分数显示 */}
          <div className="score-display">
            <div 
              className="score-circle"
              style={{ 
                background: `conic-gradient(${getScoreColor(result.final_score)} ${result.final_score * 3.6}deg, #e0e0e0 0deg)`
              }}
            >
              <div className="score-inner">
                <span className="score-value">{result.final_score.toFixed(0)}</span>
                <span className="score-max">/100</span>
              </div>
            </div>
            <div className="score-info">
              <h3>情感评分</h3>
              <p className="interpretation">{result.interpretation}</p>
              <p className="dominant">
                主导情感: {emotionEmojis[result.dominant_emotion]} {result.dominant_emotion}
              </p>
            </div>
          </div>

          {/* 饼图 */}
          <div className="chart-section">
            <h4>情感分布</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 柱状图 */}
          <div className="chart-section">
            <h4>各情感强度</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={chartData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Bar dataKey="value" fill="#8884d8">
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 详细信息 */}
          <div className="details-section">
            <h4>详细数据</h4>
            <div className="emotion-grid">
              {Object.entries(result.emotions.percentages).map(([emotion, pct]) => (
                <div key={emotion} className="emotion-card">
                  <div className="emotion-icon">{emotionEmojis[emotion]}</div>
                  <div className="emotion-name">{emotion}</div>
                  <div className="emotion-value">{pct.toFixed(1)}%</div>
                  <div className="emotion-raw">
                    原始分数: {result.emotions.raw_scores[emotion].toFixed(3)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdvancedEmotionAnalyzer;
```

## 🎨 CSS 样式

```css
.emotion-analyzer {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.file-input {
  margin-bottom: 20px;
  padding: 10px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  width: 100%;
}

.result {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.score {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
}

.emotion-item {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.progress-bar {
  flex: 1;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  margin: 0 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(to right, #4ecdc4, #44a08d);
  transition: width 0.3s ease;
}

/* 高级组件样式 */
.advanced-emotion-analyzer {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.score-display {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 30px 0;
  gap: 30px;
}

.score-circle {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.score-inner {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  color: #2c3e50;
}

.score-max {
  font-size: 16px;
  color: #7f8c8d;
}

.chart-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.emotion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.emotion-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.emotion-card:hover {
  transform: translateY(-2px);
}

.emotion-icon {
  font-size: 30px;
  margin-bottom: 10px;
}

.emotion-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.emotion-value {
  font-size: 20px;
  color: #3498db;
  font-weight: bold;
}

.emotion-raw {
  font-size: 12px;
  color: #7f8c8d;
  margin-top: 5px;
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading {
  text-align: center;
  font-size: 18px;
  color: #3498db;
  margin: 20px 0;
}
```

## 🎭 Vue.js 组件示例

```vue
<template>
  <div class="emotion-analyzer">
    <input 
      type="file" 
      @change="handleVideoUpload" 
      accept="video/*"
      :disabled="loading"
    >
    
    <div v-if="loading">分析中...</div>
    
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
      result: null,
      loading: false
    }
  },
  methods: {
    async handleVideoUpload(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('video', file);
      
      this.loading = true;
      const response = await fetch('http://localhost:5000/predict_file', {
        method: 'POST',
        body: formData
      });
      
      this.result = await response.json();
      this.loading = false;
    }
  }
}
</script>
```

## 📱 JavaScript 原生实现

```javascript
// 创建API客户端
class EmotionAPI {
  constructor(baseUrl = 'http://localhost:5000') {
    this.baseUrl = baseUrl;
  }

  async analyzeVideo(videoFile) {
    const formData = new FormData();
    formData.append('video', videoFile);
    
    const response = await fetch(`${this.baseUrl}/predict_file`, {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  }
}

// 使用示例
const api = new EmotionAPI();

document.getElementById('video-input').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (file) {
    const result = await api.analyzeVideo(file);
    displayResult(result);
  }
});

function displayResult(result) {
  const html = `
    <h3>分析结果</h3>
    <p>得分: ${result.final_score.toFixed(2)}/100</p>
    <p>主导情感: ${result.dominant_emotion}</p>
    <p>解释: ${result.interpretation}</p>
    <h4>各情感占比:</h4>
    ${Object.entries(result.emotions.percentages).map(([emotion, pct]) => 
      `<p>${emotion}: ${pct.toFixed(1)}%</p>`
    ).join('')}
  `;
  
  document.getElementById('result').innerHTML = html;
}
```

## 🔗 API接口

### 1. 文件上传
- **URL**: `POST /predict_file`
- **参数**: `video` (文件)
- **返回**: JSON格式结果

### 2. Base64上传
- **URL**: `POST /predict`
- **参数**: 
```json
{
  "video": "base64编码的视频",
  "is_base64": true
}
```

### 3. 健康检查
- **URL**: `GET /health`
- **返回**: 服务状态 