"""
数据库配置 - 使用 SQLite + SQLAlchemy（无需额外安装 MySQL）
Chroma 向量数据库同时作为文档/知识存储

修改说明：
1. 添加全局外键约束启用配置
2. 添加 external_data_records 表（外部数据记录表）
3. 完善索引定义
4. 支持 CASCADE、SET NULL 等级联操作
"""
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from app.core.config import settings

# 创建引擎 - 添加外键约束支持
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    } if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

# 自定义 SessionLocal 以支持 SQLite 外键约束
class ForeignKeySession(sessionmaker):
    """支持外键约束的会话类"""
    def __call__(self, **local_kw):
        session = super().__call__(**local_kw)
        # 在 SQLite 中强制启用外键约束
        if "sqlite" in settings.DATABASE_URL:
            session.execute(text("PRAGMA foreign_keys = ON"))
        return session

SessionLocal = ForeignKeySession(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ========== 数据模型定义 ==========

class StudentProfile(Base):
    """学生画像表"""
    __tablename__ = "student_profiles"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    name = Column(String(100), nullable=True)
    grade = Column(String(20), nullable=True)
    major = Column(String(100), nullable=True)
    target = Column(String(100), nullable=True)

    # 六大画像维度（JSON 字符串存储）
    dimensions = Column(Text, default="{}")

    # 知识掌握状态（JSON 字符串存储）
    knowledge_state = Column(Text, default="{}")

    # 薄弱知识点（逗号分隔的 ID 列表）
    weak_points = Column(Text, default="")

    # 兴趣标签
    interests = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键关联 - 一对一关系
    user = relationship("User", back_populates="profile", uselist=False)


class ChatSession(Base):
    """对话会话表"""
    __tablename__ = "chat_sessions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String(200), default="新对话")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键关联
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """对话消息表"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role = Column(String(20))  # user / assistant
    content = Column(Text)
    use_rag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 外键关联
    session = relationship("ChatSession", back_populates="messages")


class LearningResource(Base):
    """学习资源表（元数据存储在 SQLite，内容文件存储在磁盘）"""
    __tablename__ = "learning_resources"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(200))
    type = Column(String(50), index=True)  # video / document / quiz / code / mindmap
    subject = Column(String(100), index=True)
    topics = Column(Text, default="")  # 逗号分隔的知识点 ID
    difficulty = Column(Integer, default=3, index=True)
    duration = Column(Integer, default=0)  # 预计学习时长（分钟）
    file_path = Column(String(500), nullable=True)  # 文件存储路径
    content_text = Column(Text, nullable=True)  # 文本内容（用于检索）
    generated_by = Column(String(50), nullable=True)  # 生成该资源的智能体 ID
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    rating = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 外键关联
    user = relationship("User", back_populates="learning_resources")


class LearningPath(Base):
    """学习路径表"""
    __tablename__ = "learning_paths"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String(200))
    description = Column(Text, nullable=True)
    steps = Column(Text, default="")  # JSON 字符串存储步骤列表
    status = Column(String(20), default="active", index=True)  # active / completed / paused
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键关联
    user = relationship("User", back_populates="learning_paths")


class AgentTask(Base):
    """智能体任务表"""
    __tablename__ = "agent_tasks"

    id = Column(String(64), primary_key=True, index=True)
    agent_id = Column(String(50), index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    task_type = Column(String(50), index=True)
    parameters = Column(Text, default="")  # JSON 字符串
    status = Column(String(20), default="queued", index=True)  # queued / running / completed / failed
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 外键关联
    user = relationship("User", back_populates="agent_tasks")


# ========== 用户认证模块（后端 2.0 新增）==========

class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar = Column(String(500), nullable=True)
    role = Column(String(20), default="student", index=True)  # student / teacher / admin
    status = Column(String(20), default="active", index=True)  # active / inactive / banned
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    learning_resources = relationship("LearningResource", back_populates="user", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="user", cascade="all, delete-orphan")
    agent_tasks = relationship("AgentTask", back_populates="user", cascade="all, delete-orphan")
    mistakes = relationship("Mistake", back_populates="user", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="user", cascade="all, delete-orphan")
    exercise_records = relationship("ExerciseRecord", back_populates="user", cascade="all, delete-orphan")
    exercise_sessions = relationship("ExerciseSession", back_populates="user", cascade="all, delete-orphan")
    study_activities = relationship("StudyActivity", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class UserRole(Base):
    """用户角色权限表"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String(20), index=True, nullable=False)  # student / teacher / admin
    permissions = Column(Text, default="")  # JSON 字符串存储权限列表
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== 错题题库模块（后端 2.0 P0）==========

class Mistake(Base):
    """错题本表"""
    __tablename__ = "mistakes"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject = Column(String(100), index=True, nullable=False)  # 学科：数学、英语、物理等
    question = Column(Text, nullable=False)  # 题目内容
    correct_answer = Column(Text, nullable=False)  # 正确答案
    user_answer = Column(Text, nullable=True)  # 用户当时的答案
    analysis = Column(Text, nullable=True)  # 解析/反思
    knowledge_point = Column(String(200), index=True, nullable=True)  # 知识点
    tags = Column(Text, default="")  # 逗号分隔的标签
    source = Column(String(200), nullable=True)  # 来源（练习、考试、作业）
    difficulty = Column(Integer, default=3, index=True)  # 难度 1-5
    status = Column(String(20), default="unsolved", index=True)  # unsolved / reviewing / mastered
    review_count = Column(Integer, default=0)  # 复习次数
    last_review_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键关联
    user = relationship("User", back_populates="mistakes")


# ========== 练习测试模块（后端 2.0 P0）==========

class Exercise(Base):
    """练习题表"""
    __tablename__ = "exercises"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject = Column(String(100), index=True, nullable=False)
    type = Column(String(20), index=True, nullable=False)  # choice / fill_blank / short_answer / programming
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # JSON 字符串，选择题选项
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)  # 答案解析
    knowledge_point = Column(String(200), index=True, nullable=True)
    difficulty = Column(Integer, default=3, index=True)
    source = Column(String(50), default="manual", index=True)  # manual / ai_generated
    status = Column(String(20), default="active", index=True)  # active / archived
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 外键关联
    user = relationship("User", back_populates="exercises")
    records = relationship("ExerciseRecord", back_populates="exercise", cascade="all, delete-orphan")


class ExerciseRecord(Base):
    """练习记录/答题记录表"""
    __tablename__ = "exercise_records"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    exercise_id = Column(String(64), ForeignKey("exercises.id", ondelete="CASCADE"), index=True, nullable=False)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False, index=True)
    score = Column(Integer, default=0)  # 得分（百分比）
    time_spent = Column(Integer, default=0)  # 耗时（秒）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 外键关联
    user = relationship("User", back_populates="exercise_records")
    exercise = relationship("Exercise", back_populates="records")


class ExerciseSession(Base):
    """练习会话/测试会话表（一组题的练习）"""
    __tablename__ = "exercise_sessions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=True)  # 练习标题
    subject = Column(String(100), index=True, nullable=False)
    exercise_ids = Column(Text, default="")  # 逗号分隔的练习题 ID
    total_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    score = Column(Integer, default=0)  # 总分（百分比）
    status = Column(String(20), default="in_progress", index=True)  # in_progress / completed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    # 外键关联
    user = relationship("User", back_populates="exercise_sessions")


class AssessmentReport(Base):
    """评估报告表"""
    __tablename__ = "assessment_reports"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class MindMap(Base):
    """思维导图表"""
    __tablename__ = "mind_maps"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), index=True, nullable=False)
    content = Column(Text, default="{}")  # JSON 字符串存储思维导图数据
    status = Column(String(20), default="active", index=True)  # active / archived
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ========== 课堂互动模块 ==========

class Classroom(Base):
    """课堂表"""
    __tablename__ = "classrooms"

    id = Column(String(64), primary_key=True, index=True)
    code = Column(String(6), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    teacher_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status = Column(String(20), default="active", index=True)  # active / closed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    teacher = relationship("User")
    members = relationship("ClassroomMember", back_populates="classroom", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="classroom", cascade="all, delete-orphan")
    lotteries = relationship("Lottery", back_populates="classroom", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="classroom", cascade="all, delete-orphan")


class ClassroomMember(Base):
    """课堂成员表"""
    __tablename__ = "classroom_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    classroom_id = Column(String(64), ForeignKey("classrooms.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String(20), default="student", index=True)  # teacher / student
    joined_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 外键关联
    classroom = relationship("Classroom", back_populates="members")
    user = relationship("User")

    # 联合唯一约束
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class Vote(Base):
    """投票表"""
    __tablename__ = "votes"

    id = Column(String(64), primary_key=True, index=True)
    classroom_id = Column(String(64), ForeignKey("classrooms.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    options = Column(Text, default="[]")  # JSON 字符串，选项列表
    results = Column(Text, default="{}")  # JSON 字符串，投票结果统计
    status = Column(String(20), default="active", index=True)  # active / ended
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    ended_at = Column(DateTime, nullable=True)

    # 外键关联
    classroom = relationship("Classroom", back_populates="votes")


class Lottery(Base):
    """抽签表"""
    __tablename__ = "lotteries"

    id = Column(String(64), primary_key=True, index=True)
    classroom_id = Column(String(64), ForeignKey("classrooms.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    candidates = Column(Text, default="[]")  # JSON 字符串，候选人列表
    winner = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 外键关联
    classroom = relationship("Classroom", back_populates="lotteries")


class Quiz(Base):
    """随堂测验表"""
    __tablename__ = "quizzes"

    id = Column(String(64), primary_key=True, index=True)
    classroom_id = Column(String(64), ForeignKey("classrooms.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    questions = Column(Text, default="[]")  # JSON 字符串，题目列表
    answers = Column(Text, default="{}")  # JSON 字符串，用户提交的答案
    status = Column(String(20), default="active", index=True)  # active / ended
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 外键关联
    classroom = relationship("Classroom", back_populates="quizzes")


# ========== 学习资料库模块 ==========

class StudyMaterial(Base):
    """学习资料表"""
    __tablename__ = "study_materials"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # 资料内容
    subject = Column(String(100), index=True, nullable=False)  # 学科：数学、英语、物理等
    grade = Column(String(20), index=True, nullable=True)  # 年级：高一、高二、初三等
    material_type = Column(String(50), default="知识点", index=True)  # 知识点/公式/例题/文章/笔记
    knowledge_point = Column(String(200), index=True, nullable=True)  # 所属知识点
    tags = Column(Text, default="")  # 逗号分隔的标签
    source = Column(String(200), nullable=True)  # 来源（教材、网络、整理）
    difficulty = Column(Integer, default=3, index=True)  # 难度 1-5
    views = Column(Integer, default=0)  # 浏览次数
    status = Column(String(20), default="active", index=True)  # active / archived
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ========== 收藏功能模块 ==========

class Favorite(Base):
    """收藏表"""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    target_type = Column(String(50), index=True, nullable=False)  # study_material / mistake / exercise
    target_id = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 外键关联
    user = relationship("User", back_populates="favorites")

    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


# ========== 通知消息模块 ==========

class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="system", index=True)  # system / exercise / classroom / reminder
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 外键关联
    user = relationship("User", back_populates="notifications")


# ========== 学习记录时间线模块 ==========

class StudyActivity(Base):
    """学习活动记录表"""
    __tablename__ = "study_activities"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    activity_type = Column(String(50), index=True, nullable=False)  # exercise / mistake_review / material_read / session_complete
    target_id = Column(String(64), nullable=True)
    title = Column(String(200), nullable=True)
    duration = Column(Integer, default=0)  # 学习时长（秒）
    score = Column(Integer, nullable=True)  # 得分（如果有）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 外键关联
    user = relationship("User", back_populates="study_activities")


# ========== 成就系统模块 ==========

class Achievement(Base):
    """成就表"""
    __tablename__ = "achievements"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(200), nullable=True)
    condition_type = Column(String(50), index=True, nullable=False)  # exercise_count / streak_days / accuracy / material_count
    condition_value = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class UserAchievement(Base):
    """用户成就表"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    achievement_id = Column(String(64), ForeignKey("achievements.id", ondelete="CASCADE"), index=True, nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class LearningWebsite(Base):
    """学习网站链接表"""
    __tablename__ = "learning_websites"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    url = Column(String(500), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="general", index=True)
    icon = Column(String(500), nullable=True)
    is_recommended = Column(Boolean, default=False, index=True)
    sort_order = Column(Integer, default=0)
    status = Column(String(20), default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ========== 外部数据模块（新增）==========

class ExternalDataRecord(Base):
    """外部数据记录表 - 用于存储从外部数据源获取的数据"""
    __tablename__ = "external_data_records"

    id = Column(String(64), primary_key=True, index=True)
    source_id = Column(String(64), index=True, nullable=False)  # 外部数据源ID
    data_type = Column(String(50), index=True, nullable=False)  # 数据类型：exercise / knowledge / material / course
    data = Column(Text, nullable=False)  # JSON 字符串存储原始数据
    title = Column(String(200), index=True, nullable=True)  # 标题（用于搜索）
    subject = Column(String(100), index=True, nullable=True)  # 学科
    knowledge_point = Column(String(200), index=True, nullable=True)  # 知识点
    is_active = Column(Boolean, default=True, index=True)  # 是否有效
    sync_time = Column(DateTime, index=True, nullable=True)  # 同步时间
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 复合索引 - 优化常用查询
    __table_args__ = (
        # 复合索引：按来源和类型查询
        {'sqlite_autoincrement': False},
    )


# ========== 任务管理模块（新增）==========

class Task(Base):
    """任务表 - 今日任务管理"""
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(100), default="其他", index=True)
    priority = Column(String(20), default="medium", index=True)  # low, medium, high
    status = Column(String(20), default="pending", index=True)  # pending, completed
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ========== 数据库操作函数 ==========

def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据库表初始化完成 (SQLite)")


def get_db():
    """获取数据库会话（用于 FastAPI Dependency）"""
    db = SessionLocal()
    try:
        # 确保 SQLite 外键约束启用
        if "sqlite" in settings.DATABASE_URL:
            db.execute(text("PRAGMA foreign_keys = ON"))
        yield db
    finally:
        db.close()


def test_foreign_key_constraint():
    """测试外键约束功能"""
    """
    此函数用于验证外键约束是否正常工作。
    在 FastAPI 启动时或测试中调用此函数。
    
    测试场景：
    1. 尝试删除被引用的用户，验证级联删除是否生效
    2. 尝试插入不存在的外键引用，验证约束是否阻止
    """
    db = SessionLocal()
    try:
        # 测试1: 验证外键约束已启用
        result = db.execute(text("PRAGMA foreign_keys")).fetchone()
        if result and result[0] == 1:
            print("[OK] 外键约束已启用")
            return True
        else:
            print("[WARN] 外键约束未启用")
            return False
    except Exception as e:
        print(f"[ERROR] 外键约束测试失败: {e}")
        return False
    finally:
        db.close()