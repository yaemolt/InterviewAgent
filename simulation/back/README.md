# 智能面试系统后端服务

基于星火大模型的智能面试系统后端服务，提供简历处理和面试对话功能。

## 🚀 功能特性

- 📝 简历信息处理和存储
- 🤖 基于星火大模型的智能面试对话  
- 💡 个性化面试问题生成
- 📊 面试对话历史管理
- ✅ 跨域请求支持 (CORS)
- ✅ 错误处理和重试机制
- ✅ RESTful API 设计

## 🔧 环境配置

### 星火大模型API配置

1. 访问 [讯飞开放平台](https://console.xfyun.cn/) 注册账号
2. 创建应用并获取以下信息：
   - API Key
   - App ID  
   - API Secret

3. 设置环境变量（推荐创建 `.env` 文件）：

```bash
# 星火大模型API配置
SPARK_API_KEY=your_spark_api_key_here
SPARK_APP_ID=your_app_id_here  
SPARK_API_SECRET=your_api_secret_here
SPARK_API_URL=https://spark-api-open.xf-yun.com/v1/chat/completions
```

## 📚 API接口

### 1. 简历提交接口
```
POST /api/interview/start
Content-Type: application/json

{
    "resume": {
        "name": "张三",
        "targetPosition": "前端开发工程师",
        "education": "本科",
        "major": "计算机科学与技术",
        "workExperience": "1-3年",
        "technicalSkills": "JavaScript, Vue.js, React",
        // ...其他简历字段
    }
}
```

响应：
```json
{
    "success": true,
    "firstQuestion": "您好张三！很高兴见到您...",
    "message": "简历提交成功，面试已开始",
    "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 2. 面试对话接口
```
POST /api/chat
Content-Type: application/json

{
    "message": "我毕业于某某大学计算机专业...",
    "model": "generalv3.5"  // 可选，默认为 generalv3.5
}
```

响应：
```json
{
    "success": true,
    "response": "很好！您的教育背景很扎实...",
    "model": "generalv3.5",
    "usage": {
        "prompt_tokens": 150,
        "completion_tokens": 80,
        "total_tokens": 230
    },
    "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 3. 获取对话历史
```
GET /api/chat/history?limit=50
```

### 4. 清空对话历史
```
POST /api/chat/clear
```

### 5. 获取可用模型
```
GET /api/models
```

响应：
```json
{
    "success": true,
    "models": [
        {
            "id": "generalv3.5",
            "name": "星火大模型 3.5",
            "description": "星火大模型通用版本，适合面试对话"
        }
    ]
}
```

### 6. 健康检查
```
GET /api/health
```

## 🎯 面试流程

1. **简历提交**: 用户填写简历表格并提交到 `/api/interview/start`
2. **AI分析**: 系统解析简历信息，生成个性化面试官提示词
3. **问题生成**: 基于简历背景生成第一个面试问题
4. **对话交互**: 用户通过 `/api/chat` 与面试官进行对话
5. **智能追问**: AI根据回答进行有针对性的追问和深入

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 创建 .env 文件，填入你的星火大模型API信息
cat > .env << EOF
SPARK_API_KEY=your_spark_api_key_here
SPARK_APP_ID=your_app_id_here  
SPARK_API_SECRET=your_api_secret_here
SPARK_API_URL=https://spark-api-open.xf-yun.com/v1/chat/completions
EOF
```

### 3. 运行服务
```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## 前端集成示例

### JavaScript/jQuery 调用示例：
```javascript
// 发送消息
async function sendMessage(message) {
    try {
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                model: 'generalv3.5'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('AI回复:', data.response);
            return data.response;
        } else {
            console.error('错误:', data.error);
            return null;
        }
    } catch (error) {
        console.error('请求失败:', error);
        return null;
    }
}

// 使用示例
sendMessage('你好，请介绍一下自己').then(response => {
    if (response) {
        document.getElementById('chat-output').innerHTML += 
            `<div class="ai-message">${response}</div>`;
    }
});
```

### React 调用示例：
```jsx
import React, { useState } from 'react';

function ChatComponent() {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');
    
    const sendMessage = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: 'generalv3.5'
                })
            });
            
            const data = await res.json();
            
            if (data.success) {
                setResponse(data.response);
            }
        } catch (error) {
            console.error('发送消息失败:', error);
        }
    };
    
    return (
        <div>
            <input 
                value={message} 
                onChange={(e) => setMessage(e.target.value)}
                placeholder="输入消息..."
            />
            <button onClick={sendMessage}>发送</button>
            <div>AI回复: {response}</div>
        </div>
    );
}
```

## 📝 环境变量说明

- `SPARK_API_KEY`: 星火大模型 API 密钥（必填）
- `SPARK_APP_ID`: 星火大模型应用 ID（必填）
- `SPARK_API_SECRET`: 星火大模型 API 密钥（必填）
- `SPARK_API_URL`: 星火大模型 API 地址
- `FLASK_ENV`: Flask 环境（development/production）
- `FLASK_DEBUG`: 是否开启调试模式

## ⚠️ 注意事项

1. 请确保您有有效的星火大模型 API 密钥
2. 生产环境请关闭调试模式
3. 建议使用 HTTPS 以保护 API 密钥安全
4. 简历信息将存储在内存中，重启服务会丢失
5. 可以根据需要调整对话历史的保存数量以控制内存使用

## 🎯 提示词设计

系统会根据简历信息自动生成个性化的面试官提示词，包含：

- 求职者的基本信息和背景
- 针对性的面试策略和重点
- 专业友好的面试风格指导
- 循序渐进的问题设计原则

## 错误码说明

- `400`: 请求参数错误
- `500`: 服务器内部错误或 API 调用失败

## 许可证

MIT License 