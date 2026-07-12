# 外部数据源集成方案文档

## 一、项目数据库现状分析

### 1.1 数据库类型与结构

当前项目使用 **SQLite** 作为主数据库，配合 **Chroma/FAISS** 向量数据库存储文档和知识。

### 1.2 现有数据表清单

| 序号 | 表名 | 记录数 | 用途 |
|------|------|-------|------|
| 1 | `users` | 27 | 用户基础信息 |
| 2 | `user_roles` | 27 | 用户角色权限 |
| 3 | `student_profiles` | 0 | 学生画像 |
| 4 | `learning_paths` | 4 | 学习路径 |
| 5 | `learning_resources` | 0 | 学习资源 |
| 6 | `exercises` | 未知 | 练习题 |
| 7 | `exercise_records` | 未知 | 答题记录 |
| 8 | `exercise_sessions` | 未知 | 练习会话 |
| 9 | `mistakes` | 4 | 错题本 |
| 10 | `chat_sessions` | 0 | 对话会话 |
| 11 | `chat_messages` | 0 | 对话消息 |
| 12 | `mind_maps` | 未知 | 思维导图 |
| 13 | `study_materials` | 未知 | 学习资料 |
| 14 | `classrooms` | 未知 | 课堂 |
| 15 | `classroom_members` | 未知 | 课堂成员 |
| 16 | `favorites` | 未知 | 收藏 |
| 17 | `notifications` | 未知 | 通知 |
| 18 | `study_activities` | 未知 | 学习活动 |
| 19 | `achievements` | 未知 | 成就 |
| 20 | `user_achievements` | 未知 | 用户成就 |
| 21 | `agent_tasks` | 0 | 智能体任务 |
| 22 | `learning_websites` | 未知 | 学习网站 |
| 23 | `assessment_reports` | 未知 | 评估报告 |
| 24 | `votes` | 未知 | 投票 |
| 25 | `lotteries` | 未知 | 抽签 |
| 26 | `quizzes` | 未知 | 随堂测验 |

### 1.3 数据来源说明

| 数据类型 | 存储位置 | 来源说明 |
|---------|---------|---------|
| 用户数据 | `users`, `user_roles` | 系统注册/创建 |
| 学习行为 | `study_activities`, `exercise_records` | 用户操作产生 |
| 学习资源 | `learning_resources`, `study_materials` | 本地创建/AI生成 |
| 错题数据 | `mistakes` | 用户错题收集 |
| **外部数据** | 暂未存储 | **待从外部数据源获取** |

---

## 二、外部数据源集成方案

### 2.1 架构设计

```
┌─────────────────────────────────────────────────────────────────────┐
│                        外部数据源集成层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ 教育API源    │  │ 外部题库源   │  │ 学习平台源   │  ...          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                      │
│         ▼                 ▼                 ▼                      │
│  ┌──────────────────────────────────────────────┐                  │
│  │           数据源管理器 (DataSourceManager)    │                  │
│  │  - 配置管理    - 连接池    - 认证管理    - 同步调度  │            │
│  └──────────────────┬───────────────────────────┘                  │
│                     │                                              │
│                     ▼                                              │
│  ┌──────────────────────────────────────────────┐                  │
│  │              统一数据访问接口                  │                  │
│  │  - search_all()    - fetch_data()    - sync()  │                │
│  └──────────────────┬───────────────────────────┘                  │
│                     │                                              │
└─────────────────────┼───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        内部业务系统                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ 本地数据库   │  │ 向量数据库   │  │ 业务逻辑层   │              │
│  │ (SQLite)    │  │ (Chroma)     │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件说明

| 组件 | 职责 | 实现文件 |
|------|------|---------|
| `DataSourceConfig` | 数据源配置模型 | `app/core/external_data.py` |
| `ExternalDataSource` | 数据源抽象基类 | `app/core/external_data.py` |
| `AuthHandler` | 认证处理器基类 | `app/core/external_data.py` |
| `DataSourceManager` | 数据源管理器 | `app/core/external_data.py` |
| `external_data.py` | REST API接口 | `app/api/v1/endpoints/external_data.py` |

### 2.3 支持的数据源类型

| 类型 | 枚举值 | 说明 | 典型用途 |
|------|-------|------|---------|
| 教育数据API | `education_api` | 教育领域标准化API | 知识点、课程数据 |
| 知识库 | `knowledge_base` | 专业知识库 | 文档检索、知识问答 |
| 外部题库 | `exercise_bank` | 专业题库API | 习题获取、试卷生成 |
| 学习平台 | `learning_platform` | 第三方学习平台 | 课程同步、资源导入 |
| 自定义API | `custom_api` | 自定义数据源 | 特殊需求扩展 |

### 2.4 支持的认证方式

| 认证类型 | 枚举值 | 说明 | 配置要求 |
|---------|-------|------|---------|
| 无需认证 | `none` | 公开接口 | 无 |
| API密钥 | `api_key` | 请求头携带密钥 | `api_key`, `header_name` |
| OAuth2 | `oauth2` | OAuth2.0协议 | `token_url`, `client_id`, `client_secret` |
| 基础认证 | `basic` | 用户名密码 | `username`, `password` |
| Bearer Token | `bearer_token` | Token认证 | `token` 或 `token_url` |
| 自定义 | `custom` | 自定义逻辑 | `auth_function` |

### 2.5 数据同步策略

| 策略 | 枚举值 | 说明 | 适用场景 |
|------|-------|------|---------|
| 手动同步 | `manual` | 需手动触发 | 低频更新数据 |
| 定时同步 | `scheduled` | 按间隔自动同步 | 定期更新数据 |
| 实时同步 | `realtime` | 事件驱动同步 | 高实时性需求 |
| 按需同步 | `on_demand` | 请求时触发 | 低频访问数据 |

---

## 三、数据接口设计

### 3.1 接口列表

| HTTP方法 | 路径 | 功能 | 说明 |
|---------|------|------|------|
| POST | `/external-data` | 创建数据源配置 | 注册新的外部数据源 |
| GET | `/external-data` | 获取数据源列表 | 支持按类型/状态筛选 |
| GET | `/external-data/{id}` | 获取数据源详情 | 获取单个数据源配置 |
| PUT | `/external-data/{id}` | 更新数据源配置 | 修改已有配置 |
| DELETE | `/external-data/{id}` | 删除数据源配置 | 注销数据源 |
| POST | `/external-data/{id}/enable` | 启用数据源 | 启用已禁用的数据源 |
| POST | `/external-data/{id}/disable` | 禁用数据源 | 暂停使用数据源 |
| POST | `/external-data/{id}/sync` | 同步指定数据源 | 手动触发同步 |
| POST | `/external-data/sync-all` | 同步所有数据源 | 批量同步 |
| GET | `/external-data/{id}/sync-history` | 获取同步历史 | 查看同步记录 |
| POST | `/external-data/search` | 搜索外部数据 | 跨数据源搜索 |
| GET | `/external-data/{id}/fetch` | 获取原始数据 | 直接调用API |
| GET | `/external-data/status` | 获取状态概览 | 所有数据源状态 |
| GET | `/external-data/stats` | 获取统计信息 | 同步统计 |

### 3.2 数据模型定义

#### 3.2.1 数据源配置

```json
{
  "id": "uuid-string",
  "name": "数据源名称",
  "type": "education_api|exercise_bank|learning_platform|custom_api",
  "base_url": "https://api.example.com",
  "auth_type": "none|api_key|oauth2|basic|bearer_token|custom",
  "auth_config": {
    "api_key": "your-api-key",
    "header_name": "X-API-Key"
  },
  "sync_strategy": "manual|scheduled|realtime|on_demand",
  "sync_interval": 3600,
  "enabled": true,
  "description": "数据源描述",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### 3.2.2 同步记录

```json
{
  "id": "sync-record-id",
  "source_id": "data-source-id",
  "sync_type": "knowledge|exercises|courses|custom",
  "status": "pending|running|success|failed|partial",
  "total_records": 100,
  "success_count": 95,
  "failed_count": 5,
  "error_message": "错误信息（如有）",
  "started_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:01:00"
}
```

#### 3.2.3 搜索结果

```json
{
  "id": "item-id",
  "title": "项目标题",
  "content": "内容摘要...",
  "type": "question|material|course",
  "subject": "数学|英语|物理",
  "source_id": "data-source-id",
  "source_name": "数据源名称",
  "extra": {
    "原始数据字段": "值"
  }
}
```

---

## 四、身份验证机制

### 4.1 认证流程

```
客户端请求 → 认证处理器 → 获取凭证 → 附加到请求头 → 发送请求 → 响应结果
     │              │              │              │
     │              ▼              ▼              │
     │       选择认证类型    执行认证逻辑         │
     │       (AuthType)      (authenticate)     │
     │                                            │
     └────────────────────────────────────────────┘
```

### 4.2 认证处理器实现

| 认证类型 | 处理器类 | 实现逻辑 |
|---------|---------|---------|
| `none` | `NoAuthHandler` | 无认证处理 |
| `api_key` | `ApiKeyAuthHandler` | 在请求头中添加API Key |
| `oauth2` | `BearerTokenAuthHandler` | 获取并刷新OAuth2 Token |
| `basic` | `BasicAuthHandler` | HTTP基础认证 |
| `bearer_token` | `BearerTokenAuthHandler` | Bearer Token认证 |
| `custom` | `CustomAuthHandler` | 自定义认证函数 |

### 4.3 令牌缓存策略

- **Token过期检测**：每次请求前检查Token是否过期
- **自动刷新机制**：过期前60秒自动刷新
- **缓存存储**：使用字典存储在内存中
- **线程安全**：单例模式管理

---

## 五、数据同步策略

### 5.1 同步流程

```
触发同步 → 创建同步记录 → 调用数据源API → 处理返回数据 → 更新同步状态 → 记录结果
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
  手动/定时    生成记录ID    带认证请求    解析转换数据    更新成功/失败
                                       │
                                       ▼
                          保存到本地数据库/向量库
```

### 5.2 同步间隔配置

| 数据源类型 | 默认间隔 | 建议范围 |
|-----------|---------|---------|
| 教育API | 1小时 | 30分钟-4小时 |
| 题库 | 2小时 | 1小时-8小时 |
| 学习平台 | 4小时 | 2小时-24小时 |
| 自定义 | 1小时 | 可自定义 |

### 5.3 增量同步支持

```python
# 支持按时间戳增量同步
def sync_data(self, force=False, since=None):
    """
    同步数据
    :param force: 是否强制全量同步
    :param since: 增量同步起始时间
    """
    params = {}
    if since and not force:
        params['since'] = since.isoformat()
    
    data = self.fetch_data('/sync', params=params)
    return self._process_data(data)
```

---

## 六、错误处理流程

### 6.1 错误类型定义

| 错误类型 | 异常类 | HTTP状态码 | 说明 |
|---------|-------|-----------|------|
| 通用错误 | `ExternalDataError` | 500 | 外部数据访问失败 |
| 数据源不存在 | `DataSourceNotFoundError` | 404 | 数据源配置不存在 |
| 认证失败 | `AuthenticationError` | 401 | 身份验证失败 |
| 同步失败 | `SyncError` | 500 | 数据同步失败 |
| 请求超限 | `RateLimitError` | 429 | API请求频率超限 |

### 6.2 错误处理流程

```
请求开始 → 执行操作 → 捕获异常 → 记录日志 → 返回错误响应
     │              │              │              │
     │              ▼              ▼              ▼
     │        检测错误类型    记录详细信息    构造错误响应
     │                                         │
     └─────────────────────────────────────────┘
```

### 6.3 重试机制

使用 `tenacity` 库实现自动重试：

```python
@retry(
    stop=stop_after_attempt(3),           # 最多重试3次
    wait=wait_exponential(multiplier=1,   # 指数退避
                          min=2, 
                          max=10),
    retry=retry_if_exception_type(ExternalDataError)  # 仅对特定异常重试
)
def sync_data(self, force=False):
    # 同步逻辑
    pass
```

### 6.4 熔断机制

```python
# 简化的熔断逻辑
class CircuitBreaker:
    def __init__(self, max_failures=5, reset_timeout=60):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure = None
        self.state = "closed"  # closed / open / half_open
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if (datetime.now() - self.last_failure).seconds > self.reset_timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerError("熔断器已打开")
        
        try:
            result = func(*args, **kwargs)
            self.failures = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = datetime.now()
            if self.failures >= self.max_failures:
                self.state = "open"
            raise
```

---

## 七、数据存储区分

### 7.1 数据来源标识

所有从外部获取的数据都需要标记来源：

| 字段 | 类型 | 说明 |
|------|------|------|
| `source_id` | String | 数据源ID |
| `source_name` | String | 数据源名称 |
| `is_external` | Boolean | 是否外部数据（true=外部，false=本地） |
| `sync_time` | DateTime | 同步时间 |

### 7.2 本地与外部数据对比

| 特性 | 本地数据 | 外部数据 |
|------|---------|---------|
| 存储位置 | 本地数据库 | 外部API |
| 数据更新 | 用户操作/AI生成 | 外部系统更新 |
| 同步方式 | 实时写入 | 定时/手动同步 |
| 数据所有权 | 本系统 | 外部系统 |
| 数据一致性 | 强一致 | 最终一致 |
| 访问方式 | 直接查询 | API调用 |

### 7.3 数据存储策略

```python
# 外部数据存储模型设计
class ExternalDataRecord(Base):
    """外部数据记录表"""
    __tablename__ = "external_data_records"
    
    id = Column(String(64), primary_key=True)
    source_id = Column(String(64), index=True)  # 来源数据源ID
    data_type = Column(String(50))              # 数据类型
    data = Column(Text)                         # 原始数据（JSON）
    title = Column(String(200))                 # 标题（用于搜索）
    subject = Column(String(100))               # 学科
    knowledge_point = Column(String(200))       # 知识点
    is_active = Column(Boolean, default=True)   # 是否有效
    sync_time = Column(DateTime)                # 同步时间
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 八、使用示例

### 8.1 注册数据源

```bash
curl -X POST http://localhost:8000/api/v1/external-data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "高考题库",
    "type": "exercise_bank",
    "base_url": "https://api.gaokao.com",
    "auth_type": "api_key",
    "auth_config": {
      "api_key": "your-secret-key",
      "header_name": "X-Token"
    },
    "sync_strategy": "scheduled",
    "sync_interval": 7200,
    "description": "高考真题题库"
  }'
```

### 8.2 同步数据源

```bash
curl -X POST "http://localhost:8000/api/v1/external-data/<source-id>/sync?force=true" \
  -H "Authorization: Bearer <token>"
```

### 8.3 搜索外部数据

```bash
curl -X POST http://localhost:8000/api/v1/external-data/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "三角函数",
    "filters": {
      "subject": "数学",
      "difficulty": 3
    },
    "source_ids": ["source-1", "source-2"]
  }'
```

### 8.4 获取同步状态

```bash
curl -X GET http://localhost:8000/api/v1/external-data/status \
  -H "Authorization: Bearer <token>"
```

---

## 九、代码实现文件清单

| 文件路径 | 说明 | 状态 |
|---------|------|------|
| `app/core/external_data.py` | 核心数据源管理模块 | ✅ 已实现 |
| `app/api/v1/endpoints/external_data.py` | REST API接口 | ✅ 已实现 |
| `app/api/v1/router.py` | 路由注册 | ✅ 已更新 |
| `docs/external_data_integration.md` | 集成文档 | ✅ 本文件 |

---

## 十、安全与性能建议

### 10.1 安全注意事项

1. **敏感信息保护**：API Key等凭证不应记录在日志中
2. **HTTPS强制**：外部API调用必须使用HTTPS
3. **请求频率限制**：实现客户端限流
4. **输入验证**：对所有输入参数进行验证
5. **异常信息脱敏**：对外返回的错误信息不应包含敏感数据

### 10.2 性能优化建议

1. **连接池复用**：使用`requests.Session`复用连接
2. **异步请求**：支持异步批量获取数据
3. **数据缓存**：缓存高频访问的静态数据
4. **批量同步**：支持批量获取和写入数据
5. **超时设置**：为每个请求设置合理超时时间

---

## 十一、未来扩展计划

### 11.1 功能扩展

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 异步同步 | 使用Celery实现异步任务 | P0 |
| Webhook支持 | 支持外部系统主动推送数据 | P1 |
| 多数据源联合查询 | 跨数据源复杂查询 | P1 |
| 数据质量监控 | 监控数据同步成功率 | P2 |
| 自动重试失败任务 | 失败记录自动重试 | P2 |

### 11.2 技术升级

| 升级项 | 说明 | 时间计划 |
|-------|------|---------|
| 配置持久化 | 将数据源配置存储到数据库 | 近期 |
| 分布式缓存 | 使用Redis替代内存缓存 | 中期 |
| 消息队列 | 使用RabbitMQ解耦同步任务 | 中期 |
| 多区域部署 | 支持多区域数据源 | 长期 |