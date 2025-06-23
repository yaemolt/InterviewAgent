# AI Coding 上下文压缩范式

------

## 1. 范式概述

为了在大规模项目中向 AI 模型提供精炼且富有语义的信息，我们需要将代码中的每个函数/方法抽象成一个**语义化节点（Semantic Node）**，并以 JSON 格式进行压缩存储。这种做法有助于：

- **减少上下文长度**：剔除冗余细节，仅保留对理解逻辑必要的关键信息。
- **提高检索效率**：通过结构化字段快速定位函数间调用关系和模块依赖。
- **增强可维护性**：节点化表示便于后续自动化分析、文档生成及可视化。

------

## 2. JSON 语义节点定义

```jsonc
{
  "name":       "string",          // 函数或方法名
  "type":       "function|method", // 标记：函数(function) 或 方法(method)
  "output":     "string",          // 返回值类型，如 "void"、"int"、"Promise<User>"
  "description":"string",          // 功能简介或注释
  "path":       "string",          // 所在文件绝对或相对路径
  "file":       "string",          // 文件名
  "line":       number,            // 源码起始行号
  "content": {                     // 语义内容
    "imports":        ["string"],  // 该节点依赖的模块路径列表
    "variables":      [            // 关键局部变量
      { "name":"string", "type":"string" }
    ],
    "functionCalls": [             // 内部函数调用
      {
        "name": "string",          // 被调用函数名
        "path": "string",          // 定义所在路径
        "args": ["string"]         // 主要参数或简要描述
      }
    ],
    "methodCalls": [               // 对象方法调用
      {
        "receiver": "string",      // 调用者对象/类型
        "name":     "string",      // 方法名
        "path":     "string",      // 定义所在路径
        "args":     ["string"]
      }
    ],
    "comments": "string"           // 额外注释或 TODO 标记
  }
}
```

------

## 3. 压缩流程

1. **代码解析**
    使用语言对应的 AST 解析器（如 Python 的 `ast`、JavaScript 的 `acorn`、Java 的 `javaparser` 等），遍历每个函数/方法节点。
2. **抽取元信息**
   - 签名：`name`、`output`、起始 `line`
   - 注释：函数上方或内联注释提取到 `description`
   - 文件信息：`path`、`file`
3. **提取依赖与调用**
   - **imports**：收集 `import`/`require`/`include` 语句
   - **variables**：筛选关键局部变量（如全局状态、核心数据结构）
   - **functionCalls** / **methodCalls**：检测函数/方法调用，并记录调用者、被调用者及参数简述
4. **组装 JSON 节点**
    将上述信息填充到“JSON 语义节点”模板中，生成压缩结果
5. **存储与索引**
    按模块或包路径分文件保存，或汇总到一个大文件中并生成索引，便于后续检索与加载

------

## 4. 示例

### 4.1 源代码片段

```python
# src/app.py
def main():
    """
    程序入口：处理用户注册并自动登录
    """
    from models.user import User
    user = User.register(username="alice", password="secure")
    if user.is_active:
        user.login()
```

### 4.2 压缩后 JSON 节点

```json
{
  "name":        "main",
  "type":        "function",
  "output":      "None",
  "description": "程序入口：处理用户注册并自动登录",
  "path":        "src/app.py",
  "file":        "app.py",
  "line":        1,
  "content": {
    "imports": [
      "models.user.User"
    ],
    "variables": [
      { "name":"user", "type":"User" }
    ],
    "functionCalls": [
      {
        "name": "User.register",
        "path": "src/models/user.py",
        "args": ["username", "password"]
      }
    ],
    "methodCalls": [
      {
        "receiver": "user",
        "name":     "login",
        "path":     "src/models/user.py",
        "args":     []
      }
    ],
    "comments": "检查用户激活状态后自动调用登录"
  }
}
```



------

### 4.3 函数调用链示例

下面通过JavaScript示例说明多层函数调用链的压缩节点表示：

#### 源代码片段

```javascript
// utils/math.js
export function add(a, b) {
  return a + b;
}

// services/calculator.js
import { add } from '../utils/math.js';
export function calculateSum(arr) {
  return arr.reduce((sum, val) => add(sum, val), 0);
}

// app.js
import { calculateSum } from './services/calculator.js';
function run() {
  const numbers = [1, 2, 3, 4];
  const total = calculateSum(numbers);
  console.log(`Total: ${total}`);
}
```

#### 压缩后 JSON 语义节点

```json
// utils/math.js
{
  "name": "add",
  "type": "function",
  "output": "number",
  "description": "对两个数字求和",
  "path": "utils/math.js",
  "file": "math.js",
  "line": 1,
  "content": {
    "imports": [],
    "variables": [],
    "functionCalls": [],
    "methodCalls": [],
    "comments": "返回a和b的和"
  }
}
// services/calculator.js
{
  "name": "calculateSum",
  "type": "function",
  "output": "number",
  "description": "计算数组所有元素之和",
  "path": "services/calculator.js",
  "file": "calculator.js",
  "line": 1,
  "content": {
    "imports": ["utils/math.add"],
    "variables": [
      { "name": "arr", "type": "number[]" }
    ],
    "functionCalls": [
      { "name": "add", "path": "utils/math.js", "args": ["sum", "val"] }
    ],
    "methodCalls": [
      { "receiver": "arr", "name": "reduce", "path": "services/calculator.js", "args": ["callback", "0"] }
    ],
    "comments": "使用reduce循环调用add累加"
  }
}
// app.js
{
  "name": "run",
  "type": "function",
  "output": "void",
  "description": "程序入口：运行计算逻辑并输出结果",
  "path": "app.js",
  "file": "app.js",
  "line": 1,
  "content": {
    "imports": ["services/calculator.calculateSum"],
    "variables": [
      { "name": "numbers", "type": "number[]" },
      { "name": "total",   "type": "number" }
    ],
    "functionCalls": [
      { "name": "calculateSum", "path": "services/calculator.js", "args": ["numbers"] }
    ],
    "methodCalls": [
      { "receiver": "console", "name": "log", "path": "app.js", "args": ["`Total: ${total}`"] }
    ],
    "comments": "依次调用calculateSum并输出结果"
  }
}
```

#### 调用链视图

```
run() → calculateSum(arr) → add(a, b)
```

------