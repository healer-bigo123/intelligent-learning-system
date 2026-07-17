"""
生成大量模拟通知数据用于测试分页功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
import uuid

from app.models.database import Notification, get_db
from sqlalchemy.orm import Session

# 通知模板
NOTIFICATION_TEMPLATES = [
    # 成就类
    {"title": "[成就] 成就解锁：{achievement}", "type": "achievement"},
    # 练习类
    {"title": "[练习] 练习完成通知", "type": "exercise"},
    # 课堂类
    {"title": "[课堂] 课堂通知", "type": "classroom"},
    # 提醒类
    {"title": "[提醒] 学习提醒", "type": "reminder"},
    # 系统类
    {"title": "[系统] 系统通知", "type": "system"},
]

ACHIEVEMENTS = [
    "练习新手 - 完成10道题",
    "学习达人 - 连续学习7天",
    "错题克星 - 复习20道错题",
    "专注之星 - 累计专注5小时",
    "知识探索者 - 学习3个新知识点",
    "满分王者 - 获得1次满分",
    "坚持不懈 - 连续学习14天",
    "学霸之路 - 完成50道题",
    "时间管理 - 累计专注10小时",
    "全面发展 - 掌握5个学科",
]

EXERCISE_MESSAGES = [
    "你完成了「三角函数基础」练习，正确率85%",
    "你完成了「向量运算」练习，正确率92%",
    "你完成了「数列求和」练习，正确率78%",
    "你完成了「概率统计」练习，正确率88%",
    "你完成了「立体几何」练习，正确率95%",
    "你完成了「解析几何」练习，正确率82%",
    "你完成了「导数应用」练习，正确率90%",
    "你完成了「积分计算」练习，正确率87%",
]

CLASSROOM_MESSAGES = [
    "李老师发布了新的随堂测验「函数与方程」",
    "王老师发布了课堂作业「数列与数学归纳法」",
    "张老师发起了课堂投票「最喜欢的学习方法」",
    "赵老师开始了直播课「高考数学冲刺」",
    "刘老师发布了课堂讨论「数学思维培养」",
]

REMINDER_MESSAGES = [
    "你已经连续学习3天了，继续保持！",
    "你有5道错题待复习，记得及时巩固",
    "今天的学习目标还差2小时，加油！",
    "明天有数学测验，记得提前复习",
    "本周学习计划完成度80%，继续努力",
    "你的专注时长本周排名第3，很棒！",
]

SYSTEM_MESSAGES = [
    "平台将于本周六凌晨进行系统维护",
    "新版本上线：新增智能错题本功能",
    "根据你的学习情况，为你推荐「高等数学进阶」课程",
    "你的学习报告已生成，点击查看详细分析",
    "新功能：思维导图已上线，快来体验",
]


def generate_notifications(db: Session, user_id: str = "user-001", count: int = 30):
    """生成指定数量的模拟通知"""
    print(f"[生成] 开始生成 {count} 条通知数据...")

    now = datetime.utcnow()
    created_count = 0

    for i in range(count):
        # 随机选择通知类型
        template_idx = i % len(NOTIFICATION_TEMPLATES)
        template = NOTIFICATION_TEMPLATES[template_idx]

        # 根据类型生成具体内容
        if template["type"] == "achievement":
            achievement = ACHIEVEMENTS[i % len(ACHIEVEMENTS)]
            title = template["title"].format(achievement=achievement)
            content = f"恭喜你达成成就「{achievement}」，继续加油！"
        elif template["type"] == "exercise":
            title = "[练习] 练习完成通知"
            content = EXERCISE_MESSAGES[i % len(EXERCISE_MESSAGES)]
        elif template["type"] == "classroom":
            title = "[课堂] 课堂通知"
            content = CLASSROOM_MESSAGES[i % len(CLASSROOM_MESSAGES)]
        elif template["type"] == "reminder":
            title = "[提醒] 学习提醒"
            content = REMINDER_MESSAGES[i % len(REMINDER_MESSAGES)]
        else:  # system
            title = "[系统] 系统通知"
            content = SYSTEM_MESSAGES[i % len(SYSTEM_MESSAGES)]

        # 生成时间戳（从最近到过去）
        hours_ago = i * 2  # 每条间隔2小时
        created_at = now - timedelta(hours=hours_ago)

        # 前10条未读，其余已读
        is_read = i >= 10

        notification_id = f"notif-test-{i+1:03d}"

        # 检查是否已存在
        existing = db.query(Notification).filter(Notification.id == notification_id).first()
        if existing:
            print(f"  [跳过] 通知已存在: {notification_id}")
            continue

        notification = Notification(
            id=notification_id,
            user_id=user_id,
            title=title,
            content=content,
            type=template["type"],
            is_read=is_read,
            created_at=created_at,
        )
        db.add(notification)
        created_count += 1
        print(f"  [创建] {title} - {created_at.strftime('%Y-%m-%d %H:%M')}")

    db.commit()
    print(f"\n[完成] 共创建 {created_count} 条通知数据")
    print(f"[提示] 其中前10条为未读状态，其余为已读状态")
    print(f"[提示] 可用于测试分页功能（每页20条）")


if __name__ == "__main__":
    # 获取数据库会话
    db = next(get_db())

    try:
        # 为 user-001 生成30条通知
        generate_notifications(db, user_id="user-001", count=30)
    finally:
        db.close()
