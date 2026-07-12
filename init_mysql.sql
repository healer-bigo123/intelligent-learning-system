-- SmartLearning MySQL 数据库初始化脚本
-- 数据库: smart_learning
-- 字符集: utf8mb4

USE smart_learning;

-- ============================================
-- 1. 用户认证模块
-- ============================================

CREATE TABLE `users` (
  `id` VARCHAR(64) NOT NULL COMMENT '用户唯一ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  `hashed_password` VARCHAR(255) NOT NULL COMMENT '加密后的密码',
  `nickname` VARCHAR(100) DEFAULT NULL COMMENT '昵称',
  `avatar` VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
  `role` VARCHAR(20) DEFAULT 'student' COMMENT '角色：student/teacher/admin',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态：active/inactive/banned',
  `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  UNIQUE KEY `uk_phone` (`phone`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE `user_roles` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `role` VARCHAR(20) NOT NULL COMMENT '角色',
  `permissions` TEXT COMMENT '权限列表（JSON字符串）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色权限表';

-- ============================================
-- 2. 学生画像模块
-- ============================================

CREATE TABLE `student_profiles` (
  `id` VARCHAR(64) NOT NULL COMMENT '画像ID',
  `name` VARCHAR(100) DEFAULT NULL COMMENT '姓名',
  `grade` VARCHAR(20) DEFAULT NULL COMMENT '年级',
  `major` VARCHAR(100) DEFAULT NULL COMMENT '专业',
  `target` VARCHAR(100) DEFAULT NULL COMMENT '学习目标',
  `dimensions` TEXT COMMENT '六大画像维度（JSON）',
  `knowledge_state` TEXT COMMENT '知识掌握状态（JSON）',
  `weak_points` TEXT COMMENT '薄弱知识点（逗号分隔）',
  `interests` TEXT COMMENT '兴趣标签',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生画像表';

-- ============================================
-- 3. 对话模块
-- ============================================

CREATE TABLE `chat_sessions` (
  `id` VARCHAR(64) NOT NULL COMMENT '会话ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `title` VARCHAR(200) DEFAULT '新对话' COMMENT '会话标题',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话会话表';

CREATE TABLE `chat_messages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `session_id` VARCHAR(64) NOT NULL COMMENT '会话ID',
  `role` VARCHAR(20) NOT NULL COMMENT '角色：user/assistant',
  `content` TEXT NOT NULL COMMENT '消息内容',
  `use_rag` TINYINT(1) DEFAULT 0 COMMENT '是否使用RAG',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话消息表';

-- ============================================
-- 4. 学习资源模块
-- ============================================

CREATE TABLE `learning_resources` (
  `id` VARCHAR(64) NOT NULL COMMENT '资源ID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `type` VARCHAR(50) DEFAULT NULL COMMENT '类型：video/document/quiz/code/mindmap',
  `subject` VARCHAR(100) DEFAULT NULL COMMENT '学科',
  `topics` TEXT COMMENT '知识点（逗号分隔）',
  `difficulty` INT DEFAULT 3 COMMENT '难度1-5',
  `duration` INT DEFAULT 0 COMMENT '预计时长（分钟）',
  `file_path` VARCHAR(500) DEFAULT NULL COMMENT '文件路径',
  `content_text` TEXT COMMENT '文本内容',
  `generated_by` VARCHAR(50) DEFAULT NULL COMMENT '生成智能体ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `rating` FLOAT DEFAULT 0 COMMENT '评分',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习资源表';

-- ============================================
-- 5. 错题题库模块
-- ============================================

CREATE TABLE `mistakes` (
  `id` VARCHAR(64) NOT NULL COMMENT '错题ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `subject` VARCHAR(100) NOT NULL COMMENT '学科',
  `question` TEXT NOT NULL COMMENT '题目内容',
  `correct_answer` TEXT NOT NULL COMMENT '正确答案',
  `user_answer` TEXT DEFAULT NULL COMMENT '用户答案',
  `analysis` TEXT DEFAULT NULL COMMENT '解析',
  `knowledge_point` VARCHAR(200) DEFAULT NULL COMMENT '知识点',
  `tags` TEXT COMMENT '标签（逗号分隔）',
  `source` VARCHAR(200) DEFAULT NULL COMMENT '来源',
  `difficulty` INT DEFAULT 3 COMMENT '难度1-5',
  `status` VARCHAR(20) DEFAULT 'unsolved' COMMENT '状态：unsolved/reviewing/mastered',
  `review_count` INT DEFAULT 0 COMMENT '复习次数',
  `last_review_at` DATETIME DEFAULT NULL COMMENT '最后复习时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_subject` (`subject`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='错题本表';

-- ============================================
-- 6. 练习测试模块
-- ============================================

CREATE TABLE `exercises` (
  `id` VARCHAR(64) NOT NULL COMMENT '题目ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `subject` VARCHAR(100) NOT NULL COMMENT '学科',
  `type` VARCHAR(20) NOT NULL COMMENT '类型：choice/fill_blank/short_answer/programming',
  `question` TEXT NOT NULL COMMENT '题目',
  `options` TEXT DEFAULT NULL COMMENT '选项（JSON）',
  `correct_answer` TEXT NOT NULL COMMENT '正确答案',
  `explanation` TEXT DEFAULT NULL COMMENT '解析',
  `knowledge_point` VARCHAR(200) DEFAULT NULL COMMENT '知识点',
  `difficulty` INT DEFAULT 3 COMMENT '难度1-5',
  `source` VARCHAR(50) DEFAULT 'manual' COMMENT '来源',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_subject` (`subject`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='练习题表';

CREATE TABLE `exercise_records` (
  `id` VARCHAR(64) NOT NULL COMMENT '记录ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `exercise_id` VARCHAR(64) NOT NULL COMMENT '题目ID',
  `user_answer` TEXT DEFAULT NULL COMMENT '用户答案',
  `is_correct` TINYINT(1) DEFAULT 0 COMMENT '是否正确',
  `score` INT DEFAULT 0 COMMENT '得分（百分比）',
  `time_spent` INT DEFAULT 0 COMMENT '耗时（秒）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_exercise_id` (`exercise_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='练习记录表';

CREATE TABLE `exercise_sessions` (
  `id` VARCHAR(64) NOT NULL COMMENT '会话ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `title` VARCHAR(200) DEFAULT NULL COMMENT '标题',
  `subject` VARCHAR(100) NOT NULL COMMENT '学科',
  `exercise_ids` TEXT COMMENT '题目ID列表（逗号分隔）',
  `total_count` INT DEFAULT 0 COMMENT '总题数',
  `correct_count` INT DEFAULT 0 COMMENT '正确数',
  `score` INT DEFAULT 0 COMMENT '总分',
  `status` VARCHAR(20) DEFAULT 'in_progress' COMMENT '状态：in_progress/completed',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='练习会话表';

-- ============================================
-- 7. 思维导图模块
-- ============================================

CREATE TABLE `mind_maps` (
  `id` VARCHAR(64) NOT NULL COMMENT '导图ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `subject` VARCHAR(100) NOT NULL COMMENT '学科',
  `content` TEXT COMMENT '导图数据（JSON）',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='思维导图表';

-- ============================================
-- 8. 成绩分析模块
-- ============================================

CREATE TABLE `assessment_reports` (
  `id` VARCHAR(64) NOT NULL COMMENT '报告ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `content` TEXT NOT NULL COMMENT '报告内容',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评估报告表';

-- ============================================
-- 9. 课堂互动模块
-- ============================================

CREATE TABLE `classrooms` (
  `id` VARCHAR(64) NOT NULL COMMENT '课堂ID',
  `code` VARCHAR(6) NOT NULL COMMENT '6位邀请码',
  `name` VARCHAR(200) NOT NULL COMMENT '课堂名称',
  `description` TEXT DEFAULT NULL COMMENT '描述',
  `teacher_id` VARCHAR(64) NOT NULL COMMENT '老师ID',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态：active/closed',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code` (`code`),
  KEY `idx_teacher_id` (`teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课堂表';

CREATE TABLE `classroom_members` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `classroom_id` VARCHAR(64) NOT NULL COMMENT '课堂ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `role` VARCHAR(20) DEFAULT 'student' COMMENT '角色：teacher/student',
  `joined_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  PRIMARY KEY (`id`),
  KEY `idx_classroom_id` (`classroom_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课堂成员表';

CREATE TABLE `votes` (
  `id` VARCHAR(64) NOT NULL COMMENT '投票ID',
  `classroom_id` VARCHAR(64) NOT NULL COMMENT '课堂ID',
  `title` VARCHAR(200) NOT NULL COMMENT '投票标题',
  `options` TEXT COMMENT '选项（JSON）',
  `results` TEXT COMMENT '结果统计（JSON）',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态：active/ended',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `ended_at` DATETIME DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (`id`),
  KEY `idx_classroom_id` (`classroom_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投票表';

CREATE TABLE `lotteries` (
  `id` VARCHAR(64) NOT NULL COMMENT '抽签ID',
  `classroom_id` VARCHAR(64) NOT NULL COMMENT '课堂ID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `candidates` TEXT COMMENT '候选人（JSON）',
  `winner` VARCHAR(200) DEFAULT NULL COMMENT '中奖者',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_classroom_id` (`classroom_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='抽签表';

CREATE TABLE `quizzes` (
  `id` VARCHAR(64) NOT NULL COMMENT '测验ID',
  `classroom_id` VARCHAR(64) NOT NULL COMMENT '课堂ID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `questions` TEXT COMMENT '题目（JSON）',
  `answers` TEXT COMMENT '答案（JSON）',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态：active/ended',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_classroom_id` (`classroom_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='随堂测验表';

-- ============================================
-- 10. 学习资料库模块
-- ============================================

CREATE TABLE `study_materials` (
  `id` VARCHAR(64) NOT NULL COMMENT '资料ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `content` TEXT NOT NULL COMMENT '内容',
  `subject` VARCHAR(100) NOT NULL COMMENT '学科',
  `grade` VARCHAR(20) DEFAULT NULL COMMENT '年级',
  `material_type` VARCHAR(50) DEFAULT '知识点' COMMENT '类型',
  `knowledge_point` VARCHAR(200) DEFAULT NULL COMMENT '知识点',
  `tags` TEXT COMMENT '标签',
  `source` VARCHAR(200) DEFAULT NULL COMMENT '来源',
  `difficulty` INT DEFAULT 3 COMMENT '难度1-5',
  `views` INT DEFAULT 0 COMMENT '浏览次数',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_subject` (`subject`),
  KEY `idx_material_type` (`material_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习资料表';

-- ============================================
-- 11. 收藏功能模块
-- ============================================

CREATE TABLE `favorites` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `target_type` VARCHAR(50) NOT NULL COMMENT '类型：study_material/mistake/exercise',
  `target_id` VARCHAR(64) NOT NULL COMMENT '目标ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_target` (`target_type`, `target_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';

-- ============================================
-- 12. 通知消息模块
-- ============================================

CREATE TABLE `notifications` (
  `id` VARCHAR(64) NOT NULL COMMENT '通知ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `content` TEXT NOT NULL COMMENT '内容',
  `type` VARCHAR(50) DEFAULT 'system' COMMENT '类型：system/exercise/classroom/reminder',
  `is_read` TINYINT(1) DEFAULT 0 COMMENT '是否已读',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_is_read` (`is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';

-- ============================================
-- 13. 学习记录时间线模块
-- ============================================

CREATE TABLE `study_activities` (
  `id` VARCHAR(64) NOT NULL COMMENT '活动ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `activity_type` VARCHAR(50) NOT NULL COMMENT '类型：exercise/mistake_review/material_read/session_complete',
  `target_id` VARCHAR(64) DEFAULT NULL COMMENT '目标ID',
  `title` VARCHAR(200) DEFAULT NULL COMMENT '标题',
  `duration` INT DEFAULT 0 COMMENT '时长（秒）',
  `score` INT DEFAULT NULL COMMENT '得分',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_activity_type` (`activity_type`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习活动记录表';

-- ============================================
-- 14. 成就系统模块
-- ============================================

CREATE TABLE `achievements` (
  `id` VARCHAR(64) NOT NULL COMMENT '成就ID',
  `name` VARCHAR(100) NOT NULL COMMENT '名称',
  `description` TEXT NOT NULL COMMENT '描述',
  `icon` VARCHAR(200) DEFAULT NULL COMMENT '图标',
  `condition_type` VARCHAR(50) NOT NULL COMMENT '条件类型：exercise_count/streak_days/accuracy/material_count',
  `condition_value` INT NOT NULL COMMENT '条件值',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成就定义表';

CREATE TABLE `user_achievements` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `achievement_id` VARCHAR(64) NOT NULL COMMENT '成就ID',
  `unlocked_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '解锁时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_achievement_id` (`achievement_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户成就表';

-- ============================================
-- 15. 智能体任务模块
-- ============================================

CREATE TABLE `agent_tasks` (
  `id` VARCHAR(64) NOT NULL COMMENT '任务ID',
  `agent_id` VARCHAR(50) NOT NULL COMMENT '智能体ID',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
  `task_type` VARCHAR(50) NOT NULL COMMENT '任务类型',
  `parameters` TEXT COMMENT '参数（JSON）',
  `status` VARCHAR(20) DEFAULT 'queued' COMMENT '状态：queued/running/completed/failed',
  `result` TEXT DEFAULT NULL COMMENT '结果',
  `error` TEXT DEFAULT NULL COMMENT '错误信息',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
  PRIMARY KEY (`id`),
  KEY `idx_agent_id` (`agent_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='智能体任务表';

-- ============================================
-- 索引优化
-- ============================================

CREATE INDEX idx_materials_filter ON study_materials(subject, grade, material_type, difficulty);
CREATE INDEX idx_mistakes_filter ON mistakes(user_id, subject, status);
CREATE INDEX idx_records_user_time ON exercise_records(user_id, created_at);
CREATE INDEX idx_activities_filter ON study_activities(user_id, activity_type, created_at);
CREATE INDEX idx_notifications_filter ON notifications(user_id, is_read, created_at);

-- ============================================
-- 完成
-- ============================================
SELECT '数据库初始化完成！共创建 25 张表。' AS message;
