from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import websocket
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from time import mktime
import _thread as thread
import io
import uuid
# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 星火大模型HTTP API配置
SPARK_API_URL = os.getenv("SPARK_API_URL", "https://spark-api-open.xf-yun.com/v1/chat/completions")
SPARK_API_PASSWORD = os.getenv("SPARK_API_PASSWORD", "")
SPARK_MODEL = os.getenv("SPARK_MODEL", "SPARK MAX")  # 默认使用SPARK MAX模型

# 语音合成API配置
TTS_APP_ID = os.getenv("TTS_APP_ID", "")
TTS_API_KEY = os.getenv("TTS_API_KEY", "")
TTS_API_SECRET = os.getenv("TTS_API_SECRET", "")
TTS_REQUEST_URL = os.getenv("TTS_REQUEST_URL", "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6")

# 语音识别API配置
ASR_APP_ID = os.getenv("ASR_APP_ID", "")
ASR_API_KEY = os.getenv("ASR_API_KEY", "")
ASR_API_SECRET = os.getenv("ASR_API_SECRET", "")
ASR_REQUEST_URL = os.getenv("ASR_REQUEST_URL", "ws://iat.xf-yun.com/v1")

# 检查API密钥是否配置
if not SPARK_API_PASSWORD:
    print("⚠️  警告：未正确配置星火大模型API密钥！")
    print("    请设置环境变量 SPARK_API_PASSWORD") 
    print("    获取地址：https://console.xfyun.cn/services/bmx1")
    SPARK_API_AVAILABLE = False
else:
    SPARK_API_AVAILABLE = True
    print("✅ 星火大模型HTTP API配置成功")

# 检查TTS API密钥配置
if not TTS_APP_ID or not TTS_API_KEY or not TTS_API_SECRET:
    print("⚠️  警告：未正确配置语音合成API密钥！")
    print("    请设置环境变量：TTS_APP_ID, TTS_API_KEY, TTS_API_SECRET")
    print("    获取地址：https://console.xfyun.cn/app/myapp")
    TTS_API_AVAILABLE = False
else:
    TTS_API_AVAILABLE = True
    print("✅ 语音合成API配置成功")

# 检查ASR API密钥配置
if not ASR_APP_ID or not ASR_API_KEY or not ASR_API_SECRET:
    print("⚠️  警告：未正确配置语音识别API密钥！")
    print("    请设置环境变量：ASR_APP_ID, ASR_API_KEY, ASR_API_SECRET")
    print("    获取地址：https://console.xfyun.cn/app/myapp")
    ASR_API_AVAILABLE = False
else:
    ASR_API_AVAILABLE = True
    print("✅ 语音识别API配置成功")

class TTSService:
    """语音合成服务类"""
    
    def __init__(self):
        self.app_id = TTS_APP_ID
        self.api_key = TTS_API_KEY
        self.api_secret = TTS_API_SECRET
        self.request_url = TTS_REQUEST_URL
        self.audio_data = b''
        self.is_completed = False
        self.error_message = None
    
    def _parse_url(self, request_url):
        """解析URL"""
        stidx = request_url.index("://")
        host = request_url[stidx + 3:]
        schema = request_url[:stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise Exception("invalid request url:" + request_url)
        path = host[edidx:]
        host = host[:edidx]
        return {
            'host': host,
            'path': path,
            'schema': schema
        }
    
    def _assemble_ws_auth_url(self, request_url, method="GET", api_key="", api_secret=""):
        """构建WebSocket认证URL"""
        url_info = self._parse_url(request_url)
        host = url_info['host']
        path = url_info['path']
        
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        values = {
            "host": host,
            "date": date,
            "authorization": authorization
        }
        
        return request_url + "?" + urlencode(values)
    
    def _on_message(self, ws, message):
        """WebSocket消息处理"""
        try:
            message = json.loads(message)
            code = message["header"]["code"]
            sid = message["header"]["sid"]
            
            if "payload" in message:
                audio = message["payload"]["audio"]['audio']
                audio = base64.b64decode(audio)
                status = message["payload"]['audio']["status"]
                
                if code != 0:
                    err_msg = message.get("message", "未知错误")
                    self.error_message = f"TTS错误：{err_msg} (code: {code})"
                    print(f"❌ TTS错误: {self.error_message}")
                    ws.close()
                else:
                    # 累积音频数据
                    self.audio_data += audio
                    
                    if status == 2:  # 音频合成完成
                        print("✅ 语音合成完成")
                        self.is_completed = True
                        ws.close()
        except Exception as e:
            self.error_message = f"消息解析失败: {str(e)}"
            print(f"❌ TTS消息解析失败: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket错误处理"""
        self.error_message = f"WebSocket错误: {str(error)}"
        print(f"❌ TTS WebSocket错误: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭处理"""
        print("🔌 TTS WebSocket连接已关闭")
    
    def _on_open(self, ws, text):
        """WebSocket连接打开处理"""
        def run(*args):
            # 构建请求参数
            common_args = {"app_id": self.app_id, "status": 2}
            business_args = {
                "tts": {
                    "vcn": "x4_lingxiaoxuan_oral",  # 发音人参数
                    "volume": 70,    # 音量
                    "speed": 55,     # 语速
                    "pitch": 50,     # 音调
                    "bgs": 0,        # 背景音
                    "audio": {
                        "encoding": "lame",  # mp3格式
                        "sample_rate": 24000,
                        "channels": 1,
                        "bit_depth": 16,
                        "frame_size": 0
                    }
                }
            }
            data = {
                "text": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "status": 2,
                    "seq": 0,
                    "text": str(base64.b64encode(text.encode('utf-8')), "UTF8")
                }
            }
            
            request_data = {
                "header": common_args,
                "parameter": business_args,
                "payload": data,
            }
            
            ws.send(json.dumps(request_data))
            print("🔊 开始语音合成...")
        
        thread.start_new_thread(run, (text,))
    
    def text_to_speech(self, text, timeout=30):
        """
        文本转语音
        Args:
            text: 要转换的文本
            timeout: 超时时间（秒）
        Returns:
            bytes: 音频数据，如果失败返回None
        """
        if not TTS_API_AVAILABLE:
            print("❌ TTS API未配置，无法进行语音合成")
            return None
        
        try:
            # 重置状态
            self.audio_data = b''
            self.is_completed = False
            self.error_message = None
            
            # 构建WebSocket URL
            ws_url = self._assemble_ws_auth_url(
                self.request_url, "GET", self.api_key, self.api_secret
            )
            
            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 设置on_open回调并启动
            ws.on_open = lambda ws: self._on_open(ws, text)
            
            # 运行WebSocket（带超时）
            start_time = time.time()
            
            def run_with_timeout():
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            thread.start_new_thread(run_with_timeout, ())
            
            # 等待完成或超时
            while not self.is_completed and not self.error_message:
                if time.time() - start_time > timeout:
                    self.error_message = "语音合成超时"
                    break
                time.sleep(0.1)
            
            if self.error_message:
                print(f"❌ 语音合成失败: {self.error_message}")
                return None
            
            if not self.audio_data:
                print("❌ 未获取到音频数据")
                return None
            
            print(f"✅ 语音合成成功，音频大小: {len(self.audio_data)} bytes")
            return self.audio_data
            
        except Exception as e:
            print(f"❌ 语音合成异常: {str(e)}")
            return None

class ASRService:
    """语音识别服务类"""
    
    # 音频状态标识
    STATUS_FIRST_FRAME = 0  # 第一帧的标识
    STATUS_CONTINUE_FRAME = 1  # 中间帧标识
    STATUS_LAST_FRAME = 2  # 最后一帧的标识
    
    def __init__(self):
        self.app_id = ASR_APP_ID
        self.api_key = ASR_API_KEY
        self.api_secret = ASR_API_SECRET
        self.request_url = ASR_REQUEST_URL
        self.recognition_result = ""
        self.is_completed = False
        self.error_message = None
        
        # 语音识别参数
        self.iat_params = {
            "domain": "slm",  # 通用文本识别领域
            "language": "zh_cn",  # 中文
            "accent": "mandarin",  # 普通话
            "dwa": "wpgs",  # 动态修正
            "result": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "plain"
            }
        }
    
    def _create_url(self):
        """生成WebSocket连接URL"""
        try:
            # 生成RFC1123格式的时间戳
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))
            
            # 拼接字符串
            signature_origin = "host: " + "iat.xf-yun.com" + "\n"
            signature_origin += "date: " + date + "\n"
            signature_origin += "GET " + "/v1 " + "HTTP/1.1"
            
            # 进行hmac-sha256进行加密
            signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                   digestmod=hashlib.sha256).digest()
            signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
            
            authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                self.api_key, "hmac-sha256", "host date request-line", signature_sha)
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
            
            # 将请求的鉴权参数组合为字典
            v = {
                "authorization": authorization,
                "date": date,
                "host": "iat.xf-yun.com"
            }
            
            # 拼接鉴权参数，生成url
            url = self.request_url + '?' + urlencode(v)
            return url
        except Exception as e:
            print(f"❌ ASR URL生成失败: {str(e)}")
            return None
    
    def _on_message(self, ws, message):
        """WebSocket消息处理"""
        try:
            message = json.loads(message)
            code = message["header"]["code"]
            status = message["header"]["status"]
            
            if code != 0:
                self.error_message = f"语音识别错误: code {code}"
                print(f"❌ {self.error_message}")
                ws.close()
            else:
                payload = message.get("payload")
                if payload:
                    text = payload["result"]["text"]
                    text = json.loads(str(base64.b64decode(text), "utf8"))
                    text_ws = text['ws']
                    result = ''
                    for i in text_ws:
                        for j in i["cw"]:
                            w = j["w"]
                            result += w
                    
                    # 累积识别结果
                    self.recognition_result += result
                    print(f"🎤 识别片段: {result}")
                
                if status == 2:  # 识别完成
                    print(f"✅ 语音识别完成: {self.recognition_result}")
                    self.is_completed = True
                    ws.close()
        except Exception as e:
            self.error_message = f"消息解析失败: {str(e)}"
            print(f"❌ ASR消息解析失败: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket错误处理"""
        self.error_message = f"WebSocket错误: {str(error)}"
        print(f"❌ ASR WebSocket错误: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭处理"""
        print("🔌 ASR WebSocket连接已关闭")
    
    def _on_open(self, ws, audio_data):
        """WebSocket连接打开处理"""
        def run(*args):
            try:
                frame_size = 1280  # 每一帧的音频大小
                interval = 0.04  # 发送音频间隔(单位:s)
                status = self.STATUS_FIRST_FRAME  # 音频的状态信息
                
                # 处理音频数据
                audio_bytes = io.BytesIO(audio_data)
                
                while True:
                    buf = audio_bytes.read(frame_size)
                    if not buf:
                        status = self.STATUS_LAST_FRAME
                    
                    audio = str(base64.b64encode(buf), 'utf-8')
                    
                    # 第一帧处理
                    if status == self.STATUS_FIRST_FRAME:
                        d = {
                            "header": {
                                "status": 0,
                                "app_id": self.app_id
                            },
                            "parameter": {
                                "iat": self.iat_params
                            },
                            "payload": {
                                "audio": {
                                    "audio": audio,
                                    "sample_rate": 16000,
                                    "encoding": "raw"
                                }
                            }
                        }
                        ws.send(json.dumps(d))
                        status = self.STATUS_CONTINUE_FRAME
                    
                    # 中间帧处理
                    elif status == self.STATUS_CONTINUE_FRAME:
                        d = {
                            "header": {
                                "status": 1,
                                "app_id": self.app_id
                            },
                            "parameter": {
                                "iat": self.iat_params
                            },
                            "payload": {
                                "audio": {
                                    "audio": audio,
                                    "sample_rate": 16000,
                                    "encoding": "raw"
                                }
                            }
                        }
                        ws.send(json.dumps(d))
                    
                    # 最后一帧处理
                    elif status == self.STATUS_LAST_FRAME:
                        d = {
                            "header": {
                                "status": 2,
                                "app_id": self.app_id
                            },
                            "parameter": {
                                "iat": self.iat_params
                            },
                            "payload": {
                                "audio": {
                                    "audio": audio,
                                    "sample_rate": 16000,
                                    "encoding": "raw"
                                }
                            }
                        }
                        ws.send(json.dumps(d))
                        break
                    
                    # 如果没有数据了，发送最后一帧
                    if not buf:
                        break
                    
                    # 模拟音频采样间隔
                    time.sleep(interval)
                    
            except Exception as e:
                self.error_message = f"音频发送失败: {str(e)}"
                print(f"❌ ASR音频发送失败: {e}")
        
        thread.start_new_thread(run, (audio_data,))
    
    def recognize_speech(self, audio_data, timeout=30):
        """
        语音识别
        Args:
            audio_data: 音频数据（bytes）
            timeout: 超时时间（秒）
        Returns:
            str: 识别结果文本，如果失败返回None
        """
        if not ASR_API_AVAILABLE:
            print("❌ ASR API未配置，无法进行语音识别")
            return None
        
        try:
            # 重置状态
            self.recognition_result = ""
            self.is_completed = False
            self.error_message = None
            
            # 构建WebSocket URL
            ws_url = self._create_url()
            if not ws_url:
                return None
            
            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 设置on_open回调并启动
            ws.on_open = lambda ws: self._on_open(ws, audio_data)
            
            # 运行WebSocket（带超时）
            start_time = time.time()
            
            def run_with_timeout():
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            thread.start_new_thread(run_with_timeout, ())
            
            # 等待完成或超时
            while not self.is_completed and not self.error_message:
                if time.time() - start_time > timeout:
                    self.error_message = "语音识别超时"
                    break
                time.sleep(0.1)
            
            if self.error_message:
                print(f"❌ 语音识别失败: {self.error_message}")
                return None
            
            if not self.recognition_result:
                print("❌ 未获取到识别结果")
                return None
            
            print(f"✅ 语音识别成功: {self.recognition_result}")
            return self.recognition_result.strip()
            
        except Exception as e:
            print(f"❌ 语音识别异常: {str(e)}")
            return None

class ChatService:
    def __init__(self):
        self.conversation_history = []
        self.resume_data = None
        self.tts_service = TTSService()
        self.asr_service = ASRService()
        
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
            
            # 构建消息历史
            messages = []
            
            # 如果是面试场景且有简历信息，添加系统提示词
            if self.resume_data and len(self.conversation_history) <= 2:
                system_prompt = self.generate_interview_prompt(self.resume_data)
                messages.append({"role": "system", "content": system_prompt})
            
            # 添加对话历史（只发送最近10条消息以控制token使用）
            recent_history = self.conversation_history[-10:]
            for msg in recent_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # 使用星火HTTP API调用
            if SPARK_API_AVAILABLE:
                ai_message = self._call_spark_http_api(messages, model)
            else:
                # 备用方案：使用智能回复
                ai_message = self._get_intelligent_fallback_response(user_message, messages)
            
            # 添加AI回复到历史
            self.add_message("assistant", ai_message)
            
            return {
                "success": True,
                "message": ai_message,
                "usage": {},
                "model": model
            }
            
        except Exception as e:
            print(f"❌ 星火API调用失败: {str(e)}")
            return {
                "success": False,
                "error": f"API调用失败: {str(e)}",
                "message": "抱歉，我现在无法回答您的问题，请稍后再试。"
            }
    
    def _call_spark_http_api(self, messages, model="SPARK MAX"):
        """使用星火HTTP API调用"""
        try:
            print("🔄 调用星火HTTP API...")
            
            # 设置请求头 - 参考您的http_demo.py
            headers = {
                'Authorization': f'Bearer {SPARK_API_PASSWORD}',
                'Content-Type': 'application/json'
            }
            
            # 构建请求体 - 参考您的http_demo.py格式
            body = {
                "model": model,
                "user": "interview_system_user",
                "messages": messages,
                "stream": False,  # 使用非流式响应，简化处理
                "max_tokens": 2048,
                "temperature": 0.7
            }
            
            # 发送HTTP请求
            response = requests.post(
                url=SPARK_API_URL,
                json=body,
                headers=headers,
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            # 解析响应
            result = response.json()
            
            # 提取回复内容
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    ai_message = choice['message']['content']
                    print(f"✅ 星火API调用成功，回复长度: {len(ai_message)}")
                    
                    # 记录token使用情况（如果API返回了usage信息）
                    if 'usage' in result:
                        print(f"📊 Token使用: {result['usage']}")
                    
                    return ai_message
                else:
                    raise Exception("API返回格式异常：缺少message.content字段")
            else:
                raise Exception("API返回格式异常：缺少choices字段")
            
        except requests.exceptions.Timeout:
            print("❌ 星火API调用超时")
            raise Exception("API调用超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            print("❌ 星火API连接失败")
            raise Exception("网络连接失败，请检查网络设置")
        except json.JSONDecodeError as e:
            print(f"❌ API响应解析失败: {str(e)}")
            raise Exception("API响应格式错误")
        except Exception as e:
            print(f"❌ 星火HTTP API调用失败: {str(e)}")
            raise e
    
    def _get_fallback_response(self, user_message):
        """备用回复方案"""
        fallback_responses = [
            "谢谢您的分享。请继续详细说明一下您在这方面的具体经验。",
            "很好！您提到的这个点很有趣。能否举个具体的例子来说明？",
            "我理解了。基于您刚才的回答，我想了解一下您是如何解决相关挑战的？",
            "非常好的回答！请问您对未来在这个领域的发展有什么规划吗？",
            "您的经验很丰富。能否谈谈您在团队协作方面的体会？"
        ]
        import random
        return random.choice(fallback_responses)
    
    def _get_intelligent_fallback_response(self, user_message, conversation_history):
        """智能备用回复方案 - 根据对话内容生成更合适的回复"""
        user_msg_lower = user_message.lower()
        
        # 根据关键词匹配合适的回复
        if any(keyword in user_msg_lower for keyword in ['项目', '开发', '技术', '编程', '代码']):
            responses = [
                "很好！您在技术方面的经验很丰富。能否详细说说您在项目中遇到的最大挑战是什么？您是如何解决的？",
                "您提到的技术经验很有价值。请问您通常是如何学习新技术的？有什么心得可以分享吗？",
                "听起来您的技术背景很扎实。能否举个具体的项目例子，说说您在其中承担的角色和贡献？"
            ]
        elif any(keyword in user_msg_lower for keyword in ['团队', '合作', '沟通', '协作', '管理']):
            responses = [
                "团队协作确实很重要。能否分享一个您在团队中发挥重要作用的具体例子？",
                "您的团队合作经验很宝贵。请问您是如何处理团队中的意见分歧的？",
                "沟通能力是很关键的。能否谈谈您在跨部门协作中的经验？"
            ]
        elif any(keyword in user_msg_lower for keyword in ['学习', '成长', '发展', '提升', '进步']):
            responses = [
                "持续学习的态度很棒！请问您平时是通过什么途径来保持技能更新的？",
                "您的学习能力很强。能否分享一次让您印象深刻的学习经历？",
                "成长心态很重要。您觉得在职业发展中，最重要的能力是什么？"
            ]
        elif any(keyword in user_msg_lower for keyword in ['挑战', '困难', '问题', '解决']):
            responses = [
                "面对挑战的态度很积极！能否详细说说您是如何分析和解决问题的？",
                "您的问题解决能力很强。请问您在解决复杂问题时有什么方法论吗？",
                "挑战往往带来成长。这个经历给您带来了什么收获？"
            ]
        elif any(keyword in user_msg_lower for keyword in ['未来', '计划', '目标', '期望', '发展']):
            responses = [
                "您的职业规划很清晰。能否谈谈您希望在我们公司实现什么样的目标？",
                "很好的发展思路！请问您认为这个职位如何帮助您实现职业目标？",
                "您的未来规划很有意思。您觉得在实现这些目标过程中，可能会遇到什么挑战？"
            ]
        else:
            # 默认通用回复
            responses = [
                "谢谢您的分享！这很有意思。能否再详细说明一下？",
                "很好！从您的回答中我能感受到您的热情。请问您还有什么想补充的吗？",
                "听起来很不错。基于您刚才提到的，我想了解更多细节。",
                "您的经验很丰富。能否举个具体的例子来说明一下？",
                "这个回答很有价值。请问您从中学到了什么？"
            ]
        
        import random
        return random.choice(responses)
    
    def generate_first_question(self, resume_data):
        """根据简历生成第一个面试问题"""
        try:
            # 设置简历数据
            self.set_resume(resume_data)
            
            # 生成系统提示词并获取第一个问题
            system_prompt = self.generate_interview_prompt(resume_data)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "请开始面试，给出开场白和第一个问题。"}
            ]
            
            # 使用星火HTTP API调用
            if SPARK_API_AVAILABLE:
                first_question = self._call_spark_http_api(messages, SPARK_MODEL)
            else:
                # 备用方案：使用默认问题
                name = resume_data.get('name', '求职者')
                position = resume_data.get('targetPosition', '这个职位')
                first_question = f"您好 {name}！很高兴见到您。我看到您申请的是{position}，请先简单介绍一下您自己，包括您的教育背景和相关工作经验。"
            
            # 添加到对话历史
            self.add_message("assistant", first_question)
            
            return {
                "success": True,
                "question": first_question
            }
            
        except Exception as e:
            print(f"❌ 生成面试问题失败: {str(e)}")
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
                "tts_available": TTS_API_AVAILABLE,
                "asr_available": ASR_API_AVAILABLE,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"],
                "response": result["message"],
                "tts_available": TTS_API_AVAILABLE,
                "asr_available": ASR_API_AVAILABLE
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
                "tts_available": TTS_API_AVAILABLE,
                "asr_available": ASR_API_AVAILABLE,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # 即使API调用失败，也返回默认问题
            return jsonify({
                "success": True,
                "firstQuestion": result["question"],
                "message": "简历提交成功，面试已开始（使用默认问题）",
                "error": result.get("error"),
                "tts_available": TTS_API_AVAILABLE,
                "asr_available": ASR_API_AVAILABLE,
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

@app.route('/api/tts/generate', methods=['POST'])
def generate_speech():
    """生成语音接口"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "请求格式错误，需要包含'text'字段"
            }), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({
                "success": False,
                "error": "文本内容不能为空"
            }), 400
        
        # 文本长度限制
        if len(text) > 500:
            return jsonify({
                "success": False,
                "error": "文本长度不能超过500字符"
            }), 400
        
        print(f"🔊 开始为文本生成语音: {text[:50]}...")
        
        # 调用TTS服务
        audio_data = chat_service.tts_service.text_to_speech(text)
        
        if audio_data is None:
            return jsonify({
                "success": False,
                "error": "语音合成失败"
            }), 500
        
        # 生成唯一的音频文件名
        audio_id = str(uuid.uuid4())
        
        # 保存音频文件到内存
        audio_buffer = io.BytesIO(audio_data)
        audio_buffer.seek(0)
        
        # 返回音频文件
        return send_file(
            audio_buffer,
            as_attachment=True,
            download_name=f'tts_{audio_id}.mp3',
            mimetype='audio/mpeg'
        )
        
    except Exception as e:
        print(f"❌ 语音生成失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@app.route('/api/tts/status', methods=['GET'])
def get_tts_status():
    """获取TTS服务状态"""
    return jsonify({
        "success": True,
        "tts_available": TTS_API_AVAILABLE,
        "message": "TTS服务可用" if TTS_API_AVAILABLE else "TTS服务不可用，请检查配置"
    })

@app.route('/api/asr/recognize', methods=['POST'])
def recognize_speech():
    """语音识别接口"""
    try:
        # 检查是否有上传的文件
        if 'audio' not in request.files:
            return jsonify({
                "success": False,
                "error": "请求中缺少音频文件"
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                "success": False,
                "error": "未选择音频文件"
            }), 400
        
        # 读取音频数据
        audio_data = audio_file.read()
        
        if not audio_data:
            return jsonify({
                "success": False,
                "error": "音频文件为空"
            }), 400
        
        print(f"🎤 收到音频文件，大小: {len(audio_data)} bytes")
        
        # 调用ASR服务
        recognition_result = chat_service.asr_service.recognize_speech(audio_data)
        
        if recognition_result is None:
            return jsonify({
                "success": False,
                "error": "语音识别失败"
            }), 500
        
        if not recognition_result.strip():
            return jsonify({
                "success": False,
                "error": "未识别到有效内容，请重新录音"
            }), 400
        
        return jsonify({
            "success": True,
            "text": recognition_result,
            "message": "语音识别成功",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ 语音识别失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@app.route('/api/asr/status', methods=['GET'])
def get_asr_status():
    """获取ASR服务状态"""
    return jsonify({
        "success": True,
        "asr_available": ASR_API_AVAILABLE,
        "message": "语音识别服务可用" if ASR_API_AVAILABLE else "语音识别服务不可用，请检查配置"
    })

if __name__ == '__main__':
    print("🚀 启动智能面试系统后端服务...")
    print(f"📡 API URL: {SPARK_API_URL}")
    print(f"🔑 API密钥配置: {'✓ 已配置' if SPARK_API_PASSWORD and SPARK_API_PASSWORD.strip() != '' else '✗ 未配置'}")
    print(f"🤖 使用模型: {SPARK_MODEL}")
    print(f"⚡ 星火HTTP API: {'✓ 可用' if SPARK_API_AVAILABLE else '✗ 不可用 (将使用备用方案)'}")
    print(f"🔊 语音合成TTS: {'✓ 可用' if TTS_API_AVAILABLE else '✗ 不可用'}")
    print(f"🎤 语音识别ASR: {'✓ 可用' if ASR_API_AVAILABLE else '✗ 不可用'}")
    print("🌐 服务器地址: http://localhost:5000")
    print("📋 健康检查: http://localhost:5000/api/health")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 