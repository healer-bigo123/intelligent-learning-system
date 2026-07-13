"""测试各智能体对话功能"""
import sys
sys.path.insert(0, 'app')
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import uuid
from datetime import datetime

from app.core.agent_system import (
    QAAgent, PlanningAgent, GradingAgent, 
    CompanionAgent, RecommendationAgent, AnalyticsAgent,
    Task, Intent, IntentType, TaskStatus
)

def create_task(question: str, intent_type: IntentType = IntentType.HELP) -> Task:
    """创建测试任务"""
    intent = Intent(
        intent_type=intent_type,
        entities={
            "subject": "数学",
            "topic": "未知",
            "issue": question
        },
        urgency="normal",
        raw_input=question
    )
    
    return Task(
        id=f"task_{str(uuid.uuid4())[:8]}",
        intent=intent,
        status=TaskStatus.IDLE,
        created_at=datetime.utcnow()
    )

def print_result(result):
    """打印结果"""
    content = str(result.content) if result.content else "无响应"
    return content[:150] + "..." if len(content) > 150 else content

print("=== 测试各智能体对话功能 ===\n")

# 测试答疑Agent
print("[1] 测试答疑Agent (QA)")
qa_agent = QAAgent()
task = create_task("什么是牛顿第二定律？")
result = qa_agent.process(task)
print(f"问: 什么是牛顿第二定律？")
print(f"答: {print_result(result)}")
print()

# 测试规划Agent
print("[2] 测试规划Agent (Planning)")
planning_agent = PlanningAgent()
task = create_task("帮我制定一个周末学习计划", IntentType.PLAN)
result = planning_agent.process(task)
print(f"问: 帮我制定一个周末学习计划")
print(f"答: {print_result(result)}")
print()

# 测试批改Agent
print("[3] 测试批改Agent (Grading)")
grading_agent = GradingAgent()
task = create_task("2+3=5，这个答案对吗？", IntentType.GRADING)
result = grading_agent.process(task)
print(f"问: 2+3=5，这个答案对吗？")
print(f"答: {print_result(result)}")
print()

# 测试陪伴Agent
print("[4] 测试陪伴Agent (Companion)")
companion_agent = CompanionAgent()
task = create_task("我今天学习有点累了", IntentType.COMPANION)
result = companion_agent.process(task)
print(f"问: 我今天学习有点累了")
print(f"答: {print_result(result)}")
print()

# 测试推荐Agent
print("[5] 测试推荐Agent (Recommendation)")
rec_agent = RecommendationAgent()
task = create_task("推荐一些数学学习资源", IntentType.RECOMMEND)
result = rec_agent.process(task)
print(f"问: 推荐一些数学学习资源")
print(f"答: {print_result(result)}")
print()

# 测试分析Agent
print("[6] 测试分析Agent (Analytics)")
analytics_agent = AnalyticsAgent()
task = create_task("分析我的学习情况", IntentType.ANALYSIS)
result = analytics_agent.process(task)
print(f"问: 分析我的学习情况")
print(f"答: {print_result(result)}")
print()

print("=== 所有智能体测试完成 ===")
