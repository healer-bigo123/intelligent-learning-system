# 数据库设计详细说明文档

**文档版本：** v2.0  
**创建日期：** 2026年6月19日  
**适用项目：** 基于大模型的个性化资源生成与学习多智能体系统

---

## 一、数据库设计概述

### 1.1 设计目标

| 目标 | 描述 |
|------|------|
| **数据完整性** | 确保数据的准确性和一致性 |
| **性能优化** | 支持高效的查询和数据操作 |
| **可扩展性** | 支持未来功能扩展和数据增长 |
| **安全性** | 保护敏感数据，实现访问控制 |
| **规范性** | 遵循统一的数据类型和命名规范 |

### 1.2 数据库选型

| 数据库类型 | 技术 | 用途 |
|-----------|------|------|
| 关系型数据库 | SQLite | 主数据存储、业务逻辑 |
| 向量数据库 | Chroma/FAISS | 文档检索、语义搜索 |
| 缓存 | Redis（待集成） | 热点数据缓存、会话管理 |

### 1.3 设计原则

| 原则 | 说明 |
|------|------|
| **第三范式** | 数据规范化，减少冗余 |
| **主键唯一** | 每张表必须有唯一主键 |
| **外键约束** | 维护表间关系的完整性 |
| **索引优化** | 为常用查询字段创建索引 |
| **命名规范** | 表名小写下划线，字段名清晰描述 |

---

## 二、数据模型设计

### 2.1 整体数据模型图

```
用户模块                           学习模块                              智能体模块
┌──────────┐                     ┌──────────────┐                    ┌───────────┐
│  users   │ 1:N              N:1│learning_paths│ 1:N              N:1│agent_tasks│
├──────────┤<────────────────────>├──────────────┤<───────────────────>├───────────┤
│user_roles│                     │exercise_sessions│                  │           │
└──────────┘                     ├──────────────┤                    └───────────┘
                                 │   exercises  │ 1:N              N:1
                                 ├──────────────┤<──────────────────>┌───────────┐
                                 │exercise_records│                  │ mistakes  │
                                 ├──────────────┤                    └───────────┘
                                 │ study_activities│
                                 └──────────────┘

资源模块                           课堂模块                              通知模块
┌───────────────┐                 ┌───────────┐                     ┌───────────┐
│learning_resources│              │classrooms │ 1:N              N:1│notifications│
├───────────────┤                 ├───────────┤<───────────────────>├───────────┤
│study_materials│                 │classroom_ │                     │           │
├───────────────┤                 │  members  │                     └───────────┘
│ mind_maps     │                 ├───────────┤
└───────────────┘                 │  quizzes  │
                                  ├───────────┤
                                  │  votes    │
                                  ├───────────┤
                                  │ lotteries │
                                  └───────────┘

成就模块                           外部数据模块
┌───────────────┐                 ┌──────────────────┐
│achievements  │ 1:N          N:1│external_data     │
├───────────────┤<────────────────>│  records         │
│user_achievements│              └──────────────────┘
└───────────────┘
```

### 2.2 表结构详细设计

#### 2.2.1 用户模块表

##### 表：users（用户表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 用户唯一标识 | ✅ |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 | ✅ |
| email | VARCHAR(100) | UNIQUE | 邮箱地址 | ✅ |
| phone | VARCHAR(20) | UNIQUE | 手机号码 | ✅ |
| hashed_password | VARCHAR(255) | NOT NULL | 加密后的密码 | ❌ |
| nickname | VARCHAR(100) | | 昵称 | ❌ |
| avatar | VARCHAR(500) | | 头像URL | ❌ |
| role | VARCHAR(20) | DEFAULT 'student' | 角色：student/teacher/admin | ✅ |
| status | VARCHAR(20) | DEFAULT 'active' | 状态：active/inactive/banned | ✅ |
| last_login_at | DATETIME | | 最后登录时间 | ❌ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 | ❌ |

**索引策略：**
- PRIMARY KEY: id
- UNIQUE: username, email, phone
- INDEX: role, status, created_at

##### 表：user_roles（用户角色表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键 | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| role | VARCHAR(20) | NOT NULL | 角色名称 | ✅ |
| permissions | TEXT | DEFAULT '[]' | 权限列表(JSON) | ❌ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, role

#### 2.2.2 学习模块表

##### 表：learning_paths（学习路径表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 学习路径ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| title | VARCHAR(200) | NOT NULL | 路径标题 | ❌ |
| description | TEXT | | 路径描述 | ❌ |
| steps | TEXT | DEFAULT '[]' | 步骤列表(JSON) | ❌ |
| status | VARCHAR(20) | DEFAULT 'active' | 状态：active/completed/paused | ✅ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 | ❌ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, status, created_at

##### 表：exercises（练习题表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 练习题ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| subject | VARCHAR(100) | NOT NULL | 学科 | ✅ |
| type | VARCHAR(20) | NOT NULL | 题型 | ✅ |
| question | TEXT | NOT NULL | 题目内容 | ❌ |
| options | TEXT | | 选项(JSON) | ❌ |
| correct_answer | TEXT | NOT NULL | 正确答案 | ❌ |
| explanation | TEXT | | 答案解析 | ❌ |
| knowledge_point | VARCHAR(200) | | 知识点 | ✅ |
| difficulty | INTEGER | DEFAULT 3, CHECK(1-5) | 难度1-5 | ✅ |
| source | VARCHAR(50) | DEFAULT 'manual' | 来源 | ❌ |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 | ✅ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, subject, type, knowledge_point, difficulty, status

##### 表：exercise_records（答题记录表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 记录ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| exercise_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 题目ID | ✅ |
| user_answer | TEXT | | 用户答案 | ❌ |
| is_correct | BOOLEAN | DEFAULT FALSE | 是否正确 | ✅ |
| score | INTEGER | DEFAULT 0 | 得分 | ❌ |
| time_spent | INTEGER | DEFAULT 0 | 耗时(秒) | ❌ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE
- exercise_id REFERENCES exercises(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, exercise_id, is_correct, created_at

##### 表：exercise_sessions（练习会话表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 会话ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| title | VARCHAR(200) | | 会话标题 | ❌ |
| subject | VARCHAR(100) | NOT NULL | 学科 | ✅ |
| exercise_ids | TEXT | DEFAULT '' | 题目ID列表 | ❌ |
| total_count | INTEGER | DEFAULT 0 | 总题数 | ❌ |
| correct_count | INTEGER | DEFAULT 0 | 正确数 | ❌ |
| score | INTEGER | DEFAULT 0 | 总分 | ❌ |
| status | VARCHAR(20) | DEFAULT 'in_progress' | 状态 | ✅ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |
| completed_at | DATETIME | | 完成时间 | ❌ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, subject, status, created_at

##### 表：mistakes（错题本表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 错题ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| subject | VARCHAR(100) | NOT NULL | 学科 | ✅ |
| question | TEXT | NOT NULL | 题目内容 | ❌ |
| correct_answer | TEXT | NOT NULL | 正确答案 | ❌ |
| user_answer | TEXT | | 用户答案 | ❌ |
| analysis | TEXT | | 解析 | ❌ |
| knowledge_point | VARCHAR(200) | | 知识点 | ✅ |
| tags | TEXT | DEFAULT '' | 标签 | ❌ |
| source | VARCHAR(200) | | 来源 | ❌ |
| difficulty | INTEGER | DEFAULT 3, CHECK(1-5) | 难度 | ✅ |
| status | VARCHAR(20) | DEFAULT 'unsolved' | 状态 | ✅ |
| review_count | INTEGER | DEFAULT 0 | 复习次数 | ❌ |
| last_review_at | DATETIME | | 最后复习时间 | ❌ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 | ❌ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, subject, knowledge_point, status, created_at

##### 表：study_activities（学习活动表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 活动ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| activity_type | VARCHAR(50) | NOT NULL | 活动类型 | ✅ |
| target_id | VARCHAR(64) | | 目标ID | ❌ |
| title | VARCHAR(200) | | 标题 | ❌ |
| duration | INTEGER | DEFAULT 0 | 时长(秒) | ❌ |
| score | INTEGER | | 得分 | ❌ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, activity_type, created_at

#### 2.2.3 资源模块表

##### 表：learning_resources（学习资源表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 资源ID | ✅ |
| title | VARCHAR(200) | NOT NULL | 标题 | ❌ |
| type | VARCHAR(50) | NOT NULL | 类型 | ✅ |
| subject | VARCHAR(100) | | 学科 | ✅ |
| topics | TEXT | DEFAULT '' | 知识点 | ❌ |
| difficulty | INTEGER | DEFAULT 3 | 难度 | ✅ |
| duration | INTEGER | DEFAULT 0 | 时长(分钟) | ❌ |
| file_path | VARCHAR(500) | | 文件路径 | ❌ |
| content_text | TEXT | | 文本内容 | ❌ |
| generated_by | VARCHAR(50) | | 生成智能体 | ❌ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| rating | FLOAT | DEFAULT 0 | 评分 | ❌ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, type, subject, difficulty, created_at

##### 表：study_materials（学习资料表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 资料ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| title | VARCHAR(200) | NOT NULL | 标题 | ❌ |
| content | TEXT | NOT NULL | 内容 | ❌ |
| subject | VARCHAR(100) | NOT NULL | 学科 | ✅ |
| grade | VARCHAR(20) | | 年级 | ✅ |
| material_type | VARCHAR(50) | DEFAULT '知识点' | 类型 | ✅ |
| knowledge_point | VARCHAR(200) | | 知识点 | ✅ |
| tags | TEXT | DEFAULT '' | 标签 | ❌ |
| source | VARCHAR(200) | | 来源 | ❌ |
| difficulty | INTEGER | DEFAULT 3 | 难度 | ✅ |
| views | INTEGER | DEFAULT 0 | 浏览次数 | ❌ |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 | ✅ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 | ❌ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, subject, grade, material_type, knowledge_point, status

##### 表：mind_maps（思维导图表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 思维导图ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| title | VARCHAR(200) | NOT NULL | 标题 | ❌ |
| subject | VARCHAR(100) | NOT NULL | 学科 | ✅ |
| content | TEXT | DEFAULT '{}' | 内容(JSON) | ❌ |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 | ✅ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 | ❌ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, subject, status, created_at

#### 2.2.4 课堂模块表

##### 表：classrooms（课堂表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 课堂ID | ✅ |
| code | VARCHAR(6) | UNIQUE, NOT NULL | 课堂码 | ✅ |
| name | VARCHAR(200) | NOT NULL | 名称 | ❌ |
| description | TEXT | | 描述 | ❌ |
| teacher_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 教师ID | ✅ |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 | ✅ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 | ❌ |

**外键约束：**
- teacher_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- UNIQUE: code
- INDEX: teacher_id, status, created_at

##### 表：classroom_members（课堂成员表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 成员ID | ✅ |
| classroom_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 课堂ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| role | VARCHAR(20) | DEFAULT 'student' | 角色 | ✅ |
| joined_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 加入时间 | ✅ |

**外键约束：**
- classroom_id REFERENCES classrooms(id) ON DELETE CASCADE
- user_id REFERENCES users(id) ON DELETE CASCADE

**唯一约束：** (classroom_id, user_id)

**索引策略：**
- PRIMARY KEY: id
- INDEX: classroom_id, user_id, role

#### 2.2.5 其他表

##### 表：student_profiles（学生画像表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY, FOREIGN KEY | 用户ID | ✅ |
| name | VARCHAR(100) | | 姓名 | ❌ |
| grade | VARCHAR(20) | | 年级 | ✅ |
| major | VARCHAR(100) | | 专业 | ✅ |
| target | VARCHAR(100) | | 目标 | ❌ |
| dimensions | TEXT | DEFAULT '{}' | 画像维度(JSON) | ❌ |
| knowledge_state | TEXT | DEFAULT '{}' | 知识状态(JSON) | ❌ |
| weak_points | TEXT | DEFAULT '' | 薄弱知识点 | ❌ |
| interests | TEXT | DEFAULT '' | 兴趣标签 | ❌ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 | ❌ |

**外键约束：**
- id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: grade, major, created_at

##### 表：notifications（通知表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 通知ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| title | VARCHAR(200) | NOT NULL | 标题 | ❌ |
| content | TEXT | NOT NULL | 内容 | ❌ |
| type | VARCHAR(50) | DEFAULT 'system' | 类型 | ✅ |
| is_read | BOOLEAN | DEFAULT FALSE | 是否已读 | ✅ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, type, is_read, created_at

##### 表：achievements（成就表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 成就ID | ✅ |
| name | VARCHAR(100) | NOT NULL | 成就名称 | ❌ |
| description | TEXT | NOT NULL | 描述 | ❌ |
| icon | VARCHAR(200) | | 图标 | ❌ |
| condition_type | VARCHAR(50) | NOT NULL | 条件类型 | ✅ |
| condition_value | INTEGER | NOT NULL | 条件值 | ❌ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |

**索引策略：**
- PRIMARY KEY: id
- INDEX: condition_type

##### 表：user_achievements（用户成就表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 记录ID | ✅ |
| user_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 用户ID | ✅ |
| achievement_id | VARCHAR(64) | NOT NULL, FOREIGN KEY | 成就ID | ✅ |
| unlocked_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 解锁时间 | ✅ |

**外键约束：**
- user_id REFERENCES users(id) ON DELETE CASCADE
- achievement_id REFERENCES achievements(id) ON DELETE CASCADE

**唯一约束：** (user_id, achievement_id)

**索引策略：**
- PRIMARY KEY: id
- INDEX: user_id, achievement_id

#### 2.2.6 新增外部数据表

##### 表：external_data_records（外部数据表）

| 字段名 | 类型 | 约束 | 说明 | 索引 |
|--------|------|------|------|------|
| id | VARCHAR(64) | PRIMARY KEY | 记录ID | ✅ |
| source_id | VARCHAR(64) | NOT NULL | 数据源ID | ✅ |
| data_type | VARCHAR(50) | NOT NULL | 数据类型 | ✅ |
| data | TEXT | NOT NULL | 数据(JSON) | ❌ |
| title | VARCHAR(200) | | 标题 | ❌ |
| subject | VARCHAR(100) | | 学科 | ✅ |
| knowledge_point | VARCHAR(200) | | 知识点 | ✅ |
| is_active | BOOLEAN | DEFAULT TRUE | 是否有效 | ✅ |
| sync_time | DATETIME | | 同步时间 | ✅ |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | ✅ |

**索引策略：**
- PRIMARY KEY: id
- INDEX: source_id, data_type, subject, knowledge_point, is_active

---

## 三、数据类型规范

### 3.1 基础类型规范

| 数据类型 | SQLite类型 | 说明 | 示例 |
|---------|-----------|------|------|
| 字符串 | VARCHAR(n) | 固定长度字符串，n为最大长度 | VARCHAR(50) |
| 长文本 | TEXT | 无长度限制的文本 | TEXT |
| 整数 | INTEGER | 整数类型 | INTEGER |
| 浮点数 | FLOAT | 浮点数 | FLOAT |
| 布尔 | BOOLEAN | 布尔值(0/1) | BOOLEAN |
| 日期时间 | DATETIME | 日期时间 | DATETIME |

### 3.2 长度规范

| 字段类型 | 推荐长度 | 说明 |
|---------|---------|------|
| ID字段 | 64 | UUID格式 |
| 用户名 | 50 | 用户名/昵称 |
| 邮箱 | 100 | 邮箱地址 |
| 手机号 | 20 | 包含国际区号 |
| 标题 | 200 | 资源/文章标题 |
| 标签 | 200 | 知识点/标签 |

### 3.3 命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写+下划线，复数 | users, study_activities |
| 字段名 | 小写+下划线 | user_id, created_at |
| 外键 | 关联表名_id | user_id, classroom_id |
| 主键 | id | id |

---

## 四、关系设计

### 4.1 关系类型

| 关系 | 说明 | 示例 |
|------|------|------|
| 1:N | 一对多 | user -> mistakes |
| N:1 | 多对一 | mistakes -> user |
| N:N | 多对多 | user <-> classroom (通过classroom_members) |
| 1:1 | 一对一 | user -> student_profile |

### 4.2 外键约束规则

```sql
-- ON DELETE CASCADE: 删除父记录时级联删除子记录
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

-- ON UPDATE CASCADE: 更新父记录时级联更新子记录
FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE

-- ON DELETE SET NULL: 删除父记录时设置为NULL
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
```

### 4.3 约束类型

| 约束 | 说明 | 应用场景 |
|------|------|---------|
| PRIMARY KEY | 主键 | 唯一标识记录 |
| UNIQUE | 唯一 | 邮箱、手机号、用户名 |
| NOT NULL | 非空 | 必填字段 |
| CHECK | 检查 | 难度范围1-5 |
| DEFAULT | 默认值 | status、created_at |

---

## 五、索引策略

### 5.1 索引设计原则

| 原则 | 说明 |
|------|------|
| 主键自动索引 | 主键字段自动创建索引 |
| 外键创建索引 | 外键字段应创建索引 |
| 常用查询字段 | WHERE、JOIN、ORDER BY中的字段 |
| 复合索引 | 经常一起查询的字段组合 |
| 避免过度索引 | 索引会降低写入性能 |

### 5.2 索引优先级

| 优先级 | 字段类型 | 说明 |
|--------|---------|------|
| P0 | 主键 | 必须索引 |
| P0 | 外键 | 必须索引 |
| P1 | 查询条件字段 | WHERE子句 |
| P1 | 排序字段 | ORDER BY |
| P2 | 过滤字段 | status、is_active |
| P3 | 时间字段 | created_at、updated_at |

### 5.3 复合索引示例

```sql
-- 用户查询
CREATE INDEX idx_users_role_status ON users(role, status);

-- 错题查询
CREATE INDEX idx_mistakes_user_subject_status ON mistakes(user_id, subject, status);

-- 练习记录
CREATE INDEX idx_records_user_correct_time ON exercise_records(user_id, is_correct, created_at);
```

---

## 六、数据库操作规范

### 6.1 连接配置

```python
# SQLite连接配置
DATABASE_URL = "sqlite:///./data/smart_learning.db"

# 连接参数
connect_args = {
    "check_same_thread": False,  # SQLite线程安全
    "timeout": 30,               # 超时时间
}

# 启用外键约束
PRAGMA foreign_keys = ON;
```

### 6.2 事务管理

```python
# 事务示例
def safe_operation(db):
    try:
        # 开始事务（自动）
        # 执行操作
        db.add(record)
        db.commit()
    except Exception as e:
        # 回滚事务
        db.rollback()
        raise
    finally:
        # 关闭连接
        db.close()
```

### 6.3 查询优化

| 优化项 | 说明 |
|--------|------|
| LIMIT | 分页查询使用LIMIT |
| 避免SELECT * | 只查询需要的字段 |
| 批量操作 | 使用批量插入/更新 |
| 缓存热点数据 | 使用Redis缓存 |

---

## 七、安全规范

### 7.1 数据保护

| 措施 | 说明 |
|------|------|
| 密码加密 | 使用bcrypt加密存储 |
| 敏感数据脱敏 | 日志中不记录密码、手机号 |
| 最小权限 | 数据库用户只授予必要权限 |
| 连接安全 | 使用SSL/TLS（生产环境） |

### 7.2 输入验证

| 验证项 | 说明 |
|--------|------|
| SQL注入 | 使用ORM参数化查询 |
| 长度限制 | 前端+后端双重验证 |
| 格式验证 | 邮箱、手机号格式 |
| 特殊字符 | 过滤危险字符 |

---

## 八、测试验证

### 8.1 完整性检查

```sql
-- 运行完整性检查
PRAGMA integrity_check;

-- 检查外键
PRAGMA foreign_key_check;

-- 检查索引
PRAGMA index_list(table_name);
```

### 8.2 性能测试

| 测试项 | 方法 |
|--------|------|
| 查询性能 | EXPLAIN QUERY PLAN |
| 并发测试 | 模拟多用户请求 |
| 数据量测试 | 大规模数据插入 |

### 8.3 功能测试

| 模块 | 测试点 |
|------|------|
| 用户管理 | 注册、登录、权限 |
| 学习路径 | 创建、更新、完成 |
| 练习系统 | 答题、批改、统计 |
| 错题本 | 收集、复习、掌握 |
| 资源管理 | 生成、搜索、评分 |

---

## 九、备份与恢复

### 9.1 备份策略

| 频率 | 类型 | 说明 |
|------|------|------|
| 每日 | 增量备份 | 记录当日变更 |
| 每周 | 全量备份 | 完整数据库备份 |
| 事件触发 | 重要操作后 | 如数据迁移 |

### 9.2 备份命令

```bash
# SQLite备份
sqlite3 data/smart_learning.db ".backup data/backups/smart_learning_backup.db"

# 定时任务（crontab示例）
0 2 * * * sqlite3 /app/data/smart_learning.db ".backup /app/data/backups/backup_$(date +\%Y\%m\%d).db"
```

### 9.3 恢复命令

```bash
# SQLite恢复
sqlite3 data/smart_learning.db ".restore data/backups/smart_learning_backup.db"
```

---

## 十、设计检查清单

### 10.1 表设计检查

- [ ] 每张表都有主键
- [ ] 外键约束完整
- [ ] 索引策略合理
- [ ] 数据类型正确
- [ ] 命名规范统一

### 10.2 关系设计检查

- [ ] 关系类型正确
- [ ] 级联操作合理
- [ ] 多对多关系使用中间表
- [ ] 避免循环依赖

### 10.3 安全检查

- [ ] 密码加密存储
- [ ] 敏感数据保护
- [ ] SQL注入防护
- [ ] 输入验证完善

### 10.4 性能检查

- [ ] 查询字段有索引
- [ ] 避免全表扫描
- [ ] 批量操作优化
- [ ] 缓存策略合理

---

**文档审核：** _______________  
**审核日期：** _______________