from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# DeepSeek API配置 - 优先使用环境变量
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-96ad5c5974ef42b79f7502e1380d0fa8")

# 检查API密钥是否配置
if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
    print("⚠️  警告：未正确配置DeepSeek API密钥！")

class ChatService:
    def __init__(self):
        self.conversation_history = []
    
    def add_message(self, role, content):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_deepseek_response(self, user_message, model="deepseek-chat"):
        """调用DeepSeek API获取回复"""
        try:
            # 添加用户消息到历史
            self.add_message("user", user_message)
            
            # 准备请求数据
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 构建消息历史（只发送最近10条消息以控制token使用）
            messages = []
            recent_history = self.conversation_history[-10:]
            for msg in recent_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": False
            }
            
            # 调用DeepSeek API
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # 提取AI回复
            ai_message = result["choices"][0]["message"]["content"]
            
            # 添加AI回复到历史
            self.add_message("assistant", ai_message)
            
            return {
                "success": True,
                "message": ai_message,
                "usage": result.get("usage", {}),
                "model": model
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API请求失败: {str(e)}",
                "message": "抱歉，我现在无法回答您的问题，请稍后再试。"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"处理失败: {str(e)}",
                "message": "抱歉，处理您的请求时出现了错误。"
            }

# 创建聊天服务实例
chat_service = ChatService()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "DeepSeek Chat API",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """主要对话接口"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "请求格式错误，需要包含'message'字段"
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                "success": False,
                "error": "消息内容不能为空"
            }), 400
        
        # 获取模型参数（可选）
        model = data.get('model', 'deepseek-chat')
        
        # 调用DeepSeek API
        result = chat_service.get_deepseek_response(user_message, model)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "response": result["message"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"],
                "response": result["message"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}",
            "response": "抱歉，服务器出现了问题，请稍后再试。"
        }), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """获取对话历史"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = chat_service.conversation_history[-limit:]
        
        return jsonify({
            "success": True,
            "history": history,
            "total": len(chat_service.conversation_history)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取历史记录失败: {str(e)}"
        }), 500

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    """清空对话历史"""
    try:
        chat_service.conversation_history.clear()
        return jsonify({
            "success": True,
            "message": "对话历史已清空"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"清空历史记录失败: {str(e)}"
        }), 500

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """获取可用的模型列表"""
    models = [
        {
            "id": "deepseek-chat",
            "name": "DeepSeek Chat",
            "description": "DeepSeek 通用对话模型"
        },
        {
            "id": "deepseek-coder",
            "name": "DeepSeek Coder", 
            "description": "DeepSeek 代码生成模型"
        }
    ]
    
    return jsonify({
        "success": True,
        "models": models
    })

if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    print("🚀 DeepSeek Chat API 服务启动中...")
    print(f"📡 服务地址: http://localhost:{port}")
    print(f"🔑 API密钥状态: {'✅ 已配置' if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 10 else '❌ 未配置'}")
    print(f"🌐 允许跨域: ✅")
    print(f"🔧 调试模式: {'✅' if debug else '❌'}")
    print("✅ 服务准备就绪，可以开始对话了！")
    
    app.run(debug=debug, host=host, port=port) 