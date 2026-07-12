# 前端 API 接口文档

> **Base URL**: `http://127.0.0.1:8000/api/v1`
>
> **认证方式**: 请求头 `Authorization: Bearer {token}`
>
> **超时时间**: 30000ms
>
> **前端 axios 实例**: `src/api/client.ts`

---

## 1. 错题题库 `/mistakes`

> 后端文件: `endpoints/mistakes.py` | 前端文件: `src/api/mistakes.ts` | 页面: `/mistakes`

### 1.1 添加错题

```
POST /mistakes
Content-Type: application/json
```

**请求体:**

```json
{
  "subject": "数学",
  "question": "题目内容",
  "correct_answer": "正确答案",
  "user_answer": "我的答案",
  "analysis": "解析/反思",
  "knowledge_point": "知识点",
  "tags": ["易错", "重点"],
  "source": "来源",
  "difficulty": 3
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| subject | string | 是 | 学科 |
| question | string | 是 | 题目内容 |
| correct_answer | string | 是 | 正确答案 |
| user_answer | string | 否 | 用户当时的答案 |
| analysis | string | 否 | 解析/反思 |
| knowledge_point | string | 否 | 知识点 |
| tags | string[] | 否 | 标签列表 |
| source | string | 否 | 来源 |
| difficulty | int | 否 | 难度 1-5，默认 3 |

**响应:** `201` 返回错题对象（见 1.3 响应格式）

---

### 1.2 查询错题列表

```
GET /mistakes
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| subject | string | 否 | 按学科筛选 |
| status | string | 否 | 按状态筛选: `unsolved` / `reviewing` / `mastered` |
| knowledge_point | string | 否 | 按知识点筛选（模糊匹配） |
| keyword | string | 否 | 关键词搜索（匹配题目/解析/标签） |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20，最大 100 |

**响应:** `200`

```json
{
  "total": 50,
  "items": [
    { "id": "uuid", "subject": "数学", "question": "...", "correct_answer": "...", "user_answer": "...", "analysis": "...", "knowledge_point": "...", "tags": "易错,重点", "source": "...", "difficulty": 3, "status": "unsolved", "review_count": 0, "last_review_at": null, "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00" }
  ]
}
```

---

### 1.3 获取错题详情

```
GET /mistakes/{mistake_id}
```

**响应:** `200`

```json
{
  "id": "string",
  "user_id": "string",
  "subject": "string",
  "question": "string",
  "correct_answer": "string",
  "user_answer": "string | null",
  "analysis": "string | null",
  "knowledge_point": "string | null",
  "tags": "string",
  "source": "string | null",
  "difficulty": 3,
  "status": "unsolved | reviewing | mastered",
  "review_count": 0,
  "last_review_at": "datetime | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

### 1.4 更新错题

```
PUT /mistakes/{mistake_id}
Content-Type: application/json
```

**请求体:** 所有字段可选，同创建字段，额外支持:

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | `unsolved` / `reviewing` / `mastered` |

**响应:** `200` 返回更新后的错题对象

---

### 1.5 删除错题

```
DELETE /mistakes/{mistake_id}
```

**响应:** `204` 无返回体

---

### 1.6 复习错题

```
POST /mistakes/{mistake_id}/review
```

**响应:** `200`

```json
{
  "message": "复习记录已更新",
  "review_count": 3,
  "status": "mastered"
}
```

> 逻辑: 每次调用 `review_count + 1`，`last_review_at` 更新为当前时间。当 `review_count >= 3` 时自动标记为 `mastered`。

---

### 1.7 错题统计概览

```
GET /mistakes/stats/overview
```

**响应:** `200`

```json
{
  "total": 50,
  "unsolved": 20,
  "reviewing": 15,
  "mastered": 15,
  "by_subject": { "数学": 20, "英语": 15, "物理": 15 }
}
```

---

## 2. 练习测试 `/exercises`

> 后端文件: `endpoints/exercises.py` | 前端文件: `src/api/exercises.ts` | 页面: `/exercises`

### 2.1 创建练习题

```
POST /exercises
Content-Type: application/json
```

**请求体:**

```json
{
  "subject": "数学",
  "type": "choice",
  "question": "题目内容",
  "options": ["A. xxx", "B. xxx", "C. xxx", "D. xxx"],
  "correct_answer": "A",
  "explanation": "答案解析",
  "knowledge_point": "知识点",
  "difficulty": 3
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| subject | string | 是 | 学科 |
| type | string | 是 | 题型: `choice` / `fill_blank` / `short_answer` / `programming` |
| question | string | 是 | 题目内容 |
| options | string[] | 否 | 选择题选项 |
| correct_answer | string | 是 | 正确答案 |
| explanation | string | 否 | 答案解析 |
| knowledge_point | string | 否 | 知识点 |
| difficulty | int | 否 | 难度 1-5，默认 3 |

**响应:** `201` 返回练习题对象

---

### 2.2 查询练习题列表

```
GET /exercises
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| subject | string | 否 | 按学科筛选 |
| type | string | 否 | 按题型筛选 |
| difficulty | int | 否 | 按难度筛选 |
| knowledge_point | string | 否 | 按知识点筛选（模糊匹配） |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20，最大 100 |

**响应:** `200`

```json
{
  "total": 100,
  "items": [
    {
      "id": "string",
      "user_id": "string",
      "subject": "string",
      "type": "choice",
      "question": "string",
      "options": "string | null",
      "correct_answer": "string",
      "explanation": "string | null",
      "knowledge_point": "string | null",
      "difficulty": 3,
      "source": "manual",
      "status": "active",
      "created_at": "datetime"
    }
  ]
}
```

---

### 2.3 获取练习题详情（答题用，不含答案）

```
GET /exercises/{exercise_id}
```

**响应:** `200`

```json
{
  "id": "string",
  "user_id": "string",
  "subject": "string",
  "type": "string",
  "question": "string",
  "options": ["A. xxx", "B. xxx"] | null,
  "knowledge_point": "string | null",
  "difficulty": 3,
  "created_at": "string"
}
```

> 注意: 不返回 `correct_answer` 和 `explanation`

---

### 2.4 获取练习题完整信息（含答案和解析）

```
GET /exercises/{exercise_id}/full
```

**响应:** `200` 返回完整练习题对象（同 2.2 中的 item 格式）

---

### 2.5 提交答案

```
POST /exercises/{exercise_id}/submit
Content-Type: application/json
```

**请求体:**

```json
{
  "user_answer": "A",
  "time_spent": 30
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_answer | string | 是 | 用户答案 |
| time_spent | int | 否 | 耗时（秒），默认 0 |

**响应:** `200`

```json
{
  "is_correct": true,
  "correct_answer": "A",
  "explanation": "答案解析",
  "score": 100
}
```

> 逻辑: 字符串忽略大小写和首尾空格匹配，正确得 100 分，错误得 0 分。同时自动创建 `ExerciseRecord` 记录。

---

### 2.6 获取练习历史

```
GET /exercises/history/list
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| subject | string | 否 | 按学科筛选 |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20，最大 100 |

**响应:** `200`

```json
{
  "total": 30,
  "items": [
    {
      "record_id": "string",
      "exercise_id": "string",
      "question": "string",
      "subject": "string",
      "type": "string",
      "user_answer": "string | null",
      "correct_answer": "string",
      "is_correct": true,
      "score": 100,
      "time_spent": 30,
      "created_at": "string"
    }
  ]
}
```

---

### 2.7 生成练习会话

```
POST /exercises/sessions/generate
Content-Type: application/json
```

**请求体:**

```json
{
  "title": "数学练习",
  "subject": "数学",
  "exercise_count": 5,
  "difficulty": 3
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 练习标题，默认 `{subject} 练习` |
| subject | string | 是 | 学科 |
| exercise_count | int | 否 | 题目数量，默认 5，最大 20 |
| difficulty | int | 否 | 难度筛选 1-5 |

**响应:** `201`

```json
{
  "session": {
    "id": "string",
    "user_id": "string",
    "title": "数学练习",
    "subject": "数学",
    "exercise_ids": "id1,id2,id3",
    "total_count": 5,
    "correct_count": 0,
    "score": 0,
    "status": "in_progress",
    "created_at": "datetime",
    "completed_at": null
  },
  "exercises": [
    {
      "id": "string",
      "type": "choice",
      "question": "string",
      "options": ["A. xxx"] | null,
      "difficulty": 3,
      "knowledge_point": "string | null"
    }
  ]
}
```

> 逻辑: 从题库中随机抽取指定学科的题目。若题库中符合条件的题目不足，返回 `400` 错误。

---

### 2.8 获取练习会话历史

```
GET /exercises/sessions/history/list
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| subject | string | 否 | 按学科筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应:** `200`

```json
{
  "total": 10,
  "items": [
    {
      "id": "string",
      "user_id": "string",
      "title": "数学练习",
      "subject": "数学",
      "exercise_ids": "id1,id2",
      "total_count": 5,
      "correct_count": 4,
      "score": 80,
      "status": "completed",
      "created_at": "datetime",
      "completed_at": "datetime | null"
    }
  ]
}
```

---

### 2.9 获取练习会话详情

```
GET /exercises/sessions/{session_id}
```

**响应:** `200`

```json
{
  "session": { "..." },
  "exercises": [
    { "id": "string", "type": "string", "question": "string", "options": [] | null, "difficulty": 3, "knowledge_point": "string | null" }
  ]
}
```

---

### 2.10 完成练习会话

```
POST /exercises/sessions/{session_id}/complete
```

**响应:** `200`

```json
{
  "session": { "..." },
  "summary": {
    "total": 5,
    "correct": 4,
    "wrong": 1,
    "score": 80
  }
}
```

> 逻辑: 统计该会话所有题目的答题记录，计算 `score = (correct / total) * 100`，将会话状态设为 `completed`。

---

## 3. 智能体 `/agents`

> 后端文件: `endpoints/agents.py` | 前端文件: `src/api/agent.ts` | 页面: `/agent`

### 3.1 获取智能体列表

```
GET /agents/
```

**响应:** `200`

```json
{
  "agents": [
    { "id": "profile_analyst", "name": "画像分析师", "description": "...", "status": "active", "tools": ["tool1", "tool2"] }
  ],
  "total": 6
}
```

---

### 3.2 获取智能体详情

```
GET /agents/{agent_id}
```

**响应:** `200` 返回智能体对象

---

### 3.3 向智能体发送查询

```
POST /agents/query
Content-Type: application/json
```

**请求体:**

```json
{
  "user_input": "帮我分析数学成绩",
  "user_id": "string",
  "session_id": "string"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_input | string | 是 | 用户输入的自然语言 |
| user_id | string | 是 | 用户 ID |
| session_id | string | 否 | 会话 ID（保持上下文） |

**响应:** `200`

```json
{
  "session_id": "string",
  "intent": "string",
  "result": {},
  "tasks_executed": 1,
  "timestamp": "datetime"
}
```

---

### 3.4 创建会话

```
POST /agents/sessions
```

**Query 参数:** `user_id` (必填)

**响应:** `200`

```json
{
  "session_id": "string",
  "user_id": "string",
  "task_count": 0,
  "conversation_history_count": 0,
  "created_at": "datetime",
  "last_active_at": "datetime"
}
```

---

### 3.5 获取会话信息

```
GET /agents/sessions/{session_id}
```

**响应:** `200` 同 3.4 响应格式

---

### 3.6 关闭会话

```
DELETE /agents/sessions/{session_id}
```

**响应:** `200`

```json
{ "message": "会话 xxx 已成功关闭" }
```

---

### 3.7 获取会话任务列表

```
GET /agents/sessions/{session_id}/tasks
```

**响应:** `200` 返回任务数组

---

### 3.8 意图识别

```
POST /agents/intent/recognize
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_input | string | 是 | 用户输入 |
| session_id | string | 否 | 会话 ID |
| user_id | string | 否 | 用户 ID |

**响应:** `200`

```json
{
  "intent_type": "string",
  "entities": {},
  "urgency": "low | medium | high",
  "preferred_agent": "string",
  "emotion_tag": "string",
  "raw_input": "string"
}
```

---

### 3.9 短期记忆

```
POST /agents/memory/short-term
```

**Query 参数:** `session_id` (必填)

**请求体:** `content` (JSON 对象)

**响应:** `200` `{ "message": "短期记忆添加成功" }`

```
GET /agents/memory/short-term/{session_id}
```

**响应:** `200` `{ "session_id": "string", "memory": {} }`

---

### 3.10 长期记忆

```
POST /agents/memory/long-term
```

**Query 参数:** `user_id`, `key`, `value` (均必填)

**响应:** `200` `{ "message": "长期记忆添加成功" }`

```
GET /agents/memory/long-term/{user_id}
```

**Query 参数:** `key` (可选，不传返回所有)

**响应:** `200` `{ "user_id": "string", "memory": {} }`

---

### 3.11 模型管理

```
GET /agents/models
```

**响应:** `200`

```json
{
  "models": [
    { "id": "string", "name": "string", "provider": "string", "description": "string", "available": true }
  ],
  "current_model": "string"
}
```

---

```
POST /agents/model/select
Content-Type: application/json
```

**请求体:**

```json
{
  "model_id": "string"
}
```

**响应:** `200`

```json
{
  "message": "string",
  "current_model": "string"
}
```

---

### 3.12 健康检查

```
GET /agents/health
```

**响应:** `200`

```json
{
  "status": "healthy",
  "agents_count": 6,
  "sessions_count": 0,
  "timestamp": "datetime"
}
```

---

## 4. 学习记录时间线 `/timeline`

> 后端文件: `endpoints/timeline.py` | 页面: `/records`

### 4.1 记录学习活动

```
POST /timeline/record
Content-Type: application/json
```

**请求体:**

```json
{
  "activity_type": "exercise",
  "target_id": "string",
  "title": "完成数学练习",
  "duration": 1800,
  "score": 85
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activity_type | string | 是 | `exercise` / `mistake_review` / `material_read` / `session_complete` |
| target_id | string | 否 | 关联目标 ID |
| title | string | 否 | 活动标题 |
| duration | int | 否 | 学习时长（秒），默认 0 |
| score | int | 否 | 得分 0-100 |

**响应:** `201`

```json
{
  "activity": { "id": "string", "user_id": "string", "activity_type": "string", "target_id": "string | null", "title": "string | null", "duration": 1800, "score": 85, "created_at": "datetime" },
  "unlocked_achievements": [
    { "achievement_id": "string", "name": "string", "description": "string", "icon": "string | null" }
  ]
}
```

---

### 4.2 获取学习记录时间线

```
GET /timeline
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activity_type | string | 否 | 按活动类型筛选 |
| start_date | date | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | date | 否 | 结束日期 (YYYY-MM-DD) |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20，最大 100 |

**响应:** `200`

```json
{
  "total": 100,
  "items": [
    { "id": "string", "user_id": "string", "activity_type": "string", "target_id": "string | null", "title": "string | null", "duration": 1800, "score": 85, "created_at": "datetime" }
  ]
}
```

---

### 4.3 获取每日学习统计

```
GET /timeline/stats/daily
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | date | 否 | 开始日期 |
| end_date | date | 否 | 结束日期 |

**响应:** `200`

```json
{
  "items": [
    { "date": "2026-07-10", "total_duration": 3600, "activity_count": 5 }
  ]
}
```

---

### 4.4 获取学习总览

```
GET /timeline/stats/overview
```

**响应:** `200`

```json
{
  "total_duration": 86400,
  "total_activities": 120,
  "streak_days": 7
}
```

---

### 4.5 获取连续学习天数

```
GET /timeline/streak
```

**响应:** `200`

```json
{
  "streak_days": 7,
  "last_study_date": "2026-07-10"
}
```

---

## 5. 成绩分析 `/analytics`

> 后端文件: `endpoints/analytics.py`

### 5.1 学习概览

```
GET /analytics/overview
```

**响应:** `200`

```json
{
  "total_exercises": 200,
  "correct_count": 160,
  "accuracy_rate": 80.0,
  "total_mistakes": 50,
  "unsolved_mistakes": 20,
  "streak_days": 7
}
```

---

### 5.2 各科成绩趋势

```
GET /analytics/subjects
```

**响应:** `200`

```json
{
  "items": [
    { "subject": "数学", "total_exercises": 80, "correct_count": 64, "accuracy_rate": 80.0 }
  ]
}
```

---

### 5.3 薄弱知识点分析

```
GET /analytics/weak-points
```

**响应:** `200` 按错误率降序排列

```json
{
  "items": [
    { "knowledge_point": "二次函数", "total_attempts": 20, "wrong_count": 12, "error_rate": 60.0 }
  ]
}
```

---

### 5.4 生成评估报告

```
POST /analytics/report/generate
```

**响应:** `200` (调用 LLM 生成)

```json
{
  "id": "string",
  "content": "报告正文（markdown 格式）",
  "created_at": "datetime"
}
```

---

### 5.5 获取最新评估报告

```
GET /analytics/report/latest
```

**响应:** `200` 同 5.4 格式。无报告时返回 `404`。

---

## 6. 其他模块路由一览

> 以下模块在 `router.py` 中已注册路由，前端尚未封装对应 API 文件。

| 模块 | 路由前缀 | 后端文件 | 说明 |
|------|----------|----------|------|
| 健康检查 | `/health` | `health.py` | 系统健康状态 |
| 用户认证 | `/auth` | `auth.py` | 登录/注册/Token |
| 知识库 | `/knowledge` | `knowledge.py` | 知识库管理 |
| 对话 | `/chat` | `chat.py` | 对话接口 |
| 思维导图 | `/mindmaps` | `mindmaps.py` | 思维导图生成 |
| 课堂互动 | `/classrooms` | `classroom.py` | 课堂功能 |
| 学习资料库 | `/study-materials` | `study_materials.py` | 学习资料 CRUD |
| 学习路径 | `/learning-paths` | `learning_paths.py` | 学习路径规划 |
| 收藏 | `/favorites` | `favorites.py` | 收藏功能 |
| 通知消息 | `/notifications` | `notifications.py` | 通知推送 |
| 成就系统 | `/achievements` | `achievements.py` | 成就管理 |
| 学习网站 | `/learning-websites` | `learning_websites.py` | 学习网站链接 |
| 外部数据 | `/external-data` | `external_data.py` | 外部数据源管理 |
| 图片识别 | `/image` | `image_recognition.py` | 图片 OCR 识别 |

---

## 附录：前端文件结构

```
src/api/
├── client.ts       # axios 实例（baseURL、Token 拦截器、401 处理）
├── agent.ts        # 智能体接口（含模型管理、记忆管理）
├── mistakes.ts     # 错题题库接口
└── exercises.ts    # 练习测试接口

src/pages/
├── Login.vue           # 登录页面
├── Dashboard.vue       # 首页仪表盘
├── Mistakes.vue        # 错题本页面
├── Exercises.vue       # 练习测试页面
├── MindMap.vue         # 思维导图页面（含科目筛选、10门课程数据）
├── Focus.vue           # 专注学习页面（全屏模式、防退出、计时器）
├── Notifications.vue   # 通知页面
├── Records.vue         # 学习记录页面
├── LearningPath.vue    # 学习路径页面
├── Resources.vue       # 学习资源页面
├── Classroom.vue       # 课堂页面
├── Achievements.vue    # 成就页面
└── Profile.vue         # 个人中心页面

src/layouts/
└── MainLayout.vue      # 主布局（侧边栏菜单）
```

---

## 前端修改文件清单

### ✅ 已修改的文件

| 文件路径 | 修改内容 | 优先级 |
|----------|----------|--------|
| `src/pages/MindMap.vue` | 添加科目筛选功能、10门课程数据、调整样式布局 | 高 |
| `src/pages/Focus.vue` | 添加全屏模式、防退出保护、倒计时显示、自定义时间输入 | 高 |
| `src/pages/Notifications.vue` | 修复图标导入错误（CheckCheck → CheckSquare） | 中 |
| `src/layouts/MainLayout.vue` | 添加"专注学习"菜单项 | 中 |
| `src/api/agent.ts` | 添加模型管理接口（getModels、selectModel） | 中 |
| `api.md` | 更新接口文档，添加模型管理接口说明 | 低 |

### 📋 需要推送到 GitHub 的文件

建议按以下顺序推送：

1. **API层（核心）**
   - `src/api/client.ts`
   - `src/api/agent.ts`
   - `src/api/mistakes.ts`
   - `src/api/exercises.ts`
   - `api.md`

2. **页面层（功能）**
   - `src/pages/MindMap.vue`
   - `src/pages/Focus.vue`
   - `src/pages/Notifications.vue`
   - `src/layouts/MainLayout.vue`

3. **其他页面（如需同步）**
   - `src/pages/Dashboard.vue`
   - `src/pages/Mistakes.vue`
   - `src/pages/Exercises.vue`
   - `src/pages/Records.vue`
   - `src/pages/LearningPath.vue`
   - `src/pages/Resources.vue`
   - `src/pages/Classroom.vue`
   - `src/pages/Achievements.vue`
   - `src/pages/Profile.vue`
   - `src/pages/Login.vue`
