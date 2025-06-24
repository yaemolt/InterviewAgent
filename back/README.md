# DeepSeek 对话 API

这是一个与 DeepSeek API 对接的后端服务，提供对话功能的 REST API 接口。

## 功能特性

- ✅ 与 DeepSeek API 完整对接
- ✅ 支持对话历史管理
- ✅ 跨域请求支持 (CORS)
- ✅ 错误处理和重试机制
- ✅ 多模型支持
- ✅ RESTful API 设计

## API 接口

### 1. 对话接口
```
POST /api/chat
Content-Type: application/json

{
    "message": "你好，请介绍一下自己",
    "model": "deepseek-chat"  // 可选，默认为 deepseek-chat
}
```

响应：
```json
{
    "success": true,
    "response": "你好！我是DeepSeek，一个AI助手...",
    "model": "deepseek-chat",
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    },
    "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 2. 获取对话历史
```
GET /api/chat/history?limit=50
```

### 3. 清空对话历史
```
POST /api/chat/clear
```

### 4. 获取可用模型
```
GET /api/models
```

### 5. 健康检查
```
GET /api/health
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API 密钥
# DEEPSEEK_API_KEY=your_actual_api_key
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
                model: 'deepseek-chat'
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
                    model: 'deepseek-chat'
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

## 环境变量说明

- `DEEPSEEK_API_KEY`: DeepSeek API 密钥（必填）
- `FLASK_ENV`: Flask 环境（development/production）
- `FLASK_DEBUG`: 是否开启调试模式
- `HOST`: 服务器绑定地址
- `PORT`: 服务器端口

## 注意事项

1. 请确保您有有效的 DeepSeek API 密钥
2. 生产环境请关闭调试模式
3. 建议使用 HTTPS 以保护 API 密钥安全
4. 可以根据需要调整对话历史的保存数量以控制内存使用

## 错误码说明

- `400`: 请求参数错误
- `500`: 服务器内部错误或 API 调用失败

## 许可证

MIT License 