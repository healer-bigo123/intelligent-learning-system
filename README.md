# SmartLearning-MAS

基于大模型的个性化资源生成与学习多智能体系统

## 项目结构

```
.
├── backend/                 # Python 后端服务
│   ├── app/
│   │   ├── api/v1/endpoints/  # API 接口
│   │   ├── core/              # 核心模块（配置、向量库、知识库）
│   │   ├── agents/            # 智能体实现
│   │   ├── models/            # 数据模型
│   │   └── services/          # 业务服务
│   ├── main.py              # FastAPI 入口
│   ├── requirements.txt     # Python 依赖
│   ├── setup.py             # 安装配置
│   └── .env.example         # 环境变量模板
│
├── frontend/                # React 前端
│   ├── src/
│   │   ├── components/      # 公共组件
│   │   ├── pages/           # 页面
│   │   ├── App.tsx          # 路由配置
│   │   └── main.tsx         # 入口
│   ├── package.json         # Node 依赖
│   ├── vite.config.ts       # Vite 配置
│   └── tailwind.config.js   # Tailwind 配置
│
├── docs/                    # 文档
├── data/                    # 数据目录
└── knowledge_base/          # 知识库文档
```

## 快速开始

### 1. 环境要求

- Python >= 3.11
- Node.js >= 18
- Git

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# Windows 激活
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 填写科大讯飞 API 密钥

# 启动服务
python main.py
```

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问系统

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 核心功能

- 智能对话（支持 RAG 检索增强）
- 知识库管理（文档上传、语义检索）
- 多智能体协同（6 大智能体角色）
- 学生画像分析（6 大维度）
- 个性化资源生成

## 技术栈

| 层级 | 技术 |
|-----|------|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS + Ant Design |
| 后端 | Python + FastAPI |
| 多智能体 | LangChain + AutoGen |
| 向量数据库 | Chroma + FAISS |
| 大模型 | 科大讯飞星火 API |
| Embedding | BGE-Large-Zh |

## 开发团队

第十五届中国软件杯大赛 A3 赛题
