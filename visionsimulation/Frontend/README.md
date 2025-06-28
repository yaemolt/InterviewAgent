# 智能情绪识别系统 - 前端

## 项目概述

本项目是一个基于 Vue 3 + Vite 的智能情绪识别系统前端应用，通过摄像头实时捕获用户面部表情，每秒发送 8 帧视频片段到后端进行情绪识别分析，并提供详细的结果展示和数据导出功能。

## 主要功能

### 🎥 实时摄像头预览
- 使用 `MediaDevices.getUserMedia` 获取摄像头权限
- 设置帧率为 8fps，确保每秒正好采集 8 帧画面
- 支持移动端和桌面端的摄像头适配

### 📹 智能视频录制
- 使用 `MediaRecorder` 每隔 1 秒触发 `ondataavailable` 事件
- 每个视频片段包含 8 帧图像数据
- 自动发送到后端 API `/api/face/emotionRecognition`

### 🧠 情绪识别与分析
- 实时显示最新识别结果
- 记录识别次数和置信度
- 支持多种情绪类型识别

### 📊 结果统计展示
- 详细的情绪识别记录列表
- 情绪分布统计图表
- 主要情绪、平均置信度等关键指标
- JSON 格式数据导出功能

## 技术栈

### 核心框架
- **Vue 3.4+**: 使用 Composition API
- **Vite 5.x**: 现代化构建工具
- **JavaScript ES6+**: 现代 JavaScript 语法

### 主要依赖
- **axios 1.6+**: HTTP 请求库
- **@vitejs/plugin-vue**: Vue 单文件组件支持

### 开发工具
- **ESLint**: 代码质量检查
- **Prettier**: 代码格式化
- **Vite Dev Server**: 开发服务器与热重载

## 项目结构

```
src/
├── api/                    # API 调用层
│   └── emotion.js         # 情绪识别 API 配置
├── components/            # Vue 组件
│   ├── CameraEmotionPage.vue    # 摄像头情绪识别主页面
│   └── EmotionResult.vue        # 结果展示组件
├── styles/               # 样式文件
│   └── index.css        # 全局样式
├── App.vue              # 根组件
└── main.js             # 应用入口
```

## API 接口说明

### 情绪识别接口
- **URL**: `POST /api/face/emotionRecognition`
- **Content-Type**: `multipart/form-data`
- **参数**: `video` (Blob) - 视频片段数据
- **响应格式**:
```json
{
  "success": true,
  "emotion": "happy",
  "confidence": 0.85,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## 开发规范

### 组件命名
- **文件名**: PascalCase (`CameraEmotionPage.vue`)
- **组件名**: PascalCase (`<CameraEmotionPage />`)
- **CSS 类名**: BEM 规范 (`.camera-emotion-page__container`)

### 样式规范
- 所有样式使用 `scoped` 作用域
- 遵循 BEM (Block Element Modifier) 命名规范
- 支持响应式设计，适配移动端

### 代码规范
- 使用 Vue 3 Composition API
- ES6+ 语法和现代 JavaScript 特性
- 完整的错误处理和用户反馈

## 快速开始

### 环境要求
- Node.js 16+ 
- npm 或 yarn 包管理器
- 现代浏览器支持 (Chrome 88+, Firefox 78+, Safari 14+)

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

应用将在 `http://localhost:5175` 启动

### 构建生产版本
```bash
npm run build
```

### 预览生产构建
```bash
npm run preview
```

## 配置说明

### Vite 配置
- 开发服务器端口: 5175
- API 代理: `/api` -> `http://localhost:5000`
- 支持热重载和快速刷新

### 浏览器支持
- Chrome 88+ (推荐)
- Firefox 78+
- Safari 14+
- Edge 88+

## 核心特性详解

### 1. 摄像头约束配置
```javascript
const constraints = {
  video: {
    frameRate: { ideal: 8, max: 8 }, // 8fps 确保每秒8帧
    width: { ideal: 640, max: 1280 },
    height: { ideal: 480, max: 720 },
    facingMode: 'user'
  }
}
```

### 2. 视频录制机制
```javascript
// 每1000ms触发一次，收集8帧数据
mediaRecorder.start(1000)

mediaRecorder.ondataavailable = async (event) => {
  // event.data 包含8帧视频数据
  await handleVideoData(event.data)
}
```

### 3. 响应式状态管理
```javascript
const emotionResults = ref([])     // 存储所有识别结果
const isRecording = ref(false)     // 录制状态
const latestEmotion = computed(() => {
  // 计算最新情绪结果
})
```

## 故障排除

### 常见问题

1. **摄像头权限被拒绝**
   - 检查浏览器设置，允许摄像头访问
   - 确保使用 HTTPS 或 localhost 访问

2. **API 请求失败**
   - 确认后端服务已启动在 `localhost:5000`
   - 检查网络连接和防火墙设置

3. **视频录制异常**
   - 检查浏览器是否支持 `MediaRecorder` API
   - 确认 `video/webm` 格式支持

4. **性能问题**
   - 降低视频分辨率设置
   - 检查设备摄像头性能

### 浏览器兼容性检查
```javascript
// 检查必要的 API 支持
if (!navigator.mediaDevices?.getUserMedia) {
  console.error('浏览器不支持 getUserMedia')
}

if (!window.MediaRecorder) {
  console.error('浏览器不支持 MediaRecorder')
}
```

## 性能优化

- 使用 `v-memo` 缓存复杂列表渲染
- 合理使用 `computed` 计算属性
- 避免不必要的响应式数据
- 及时清理摄像头资源

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 版本历史

- **v1.0.0** - 初始版本
  - 基础摄像头功能
  - 情绪识别集成
  - 结果展示界面
  - 数据导出功能 