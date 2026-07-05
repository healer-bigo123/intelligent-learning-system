# 智能学习助手 - 部署说明

## 项目概述

这是一个基于AI的智能学习助手系统，包含前端应用、后端服务和数据库。

## 目录结构

```
dist-packages/
├── frontend/          # 前端静态文件（已构建）
├── backend/           # 后端Python代码
│   ├── app/           # 应用核心代码
│   ├── data/          # SQLite数据库和向量数据库
│   └── requirements.txt # 依赖列表
└── README.md          # 部署说明
```

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+ (可选，用于开发模式)

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `backend/.env` 文件，配置LLM API Key：

```env
# 火山方舟 API Key（必须配置）
VOLCES_API_KEY=your-api-key-here
VOLCES_MODEL=deepseek-v3-2-251201

# 其他配置（保持默认即可）
LLM_PROVIDER=volces
DATABASE_URL=sqlite:///./data/smart_learning.db
```

### 3. 启动后端服务

```bash
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动

### 4. 启动前端服务

**方式一：使用静态文件服务器（推荐）**

```bash
# 方法1：使用Python
cd frontend
python -m http.server 5173

# 方法2：使用Node.js
npx serve -l 5173
```

**方式二：使用开发模式**

```bash
cd frontend
npm install
npm run dev
```

### 5. 访问应用

打开浏览器访问 `http://localhost:5173`

## API 文档

启动后端后，可访问以下地址查看API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 功能模块

| 模块 | 说明 |
|------|------|
| 智能助手 | 6个AI智能体（答疑、规划、批改、陪伴、推荐、分析） |
| 学习资源 | 课程、资料管理 |
| 学习记录 | 学习时长统计、内容分布分析 |
| 个人中心 | 用户信息、学习目标设置 |
| 错题本 | 错题收集与复习 |

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite
- **后端**: FastAPI + SQLAlchemy
- **数据库**: SQLite + Chroma (向量数据库)
- **LLM**: 火山方舟 DeepSeek

## 注意事项

1. **LLM配置**：必须配置有效的API Key才能使用AI功能
2. **端口占用**：确保5173和8000端口未被占用
3. **首次启动**：数据库会自动初始化，无需手动创建表
4. **数据持久化**：SQLite数据库文件位于 `backend/data/smart_learning.db`

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /F /PID <PID>
   ```

2. **依赖安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --timeout=120
   ```

3. **前端无法连接后端**
   - 确保后端服务已启动
   - 检查浏览器控制台是否有CORS错误
   - 确认前端配置的后端地址正确

## 联系信息

如有问题，请联系开发者。
