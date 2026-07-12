"""
API V1 路由聚合
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, knowledge, chat, agents, auth, mistakes, exercises, mindmaps, analytics, classroom, study_materials, favorites, notifications, achievements, timeline, learning_paths, learning_websites, external_data, image_recognition, tasks

api_router = APIRouter()

# 健康检查
api_router.include_router(health.router, prefix="/health", tags=["health"])

# 用户认证（后端 2.0 新增）
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 错题题库（后端 2.0 P0）
api_router.include_router(mistakes.router, prefix="/mistakes", tags=["mistakes"])

# 练习测试（后端 2.0 P0）
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])

# 知识库管理
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

# 对话接口
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# 智能体接口
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# 思维导图
api_router.include_router(mindmaps.router, prefix="/mindmaps", tags=["mindmaps"])

# 成绩分析
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# 课堂互动
api_router.include_router(classroom.router, prefix="/classrooms", tags=["classroom"])

# 学习资料库
api_router.include_router(study_materials.router, prefix="/study-materials", tags=["study-materials"])

# 学习路径/计划
api_router.include_router(learning_paths.router, prefix="/learning-paths", tags=["learning-paths"])

# 学习记录时间线
api_router.include_router(timeline.router, prefix="/timeline", tags=["timeline"])

# 任务管理（新增）
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# 收藏功能
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])

# 通知消息
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

# 成就系统
api_router.include_router(achievements.router, prefix="/achievements", tags=["achievements"])

# 学习网站链接
api_router.include_router(learning_websites.router, prefix="/learning-websites", tags=["learning-websites"])

# 外部数据源管理
api_router.include_router(external_data.router, prefix="/external-data", tags=["external-data"])

# 图片识别
api_router.include_router(image_recognition.router, prefix="/image", tags=["image"])
