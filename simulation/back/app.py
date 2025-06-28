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

# 星火大模型API配置 - 优先使用环境变量
SPARK_API_URL = os.getenv("SPARK_API_URL", "https://spark-api-open.xf-yun.com/v1/chat/completions")
SPARK_API_KEY = os.getenv("SPARK_API_KEY", "")
SPARK_APP_ID = os.getenv("SPARK_APP_ID", "")
SPARK_API_SECRET = os.getenv("SPARK_API_SECRET", "")

# 检查API密钥是否配置
if not SPARK_API_KEY:
    print("⚠️  警告：未正确配置星火大模型API密钥！请设置环境变量 SPARK_API_KEY")

class ChatService:
    def __init__(self):
        self.conversation_history = []
        self.resume_data = None
        
    def set_resume(self, resume_data):
        """设置简历数据"""
        self.resume_data = resume_data
    
    def add_message(self, role, content):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_interview_prompt(self, resume_data):
        """生成面试官的系统提示词"""
        prompt = f"""你是一位专业的面试官，正在为以下求职者进行面试。请根据他们的简历信息，进行专业、友好的面试对话。

===== 求职者简历信息 =====
姓名：{resume_data.get('name', '未提供')}
年龄：{resume_data.get('age', '未提供')}
期望职位：{resume_data.get('targetPosition', '未提供')}
期望薪资：{resume_data.get('expectedSalary', '未提供')}
学历：{resume_data.get('education', '未提供')}
专业：{resume_data.get('major', '未提供')}
毕业院校：{resume_data.get('university', '未提供')}
毕业年份：{resume_data.get('graduationYear', '未提供')}
工作经验：{resume_data.get('workExperience', '未提供')}
工作描述：{resume_data.get('workDescription', '未提供')}
技术技能：{resume_data.get('technicalSkills', '未提供')}
其他技能：{resume_data.get('otherSkills', '未提供')}
项目经验：{resume_data.get('projectExperience', '未提供')}
自我评价：{resume_data.get('selfEvaluation', '未提供')}
===========================

面试要求：
1. 作为专业面试官，你需要：
   - 根据求职者的简历背景，问出有针对性的问题
   - 保持专业、友好的语调，营造轻松的面试氛围
   - 循序渐进地了解求职者的能力、经验和职业规划
   - 适时给出正面反馈，鼓励求职者充分展示自己

2. 面试重点关注：
   - 与目标职位相关的技能和经验
   - 求职者的学习能力和适应能力
   - 项目经验和技术深度
   - 团队协作和沟通能力
   - 职业规划和发展目标

3. 面试风格：
   - 语言简洁清楚，避免过于复杂的表述
   - 一次只问一个核心问题，给求职者充分表达机会
   - 根据求职者的回答，进行适当的追问和深入
   - 保持积极正面的面试体验

请现在开始面试，先给出一个合适的开场白和第一个问题。记住你是面试官，需要引导整个面试过程。"""
        
        return prompt
    
    def get_spark_response(self, user_message, model="generalv3.5"):
        """调用星火大模型API获取回复"""
        try:
            # 添加用户消息到历史
            self.add_message("user", user_message)
            
            # 准备请求数据 - 星火大模型需要特定的认证方式
            headers = {
                "Authorization": f"Bearer {SPARK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 构建消息历史（只发送最近10条消息以控制token使用）
            messages = []
            
            # 如果是面试场景且有简历信息，添加系统提示词
            if self.resume_data and len(self.conversation_history) <= 2:
                system_prompt = self.generate_interview_prompt(self.resume_data)
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加对话历史
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
            
            # 调用星火大模型API
            response = requests.post(SPARK_API_URL, headers=headers, json=data, timeout=30)
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
    
    def generate_first_question(self, resume_data):
        """根据简历生成第一个面试问题"""
        try:
            # 设置简历数据
            self.set_resume(resume_data)
            
            # 生成系统提示词并获取第一个问题
            system_prompt = self.generate_interview_prompt(resume_data)
            
            # 直接调用API获取第一个问题
            headers = {
                "Authorization": f"Bearer {SPARK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": "请开始面试，给出开场白和第一个问题。"
                }
            ]
            
            data = {
                "model": "generalv3.5",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024,
                "stream": False
            }
            
            response = requests.post(SPARK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            first_question = result["choices"][0]["message"]["content"]
            
            # 添加到对话历史
            self.add_message("assistant", first_question)
            
            return {
                "success": True,
                "question": first_question
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"生成面试问题失败: {str(e)}",
                "question": f"您好 {resume_data.get('name', '求职者')}！很高兴见到您。请先简单介绍一下您自己，包括您的教育背景和工作经验。"
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
        model = data.get('model', 'generalv3.5')
        
        # 调用星火大模型API
        result = chat_service.get_spark_response(user_message, model)
        
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
        chat_service.resume_data = None
        return jsonify({
            "success": True,
            "message": "对话历史已清空"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"清空历史记录失败: {str(e)}"
        }), 500

@app.route('/api/interview/start', methods=['POST'])
def start_interview():
    """开始面试：提交简历并获取第一个问题"""
    try:
        data = request.get_json()
        
        if not data or 'resume' not in data:
            return jsonify({
                "success": False,
                "error": "请求格式错误，需要包含'resume'字段"
            }), 400
        
        resume_data = data['resume']
        
        # 验证必要字段
        required_fields = ['name', 'targetPosition', 'education']
        for field in required_fields:
            if not resume_data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"简历必填字段缺失: {field}"
                }), 400
        
        print(f"📋 收到简历提交：{resume_data.get('name')} - {resume_data.get('targetPosition')}")
        
        # 清空之前的对话历史，开始新的面试
        chat_service.conversation_history.clear()
        
        # 生成第一个面试问题
        result = chat_service.generate_first_question(resume_data)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "firstQuestion": result["question"],
                "message": "简历提交成功，面试已开始",
                "timestamp": datetime.now().isoformat()
            })
        else:
            # 即使API调用失败，也返回默认问题
            return jsonify({
                "success": True,
                "firstQuestion": result["question"],
                "message": "简历提交成功，面试已开始（使用默认问题）",
                "error": result.get("error"),
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        print(f"❌ 面试启动失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}",
            "firstQuestion": "您好！很高兴见到您。请先简单介绍一下您自己。"
        }), 500

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """获取可用的模型列表"""
    models = [
        {
            "id": "generalv3.5",
            "name": "星火大模型 3.5",
            "description": "星火大模型通用版本，适合面试对话"
        },
        {
            "id": "generalv2",
            "name": "星火大模型 2.0",
            "description": "星火大模型标准版本"
        }
    ]
    
    return jsonify({
        "success": True,
        "models": models
    })

if __name__ == '__main__':
    print("🚀 启动DeepSeek聊天API服务...")
    print(f"📡 API URL: {SPARK_API_URL}")
    print(f"🔑 API Key配置: {'✓ 已配置' if SPARK_API_KEY and SPARK_API_KEY != 'your_deepseek_api_key_here' else '✗ 未配置'}")
    print("🌐 服务器地址: http://localhost:5000")
    print("📋 健康检查: http://localhost:5000/api/health")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 