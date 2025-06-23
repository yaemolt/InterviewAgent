# 智能面试系统技术文档提纲

## 1. 引言

- 1.1 文档目的：
   本技术文档旨在系统化梳理并全面阐述智能面试系统的各模块设计与实现细节，为团队成员提供清晰的技术路线和协作指南，助力快速上手并高效推进开发工作。
- 1.2 项目背景：
   本项目基于第十四届“中国软件杯”大学生软件设计大赛 A 组赛题，旨在开发一款多模态智能面试评测系统，通过面部情绪识别、语音流畅度评估和大模型问答等技术手段，为高校学生提供高仿真、全方位的在线模拟面试体验，帮助提升面试能力与求职竞争力。
- 1.3 范围与读者：
   描述本技术文档所涵盖的系统模块和功能范围，面向系统架构师、前后端开发工程师、测试工程师及运维人员。

## 2. 系统架构概述

- 2.1 整体架构图：
  - 前端（Vue 3 SPA）
    - 页面展示、路由管理、表单收集、摄像头&麦克风数据采集
  - 后端（FastAPI 服务）
    - RESTful API（Axios 调用）
    - 人脸识别服务：本地部署 Python 模型，输入视频，输出情绪标签
    - ASR 服务：后端调用第三方语音转文字 API，返回文本结果
    - 流畅度评估服务：基于关键词切分和停顿统计计算停顿次数、语速等指标
    - 大模型问答服务：调用星火大模型 API 生成面试问题与反馈
  - 数据存储层（SQLite 开发/本地）
    - 存储用户信息、面试会话、分析结果等，保证一致性与持久化
  - 第三方服务
    - 语音转文字 API（已备案账号）
    - 星火大模型 API
- 2.2 模块划分：
  1. **前端模块（Vue 3）**：
     - 登录/注册、用户信息管理、简历编辑、面试配置、面试界面、结果报告
  2. **后端接口层（FastAPI）**：
     - auth.py：用户认证授权（JWT）
     - interview.py：面试流程控制（问题获取、答案提交、反馈生成）
     - face_service.py：调用本地人脸识别模型，返回情绪标签
     - asr_service.py：封装第三方语音转文字 API 调用
     - fluency_service.py：实现流畅度评估规则，输出停顿次数、语速等
     - lm_service.py：集成星火大模型 API
  3. **数据访问层**：
     - ORM（SQLAlchemy）定义模型：User、Session、AnswerRecord、EvaluationResult
     - CRUD 操作封装与事务管理
  4. **基础设施**：
     - 日志：Python logging，结构化输出
     - 监控：Prometheus + Grafana 采集 API 性能指标
     - 配置管理：dotenv 管理环境变量
- 2.3 技术选型及原因：
  - **前端**：Vue 3 + Vite + Axios + Tailwind CSS，最简配置即可启动开发环境
  - **后端**：FastAPI，异步、自动文档、零样板
  - **人脸识别**：DeepFace（Python 本地部署），一行调用即可输出情绪标签
  - **ASR**：前端 Web Speech API 或后端星火 SDK，优先浏览器端转写，后端云服务调用可选
  - **流畅度评估**：webrtcvad + 自研简易规则（停顿检测、词速计算），零训练成本
  - **大模型**：星火大模型 API，统一调用入口
  - **数据库**：SQLite（开发阶段零配置），生产阶段依然可切换 PostgreSQL
  - **简化**：取消 Docker/Kubernetes、Redis 缓存、Prometheus 监控和 CI/CD 配置，采用本地一键启动方式

## 3. 前端设计. 前端设计

- 3.1 技术栈与框架：

  - Vue 3 + Vite
  - Vue Router 管理路由
  - Pinia 进行状态管理
  - Tailwind CSS 实现原子化样式

- 3.2 页面布局与路由：

  | 路由路径             | 组件            | 功能说明             |
  | -------------------- | --------------- | -------------------- |
  | `/login`             | LoginForm       | 用户登录             |
  | `/register`          | RegisterForm    | 用户注册             |
  | `/profile`           | ProfileEditor   | 编辑个人信息与简历   |
  | `/config`            | InterviewConfig | 配置面试场景与提示词 |
  | `/interview`         | InterviewPanel  | 进行实时多模态面试   |
  | `/report/:sessionId` | ReportView      | 查看面试评估结果     |

- 3.3 核心组件说明：

  1. **LoginForm**：收集邮箱/密码，调用后端 `/api/auth/login`。
  2. **ProfileEditor**：表单上传或编辑简历 JSON，保存至后端 `/api/user/profile`。
  3. **InterviewConfig**：选择岗位、提示词和评估维度，提交至 `/api/interview/start`。
  4. **InterviewPanel**：启动摄像头/麦克风，调用 face-service、ASR、fluency-service 获取实时分析。基于 Axios 发送/接收 JSON 数据。
  5. **ReportView**：展示评分雷达图（基于 `recharts`）及文字反馈。

- 3.4 状态管理方案：

  - **authStore**：存储用户 Token 与登录状态
  - **userStore**：维护用户基本信息与简历内容
  - **interviewStore**：管理当前会话 ID、实时分数与最终报告

- 3.5 多媒体权限与采集：

  ```js
  async function initMedia() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    videoEl.srcObject = stream;
    recognition.start(); // Web Speech API
  }
  ```

  - 使用 `navigator.mediaDevices.getUserMedia` 获取视频流
  - 前端定时截帧并通过 WebSocket 或 REST 发送到后端人脸识别服务
  - `SpeechRecognition` 接口实时收集音频并产生文本

## 4. 后端设计

- 4.1 技术栈与框架：

  - Python 3.9+
  - FastAPI + Uvicorn
  - SQLAlchemy ORM
  - Pydantic 数据校验

- 4.2 系统接口（API）设计：

  | 方法 | 路径                      | 描述                           |
  | ---- | ------------------------- | ------------------------------ |
  | POST | `/api/auth/login`         | 用户登录，返回 JWT             |
  | POST | `/api/auth/register`      | 用户注册                       |
  | GET  | `/api/user/profile`       | 获取用户信息                   |
  | PUT  | `/api/user/profile`       | 更新用户信息                   |
  | POST | `/api/interview/start`    | 新建面试会话，返回 sessionId   |
  | GET  | `/api/interview/question` | 获取下一个问题                 |
  | POST | `/api/interview/answer`   | 提交回答及多模态数据，返回评分 |
  | GET  | `/api/report/{sessionId}` | 获取完整评估报告               |

- 4.3 数据模型与存储：

  ```python
  class User(Base):
      id = Column(Integer, primary_key=True)
      email = Column(String, unique=True)
      password_hash = Column(String)
      profile = Column(JSON)
  class Session(Base):
      id = Column(Integer, primary_key=True)
      user_id = Column(Integer, ForeignKey('user.id'))
      started_at = Column(DateTime)
  class AnswerRecord(Base):
      id = Column(Integer, primary_key=True)
      session_id = Column(Integer, ForeignKey('session.id'))
      question_id = Column(String)
      answer_text = Column(Text)
  class EvaluationResult(Base):
      id = Column(Integer, primary_key=True)
      record_id = Column(Integer, ForeignKey('answerrecord.id'))
      emotion = Column(String)
      fluency_score = Column(Float)
      lm_feedback = Column(Text)
  ```

- 4.4 服务与微服务划分：

  - **face-service**：Python 脚本封装，启动后监听 HTTP 请求
  - **asr-service**：后端模块，调用第三方语音 API
  - **fluency-service**：内嵌规则引擎，分析 ASR 文本输出
  - **lm-service**：调用星火大模型 REST API，返回文本

- 4.5 第三方集成：

  - **星火大模型**：

    ```python
    import requests
    headers = {'Authorization': f"Bearer {API_KEY}"}
    resp = requests.post(
        'https://api.zhipuai.com/v1/chat/completions',
        json={'model': 'spark-v1', 'messages': [...]},
        headers=headers
    )
    ```

  - **语音转文字 API**：

    ```python
    def asr_transcribe(audio_bytes):
        resp = requests.post(
            ASR_URL,
            headers={'Ocp-Apim-Subscription-Key': ASR_KEY},
            data=audio_bytes
        )
        return resp.json()['text']
    ```

## 5. 多模态算法与模型

- 5.1 面部情绪识别模块：
  - 接收视频流或单帧图片，使用 `face_recognition` 库检测人脸
  - 调用自带分类模型预测情绪（如 happy、neutral、angry 等）
  - 返回 `{ emotion: 'happy', confidence: 0.92 }`
- 5.2 语音转文字（ASR）模块：
  - 后端接收前端上传的音频二进制
  - 调用第三方 ASR API，处理并返回标准化文本
- 5.3 语音流畅度评估模块：
  - 基于 ASR 文本，定义停顿阈值（0.3s）统计停顿次数
  - 计算平均词速（wpm = totalWords / totalTime * 60）
  - 输出 `{ pauses: 5, wpm: 110 }`
- 5.4 文字转语音（TTS）模块：
  - 前端使用 Web Speech Synthesis API 播放反馈文本
  - 可选后端集成云 TTS API 提供下载链接
- 5.5 大模型问答与反馈生成：
  - 将对话上下文与评估结果作为 prompt 发送给星火大模型
  - 解析返回的 `choices[0].message.content` 作为下一问题或文字化建议

## 6. 安全与权限管理

- 6.1 身份认证与授权：
  - 使用 JWT 进行无状态认证
  - FastAPI `Depends` + Pydantic 验证用户身份
- 6.2 数据加密与传输安全：
  - 在生产环境部署 HTTPS，前端强制 `https://`
  - 存储密码使用 PBKDF2 或 bcrypt 加盐哈希
- 6.3 防切屏与行为监测：
  - 前端监听 `visibilitychange` 事件，记录切屏时间点
  - 上报后端 `/api/interview/visibility` 存日志

## 7. 性能与可用性

- 7.1 本地开发性能：
  - 人脸识别响应 <200ms/帧
  - ASR 转写延迟 <500ms（浏览器端）
  - 星火模型调用延迟 <1s
- 7.2 简易优化：
  - 端到端直连，无需缓存或队列
  - FastAPI 异步支持并发请求处理
- 7.3 可用性保障：
  - 本地一键启动，无需额外运维
  - 开发过程中可通过 Swagger 页面快速调试接口

## 8. 部署与运维. 部署与运维

- 8.1 本地开发环境搭建：

  ```bash
  cd backend
  uvicorn main:app --reload
  # 打开新终端
  cd frontend
  npm install
  npm run dev
  ```

- 8.2 容器化与部署流程：
   本地环境取消容器化，所有服务均可直接运行。生产环境可选用 Docker，但非必需。

- 8.3 CI/CD 流水线设计：
   对于学习和演示场景，可先手动部署与更新，无需配置自动化流程。

- 8.4 监控与日志：

  - 使用 FastAPI 默认日志记录在控制台，可按需写入文件。
  - 本地开发无需接入 Prometheus 或 Grafana。

## 9. 测试策略. 测试策略

- 9.1 单元测试：
  - 后端：pytest 覆盖核心业务逻辑
  - 前端：Vitest 测试组件与状态管理
- 9.2 接口测试：
  - 使用 HTTPX 或 Postman Collection 自动化执行
- 9.3 E2E 测试：
  - Cypress 脚本模拟用户登录、面试流程
- 9.4 性能与压力测试：
  - Locust 编写脚本压测后端接口
  - Lighthouse 测试前端性能指标

## 10. 维护与扩展

- 10.1 模块化与可扩展性：
  - 各服务通过 REST 接口解耦，支持后续拆分为微服务
  - 前端组件化开发，易于复用与替换
- 10.2 文档更新流程：
  - 采用 Git 流程，所有文档变更通过 PR 审核
  - CI 校验 Markdown 格式与链接有效性
- 10.3 常见问题与支持：
  - 在文档末尾维护 FAQ
  - 提供在线支持渠道（Slack/微信群）

## 11. 附录

- A. 术语表：面部情绪识别、ASR、WPM、JWT 等定义
- B. API 列表：详见 Swagger/OpenAPI 文档
- C. 配置示例：`.env.example` 包含所有环境变量说明
- D. 参考资料：项目教程、第三方 SDK 文档、比赛官方赛题说明