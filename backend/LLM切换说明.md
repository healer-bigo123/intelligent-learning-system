# 大模型 API 切换说明

## 设计原则

**切换大模型 API，只需修改 `.env` 文件中的 1 个配置项，无需改动任何业务代码。**

业务代码（`chat.py`、`agents.py` 等）只调用统一的 `llm_client.chat()` 接口，不关心底层是哪家厂商的 API。

---

## 支持的厂商

| 厂商 | `LLM_PROVIDER` 值 | 特点 |
|-----|------------------|------|
| 火山方舟 | `volces` | 当前主用，支持 DeepSeek，原生支持 web_search |
| 讯飞星火 | `xinghuo` | 国产大模型，WebSocket 流式，需鉴权 |
| OpenAI | `openai` | 国际通用，Function Calling 完善 |

---

## 切换步骤

### 1. 修改 `.env` 文件

```env
# 切换前（火山方舟）
LLM_PROVIDER=volces

# 切换后（讯飞星火）
LLM_PROVIDER=xinghuo
```

### 2. 填写对应厂商的 API 密钥

```env
# 讯飞星火配置（在讯飞开放平台申请：https://www.xfyun.cn/）
XINGHUO_APP_ID=你的APP_ID
XINGHUO_API_KEY=你的API_KEY
XINGHUO_API_SECRET=你的API_SECRET
XINGHUO_BASE_URL=https://spark-api-open.xf-yun.com/v1
XINGHUO_DOMAIN=generalv3.5
XINGHUO_MODEL=generalv3.5
```

### 3. 重启后端服务

```bash
# 停止当前服务（Ctrl+C），然后重新启动
python main.py
```

启动时会显示：
```
🤖 使用讯飞星火 API
```

---

## 各厂商配置项说明

### 火山方舟（当前主用）

```env
LLM_PROVIDER=volces
VOLCES_API_KEY=ark-xxx
VOLCES_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VOLCES_MODEL=deepseek-v3-2-251201
```

### 讯飞星火

```env
LLM_PROVIDER=xinghuo
XINGHUO_APP_ID=xxx
XINGHUO_API_KEY=xxx
XINGHUO_API_SECRET=xxx
XINGHUO_BASE_URL=https://spark-api-open.xf-yun.com/v1
XINGHUO_DOMAIN=generalv3.5
XINGHUO_MODEL=generalv3.5
```

**注意**：讯飞星火流式输出需要安装 `websockets` 库：
```bash
pip install websockets
```

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

---

## 功能差异说明

| 功能 | 火山方舟 | 讯飞星火 | OpenAI |
|-----|---------|---------|--------|
| 基础对话 | ✅ | ✅ | ✅ |
| 流式输出 | ✅ SSE | ✅ WebSocket | ✅ SSE |
| 联网搜索 | ✅ 原生支持 | ⚠️ Prompt模拟 | ✅ Function Calling |
| 工具调用 | ✅ | ❌ | ✅ |
| 多模态 | ❌ | ❌ | ✅ GPT-4o |

**联网搜索差异**：
- 火山方舟：原生支持 `web_search` 工具，自动搜索互联网
- 讯飞星火：暂不支持原生工具，通过 prompt 工程模拟（告知模型知识截止日期）
- OpenAI：支持 Function Calling，可自定义搜索工具

---

## 技术架构

```
业务代码 (chat.py, agents.py)
        ↓
    llm_client (统一接口)
        ↓
    BaseLLMClient (抽象基类)
        ↓
   ┌─────────┬─────────┬─────────┐
   ↓         ↓         ↓
Volces   Xinghuo   OpenAI
```

- `BaseLLMClient`：定义统一接口（`chat`、`chat_stream`、`generate_with_web_search`）
- `VolcesLLMClient`：火山方舟适配器
- `XinghuoLLMClient`：讯飞星火适配器
- `OpenAILLMClient`：OpenAI 适配器
- `create_llm_client()`：工厂函数，根据 `LLM_PROVIDER` 自动创建对应实例

---

## 添加新的厂商支持

如需接入其他大模型（如文心一言、通义千问等）：

1. 在 `app/core/llm_client.py` 中新建适配器类，继承 `BaseLLMClient`
2. 实现 `chat()`、`chat_stream()`、`generate_with_web_search()` 三个方法
3. 在 `create_llm_client()` 工厂函数中添加分支判断
4. 在 `config.py` 中添加对应的环境变量配置
5. 在 `.env` 中添加配置项

**无需修改任何业务代码。**
