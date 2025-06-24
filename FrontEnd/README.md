# 我的聊天应用 (my-chat)

基于 Vue 3 + Vite 构建的现代化聊天应用界面。

## 项目结构

```
my-chat/
├── public/
│   └── index.html              # HTML 入口文件
├── src/
│   ├── main.js                 # 应用入口
│   ├── App.vue                 # 根组件
│   ├── api/
│   │   └── chat.js             # 聊天 API 接口
│   ├── components/
│   │   ├── ChatList.vue        # 消息列表组件
│   │   └── ChatInput.vue       # 输入框组件
│   ├── assets/
│   │   └── logo.png            # 项目图标
│   ├── styles/
│   │   └── index.css           # 全局样式
│   └── utils/
│       └── index.js            # 工具函数
├── package.json                # 项目配置
├── vite.config.js              # Vite 配置
├── .eslintrc.cjs               # ESLint 配置
├── .prettierrc                 # Prettier 配置
└── .gitignore                  # Git 忽略文件
```

## 功能特性

- ✨ 现代化的聊天界面设计
- 🚀 基于 Vue 3 Composition API
- ⚡ Vite 快速构建工具
- 📱 响应式布局设计
- 🎨 美观的消息气泡样式
- 🔄 自动滚动到最新消息
- ⌨️ 支持回车发送消息
- 🛡️ ESLint + Prettier 代码规范
- 🌐 支持模拟API响应（开发模式）

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

服务器将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
```

### 代码检查

```bash
npm run lint
```

### 格式化代码

```bash
npm run format
```

## API 配置

项目中的 `src/api/chat.js` 文件包含了聊天接口的配置。

### 开发模式
默认情况下，项目会尝试连接到 `http://localhost:8080/api/chat`。如果连接失败，会自动使用模拟响应。

### 生产模式
生产环境下会使用 `/api/chat` 作为接口地址。

### API 接口格式

**请求格式：**
```json
POST /api/chat
{
  "message": "用户消息内容",
  "timestamp": 1234567890123
}
```

**响应格式：**
```json
{
  "message": "AI回复内容",
  "timestamp": 1234567890123
}
```

## 自定义配置

### 修改主题色彩
在 `src/styles/index.css` 中修改以下CSS变量：
- 主色调：`#007aff`
- 用户消息背景：`.message.user`
- 机器人消息背景：`.message.bot`

### 添加新功能
1. 在 `src/components/` 目录下创建新组件
2. 在 `src/utils/index.js` 中添加工具函数
3. 在 `src/api/` 目录下添加新的API接口

## 技术栈

- **前端框架：** Vue 3
- **构建工具：** Vite
- **HTTP 客户端：** Axios
- **代码规范：** ESLint + Prettier
- **样式：** 原生 CSS

## 浏览器支持

支持所有现代浏览器，包括：
- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 许可证

MIT License 