# 数据库全面检查报告

检查时间: 2026-06-19 16:59:40
数据库路径: C:\Users\admin\Desktop\plan\backend\data\smart_learning.db

---

## 一、数据库连接状态

| 项目 | 状态 |
|------|------|
| 连接状态 | 成功 |
| 连接耗时 | 0.51 ms |
| 数据库大小 | 0.41 MB |

## 二、表结构统计

总表数: 26

| 表名 | 记录数 | 字段数 | 索引数 | 主键 |
|------|-------|--------|--------|------|
| achievements | 错误 | near ",": syntax error | - | - |
| agent_tasks | 错误 | near ",": syntax error | - | - |
| assessment_reports | 错误 | near ",": syntax error | - | - |
| chat_messages | 错误 | near ",": syntax error | - | - |
| chat_sessions | 错误 | near ",": syntax error | - | - |
| classroom_members | 错误 | near ",": syntax error | - | - |
| classrooms | 错误 | near ",": syntax error | - | - |
| exercise_records | 错误 | near ",": syntax error | - | - |
| exercise_sessions | 错误 | near ",": syntax error | - | - |
| exercises | 错误 | near ",": syntax error | - | - |
| favorites | 错误 | near ",": syntax error | - | - |
| learning_paths | 错误 | near ",": syntax error | - | - |
| learning_resources | 错误 | near ",": syntax error | - | - |
| learning_websites | 错误 | near ",": syntax error | - | - |
| lotteries | 错误 | near ",": syntax error | - | - |
| mind_maps | 错误 | near ",": syntax error | - | - |
| mistakes | 错误 | near ",": syntax error | - | - |
| notifications | 错误 | near ",": syntax error | - | - |
| quizzes | 错误 | near ",": syntax error | - | - |
| student_profiles | 错误 | near ",": syntax error | - | - |
| study_activities | 错误 | near ",": syntax error | - | - |
| study_materials | 错误 | near ",": syntax error | - | - |
| user_achievements | 错误 | near ",": syntax error | - | - |
| user_roles | 错误 | near ",": syntax error | - | - |
| users | 错误 | near ",": syntax error | - | - |
| votes | 错误 | near ",": syntax error | - | - |

## 三、问题发现

发现问题总数: 28

### 高 (1个)

#### 1. 未找到数据库备份

描述: 在备份目录中未发现任何备份文件

建议: 立即执行数据库备份，建立定期备份计划

### 中 (27个)

#### 1. 表 achievements 缺少主键

描述: 表 achievements 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 achievements 添加主键字段

#### 2. 表 agent_tasks 缺少主键

描述: 表 agent_tasks 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 agent_tasks 添加主键字段

#### 3. 表 assessment_reports 缺少主键

描述: 表 assessment_reports 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 assessment_reports 添加主键字段

#### 4. 表 chat_messages 缺少主键

描述: 表 chat_messages 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 chat_messages 添加主键字段

#### 5. 表 chat_sessions 缺少主键

描述: 表 chat_sessions 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 chat_sessions 添加主键字段

#### 6. 表 classroom_members 缺少主键

描述: 表 classroom_members 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 classroom_members 添加主键字段

#### 7. 表 classrooms 缺少主键

描述: 表 classrooms 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 classrooms 添加主键字段

#### 8. 表 exercise_records 缺少主键

描述: 表 exercise_records 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 exercise_records 添加主键字段

#### 9. 表 exercise_sessions 缺少主键

描述: 表 exercise_sessions 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 exercise_sessions 添加主键字段

#### 10. 表 exercises 缺少主键

描述: 表 exercises 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 exercises 添加主键字段

#### 11. 表 favorites 缺少主键

描述: 表 favorites 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 favorites 添加主键字段

#### 12. 表 learning_paths 缺少主键

描述: 表 learning_paths 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 learning_paths 添加主键字段

#### 13. 表 learning_resources 缺少主键

描述: 表 learning_resources 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 learning_resources 添加主键字段

#### 14. 表 learning_websites 缺少主键

描述: 表 learning_websites 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 learning_websites 添加主键字段

#### 15. 表 lotteries 缺少主键

描述: 表 lotteries 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 lotteries 添加主键字段

#### 16. 表 mind_maps 缺少主键

描述: 表 mind_maps 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 mind_maps 添加主键字段

#### 17. 表 mistakes 缺少主键

描述: 表 mistakes 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 mistakes 添加主键字段

#### 18. 表 notifications 缺少主键

描述: 表 notifications 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 notifications 添加主键字段

#### 19. 表 quizzes 缺少主键

描述: 表 quizzes 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 quizzes 添加主键字段

#### 20. 表 student_profiles 缺少主键

描述: 表 student_profiles 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 student_profiles 添加主键字段

#### 21. 表 study_activities 缺少主键

描述: 表 study_activities 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 study_activities 添加主键字段

#### 22. 表 study_materials 缺少主键

描述: 表 study_materials 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 study_materials 添加主键字段

#### 23. 表 user_achievements 缺少主键

描述: 表 user_achievements 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 user_achievements 添加主键字段

#### 24. 表 user_roles 缺少主键

描述: 表 user_roles 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 user_roles 添加主键字段

#### 25. 表 users 缺少主键

描述: 表 users 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 users 添加主键字段

#### 26. 表 votes 缺少主键

描述: 表 votes 没有定义主键约束，可能影响数据完整性和查询性能

建议: 为表 votes 添加主键字段

#### 27. 外键约束未启用

描述: PRAGMA foreign_keys 返回 0，外键约束检查未启用

建议: 在数据库连接时执行 PRAGMA foreign_keys = ON 启用外键约束检查


## 四、优先级修复建议

| 优先级 | 问题标题 | 修复建议 |
|--------|---------|---------|
| P1 - 紧急 | 未找到数据库备份 | 立即执行数据库备份，建立定期备份计划 |
| P2 - 重要 | 表 achievements 缺少主键 | 为表 achievements 添加主键字段 |
| P2 - 重要 | 表 agent_tasks 缺少主键 | 为表 agent_tasks 添加主键字段 |
| P2 - 重要 | 表 assessment_reports 缺少主键 | 为表 assessment_reports 添加主键字段 |
| P2 - 重要 | 表 chat_messages 缺少主键 | 为表 chat_messages 添加主键字段 |
| P2 - 重要 | 表 chat_sessions 缺少主键 | 为表 chat_sessions 添加主键字段 |
| P2 - 重要 | 表 classroom_members 缺少主键 | 为表 classroom_members 添加主键字段 |
| P2 - 重要 | 表 classrooms 缺少主键 | 为表 classrooms 添加主键字段 |
| P2 - 重要 | 表 exercise_records 缺少主键 | 为表 exercise_records 添加主键字段 |
| P2 - 重要 | 表 exercise_sessions 缺少主键 | 为表 exercise_sessions 添加主键字段 |

## 五、资源状态

### 磁盘空间

| 项目 | 值 |
|------|------|
| 磁盘总容量 | 474.71 GB |
| 已使用 | 193.04 GB |
| 可用空间 | 281.67 GB |
| 可用比例 | 59.33% |
| 数据库文件 | 0.41 MB |

### 备份状态

| 项目 | 值 |
|------|------|
| 备份目录存在 | 否 |
| 备份文件数 | 0 |
| 最近备份 | 无 |

## 六、性能测试

| 表名 | 操作 | 耗时(ms) |
|------|------|---------|
| study_activities | GROUP_BY | 0.0 |

---

报告结束