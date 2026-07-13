"""
智能体系统核心模块

包含：
1. 调度中心组件：意图识别器、任务分解器、状态管理器、记忆检索器、结果聚合器、冲突仲裁器
2. 智能体集群：答疑Agent、规划Agent、批改Agent、陪伴Agent、推荐Agent、分析Agent
3. 智能体基类和工具调用框架
4. LLM客户端集成
"""
import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# ================ LLM 集成 ================
try:
    from app.config.llm_config import LLM_CONFIG, PROMPT_TEMPLATES, SYSTEM_PROMPT
    from app.core.llm_client import create_llm_client, LLMConfig, Message
    
    # 创建全局 LLM 客户端
    llm_client = create_llm_client(
        provider=LLM_CONFIG["provider"],
        api_key=LLM_CONFIG["api_key"],
        secret_key=LLM_CONFIG["secret_key"],
        model_name=LLM_CONFIG["model_name"],
        base_url=LLM_CONFIG.get("base_url"),
        temperature=LLM_CONFIG["temperature"],
        max_tokens=LLM_CONFIG["max_tokens"],
        timeout=LLM_CONFIG["timeout"]
    )
    LLM_AVAILABLE = True
except Exception as e:
    # 如果 LLM 客户端初始化失败，使用模拟模式
    print(f"LLM 客户端初始化失败，使用模拟模式: {e}")
    LLM_AVAILABLE = False
    llm_client = None
    PROMPT_TEMPLATES = {}
    SYSTEM_PROMPT = ""

# ================ 枚举类型定义 ================

class IntentType(str, Enum):
    """意图类型枚举"""
    HELP = "求助"
    PLAN = "规划"
    GRADING = "批改"
    COMPANION = "陪伴"
    RECOMMEND = "推荐"
    ANALYSIS = "分析"
    UNKNOWN = "未知"

class TaskStatus(str, Enum):
    """任务状态枚举"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    DISPATCHING = "dispatching"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentType(str, Enum):
    """智能体类型枚举"""
    QA = "qa"                    # 答疑Agent
    PLANNING = "planning"        # 规划Agent
    GRADING = "grading"          # 批改Agent
    COMPANION = "companion"      # 陪伴Agent
    RECOMMENDATION = "recommendation"  # 推荐Agent
    ANALYTICS = "analytics"      # 分析Agent

# ================ 数据模型定义 ================

@dataclass
class Intent:
    """意图对象"""
    intent_type: IntentType
    entities: Dict[str, Any]
    urgency: str = "normal"  # high, normal, low
    preferred_agent: Optional[str] = None
    emotion_tag: Optional[str] = None
    raw_input: Optional[str] = None

@dataclass
class Task:
    """任务对象"""
    id: str
    intent: Intent
    status: TaskStatus = TaskStatus.IDLE
    subtasks: List['Task'] = None
    assigned_agent: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    parent_task_id: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.subtasks is None:
            self.subtasks = []

@dataclass
class AgentResult:
    """智能体执行结果"""
    task_id: str
    agent_id: str
    content: Any
    confidence: float = 1.0
    reasoning: Optional[str] = None
    supporting_data: Optional[Dict[str, Any]] = None
    conflict_detected: bool = False

@dataclass
class SessionState:
    """会话状态"""
    session_id: str
    user_id: str
    tasks: List[Task] = None
    conversation_history: List[Dict[str, Any]] = None
    created_at: datetime = None
    last_active_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_active_at is None:
            self.last_active_at = datetime.utcnow()
        if self.tasks is None:
            self.tasks = []
        if self.conversation_history is None:
            self.conversation_history = []

# ================ 智能体工具基类 ================

class Tool(ABC):
    """工具基类"""
    name: str
    description: str
    parameters: Dict[str, Any]

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        pass

    def to_dict(self):
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

class KnowledgeBaseSearchTool(Tool):
    """知识库检索工具"""
    name = "knowledge_base_search"
    description = "在知识库中检索相关概念和知识点"
    parameters = {
        "query": {"type": "string", "description": "搜索关键词", "required": True},
        "top_k": {"type": "integer", "description": "返回数量", "default": 5}
    }

    def execute(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """执行知识库检索"""
        # 模拟检索结果
        return [
            {"id": str(uuid.uuid4()), "content": f"关于'{query}'的知识点1", "score": 0.95},
            {"id": str(uuid.uuid4()), "content": f"关于'{query}'的知识点2", "score": 0.88},
            {"id": str(uuid.uuid4()), "content": f"关于'{query}'的知识点3", "score": 0.82}
        ][:top_k]

class ExerciseBankSearchTool(Tool):
    """题库检索工具"""
    name = "exercise_bank_search"
    description = "在题库中检索相关练习题"
    parameters = {
        "subject": {"type": "string", "description": "学科", "required": True},
        "topic": {"type": "string", "description": "知识点", "required": True},
        "difficulty": {"type": "integer", "description": "难度1-5", "default": 3},
        "count": {"type": "integer", "description": "数量", "default": 3}
    }

    def execute(self, subject: str, topic: str, difficulty: int = 3, count: int = 3) -> List[Dict[str, Any]]:
        """执行题库检索"""
        return [
            {
                "id": str(uuid.uuid4()),
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty,
                "question": f"{subject}-{topic} 练习题{i+1}"
            }
            for i in range(count)
        ]

class StudentProfileTool(Tool):
    """学生画像工具"""
    name = "student_profile"
    description = "获取学生画像信息"
    parameters = {
        "user_id": {"type": "string", "description": "用户ID", "required": True}
    }

    def execute(self, user_id: str) -> Dict[str, Any]:
        """获取学生画像"""
        return {
            "user_id": user_id,
            "weak_points": ["数学-导数", "物理-力学"],
            "learning_style": "规律计划型",
            "emotion_state": "normal",
            "recent_performance": {"数学": 85, "物理": 78, "英语": 92}
        }

class ResourceRecommendationTool(Tool):
    """资源推荐工具"""
    name = "resource_recommendation"
    description = "推荐学习资源"
    parameters = {
        "user_id": {"type": "string", "description": "用户ID", "required": True},
        "topic": {"type": "string", "description": "目标知识点", "required": True},
        "count": {"type": "integer", "description": "推荐数量", "default": 3}
    }

    def execute(self, user_id: str, topic: str, count: int = 3) -> List[Dict[str, Any]]:
        """获取资源推荐"""
        return [
            {
                "id": str(uuid.uuid4()),
                "title": f"{topic} 学习资料{i+1}",
                "type": ["视频", "文档", "练习"][i % 3],
                "url": f"https://example.com/resource/{i+1}"
            }
            for i in range(count)
        ]

# ================ 智能体基类 ================

class Agent(ABC):
    """智能体基类"""
    
    def __init__(self, agent_type: AgentType, agent_id: str = None):
        self.agent_type = agent_type
        self.agent_id = agent_id or f"{agent_type.value}_{str(uuid.uuid4())[:8]}"
        self.tools: List[Tool] = []
        self.memory: Dict[str, Any] = {}
    
    @abstractmethod
    def process(self, task: Task, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """处理任务"""
        pass
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return [tool.to_dict() for tool in self.tools]
    
    def invoke_tool(self, tool_name: str, **kwargs) -> Any:
        """调用工具"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.execute(**kwargs)
        raise ValueError(f"工具 {tool_name} 不存在")
    
    def add_memory(self, key: str, value: Any):
        """添加记忆"""
        self.memory[key] = value
    
    def get_memory(self, key: str) -> Optional[Any]:
        """获取记忆"""
        return self.memory.get(key)

# ================ 智能体实现 ================

class QAAgent(Agent):
    """答疑Agent - 回答学科问题、解释概念、梳理解题思路"""
    
    def __init__(self):
        super().__init__(AgentType.QA)
        self.tools = [
            KnowledgeBaseSearchTool(),
            ExerciseBankSearchTool()
        ]
    
    def process(self, task: Task, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """处理答疑任务"""
        intent = task.intent
        subject = intent.entities.get("subject") or "未知学科"
        topic = intent.entities.get("topic") or "未知知识点"
        question = intent.entities.get("issue") or intent.raw_input
        
        # 1. 检索知识库
        kb_results = self.invoke_tool("knowledge_base_search", query=f"{subject} {topic}")
        
        # 2. 生成回答（优先使用真实LLM）
        if LLM_AVAILABLE and llm_client:
            try:
                # 构建prompt
                prompt = PROMPT_TEMPLATES.get("qa_agent", """
你是一个专业的学科答疑助手，请回答以下问题：

学科：{subject}
知识点：{topic}
用户问题：{question}

参考知识：
{references}

请按照以下结构回答：
1. 问题分析
2. 核心知识点
3. 解题思路
4. 注意事项
5. 拓展建议
                """).format(
                    subject=subject,
                    topic=topic,
                    question=question,
                    references="\n".join([f"- {r['content']}" for r in kb_results])
                )
                
                # 调用LLM
                response = llm_client.generate([
                    Message(role="system", content=SYSTEM_PROMPT),
                    Message(role="user", content=prompt)
                ])
                
                if response.error:
                    # LLM调用失败，回退到模拟模式
                    answer = self._generate_simulated_answer(subject, topic, question, kb_results)
                    confidence = 0.85  # 修复：添加默认置信度
                else:
                    answer = response.content
                    confidence = min(0.95, 0.8 + (response.usage.get('completion_tokens', 0) / 1000)) if response.usage else 0.9
            except Exception as e:
                # 异常回退
                answer = self._generate_simulated_answer(subject, topic, question, kb_results)
                confidence = 0.85
        else:
            # LLM不可用，使用模拟模式
            answer = self._generate_simulated_answer(subject, topic, question, kb_results)
            confidence = 0.92
        
        return AgentResult(
            task_id=task.id,
            agent_id=self.agent_id,
            content={"answer": answer.strip(), "references": kb_results},
            confidence=confidence,
            reasoning="基于知识库检索和问题分析生成解答"
        )
    
    def _generate_simulated_answer(self, subject: str, topic: str, question: str, kb_results: List[Dict]) -> str:
        """生成模拟回答（回退方案）"""
        return f"""
针对您关于【{subject}-{topic}】的问题，我的解答如下：

【问题分析】
{question}

【核心知识点】
{kb_results[0]['content']}

【解题思路】
1. 首先理解基本概念
2. 应用相关定理公式
3. 逐步推导求解

【注意事项】
- 注意公式的适用条件
- 检查计算过程中的符号
- 验证答案的合理性

【拓展练习】
已为您推荐3道同类练习题进行巩固。
        """.strip()

class PlanningAgent(Agent):
    """规划Agent - 制定学习计划，动态调整优先级"""
    
    def __init__(self):
        super().__init__(AgentType.PLANNING)
        self.tools = [
            StudentProfileTool(),
            ResourceRecommendationTool()
        ]
    
    def process(self, task: Task, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """处理规划任务"""
        intent = task.intent
        user_id = context.get("user_id") if context else "test_user"
        duration = intent.entities.get("duration", "week")
        
        # 1. 获取学生画像
        profile = self.invoke_tool("student_profile", user_id=user_id)
        weak_points = profile["weak_points"]
        
        # 2. 生成学习计划
        plan = self._generate_plan(weak_points, duration, profile["learning_style"])
        
        return AgentResult(
            task_id=task.id,
            agent_id=self.agent_id,
            content={"plan": plan, "profile_summary": profile},
            confidence=0.88,
            reasoning="基于学生画像和学习风格生成个性化计划"
        )
    
    def _generate_plan(self, weak_points: List[str], duration: str, learning_style: str) -> Dict[str, Any]:
        """生成学习计划"""
        days = {"day": 1, "week": 7, "month": 30}[duration]
        
        plan = {
            "duration": duration,
            "learning_style": learning_style,
            "goals": weak_points,
            "daily_schedule": []
        }
        
        for day in range(1, min(days, 7) + 1):
            goal = weak_points[(day - 1) % len(weak_points)]
            plan["daily_schedule"].append({
                "day": day,
                "focus_goal": goal,
                "tasks": [
                    {"time": "09:00-10:00", "activity": f"{goal} 视频学习"},
                    {"time": "10:30-11:30", "activity": f"{goal} 练习题巩固"},
                    {"time": "14:00-15:00", "activity": f"{goal} 错题回顾"}
                ]
            })
        
        return plan

class GradingAgent(Agent):
    """批改Agent - 批改主观题、作文、代码"""
    
    def __init__(self):
        super().__init__(AgentType.GRADING)
        self.tools = [ExerciseBankSearchTool()]
    
    def process(self, task: Task, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """处理批改任务"""
        intent = task.intent
        subject = intent.entities.get("subject")
        question_type = intent.entities.get("type", "subjective")
        user_answer = intent.entities.get("answer")
        correct_answer = intent.entities.get("correct_answer")
        
        # 评估答案
        score, feedback = self._evaluate_answer(user_answer, correct_answer, question_type)
        
        return AgentResult(
            task_id=task.id,
            agent_id=self.agent_id,
            content={
                "score": score,
                "feedback": feedback,
                "analysis": self._analyze_error_type(user_answer, correct_answer)
            },
            confidence=0.9,
            reasoning="基于答案对比和错误分析进行批改"
        )
    
    def _evaluate_answer(self, user_answer: str, correct_answer: str, question_type: str) -> tuple:
        """评估答案"""
        if not user_answer:
            return 0, "未作答"
        
        if user_answer == correct_answer:
            return 100, "回答完全正确！"
        
        # 相似度匹配
        similarity = self._calculate_similarity(user_answer, correct_answer)
        if similarity > 0.8:
            return 90, "回答基本正确，细节需完善"
        elif similarity > 0.6:
            return 70, "回答有一定正确性，但存在错误"
        elif similarity > 0.4:
            return 50, "回答部分正确"
        else:
            return 30, "回答错误较多，建议复习相关知识点"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 and not words2:
            return 1.0
        common = words1 & words2
        return len(common) / max(len(words1), len(words2))
    
    def _analyze_error_type(self, user_answer: str, correct_answer: str) -> Dict[str, Any]:
        """分析错误类型"""
        return {
            "error_type": "conceptual",
            "suggestion": "建议回顾基础概念，理解核心原理",
            "similar_questions": 3
        }

class CompanionAgent(Agent):
    """陪伴Agent - 情感支持、学习动力激励"""
    
    def __init__(self):
        super().__init__(AgentType.COMPANION)
        self.tools = [StudentProfileTool()]
    
    def process(self, task: Task, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """处理陪伴任务"""
        intent = task.intent
        emotion = intent.emotion_tag or "neutral"
        
        # 生成回应
        response = self._generate_response(emotion, intent.raw_input)
        
        return AgentResult(
            task_id=task.id,
            agent_id=self.agent_id,
            content={"response": response, "emotion_detected": emotion},
            confidence=0.85,
            reasoning="基于情绪分析生成支持性回应"
        )
    
    def _generate_response(self, emotion: str, input_text: str) -> str:
        """生成陪伴回应"""
        responses = {
            "anxious": "我理解你现在可能感到有些焦虑，但请相信自己的能力！每一步努力都在积累，保持专注，你一定可以克服困难的。需要我帮你制定一个更轻松的学习计划吗？",
            "frustrated": "遇到困难是学习中很正常的事情，不要灰心！让我们一起分析问题出在哪里，找到解决方法。你愿意和我说说具体遇到了什么问题吗？",
            "tired": "学习了这么久，确实辛苦了！适当休息是为了更好地前进。建议你先放松一下，听听音乐或做些运动，等状态好了再继续。",
            "happy": "太棒了！看到你这么开心，我也很为你高兴。继续保持这份热情，你会取得更大的进步！",
            "neutral": "你好呀！我是你的学习伙伴，随时在这里为你提供支持。今天有什么我可以帮助你的吗？"
        }
        return responses.get(emotion, responses["neutral"])

class RecommendationAgent(Agent):
    """推荐Agent - 推荐学习资源、同类题、拓展阅读"""
    
    def __init__(self):
        super().__init__(AgentType.RECOMMENDATION)
        self.tools = [
            ResourceRecommendationTool(),
            ExerciseBankSearchTool(),
            StudentProfileTool()
        ]
    
    def process(self, task: Task, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """处理推荐任务"""
        intent = task.intent
        user_id = context.get("user_id") if context else "test_user"
        topic = intent.entities.get("topic")
        
        # 获取推荐
        resources = self.invoke_tool("resource_recommendation", user_id=user_id, topic=topic)
        exercises = self.invoke_tool("exercise_bank_search", subject="综合", topic=topic)
        
        return AgentResult(
            task_id=task.id,
            agent_id=self.agent_id,
            content={
                "topic": topic,
                "resources": resources,
                "exercises": exercises,
                "reason": f"因为你在{topic}相关知识点上需要加强，推荐这些资源帮助你巩固"
            },
            confidence=0.88,
            reasoning="基于学生画像和目标知识点生成推荐"
        )

class AnalyticsAgent(Agent):
    """分析Agent - 学情分析、知识图谱构建、学习效果归因"""
    
    def __init__(self):
        super().__init__(AgentType.ANALYTICS)
        self.tools = [StudentProfileTool()]
    
    def process(self, task: Task, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """处理分析任务"""
        intent = task.intent
        user_id = context.get("user_id") if context else "test_user"
        period = intent.entities.get("period", "week")
        
        # 获取学生画像和分析
        profile = self.invoke_tool("student_profile", user_id=user_id)
        report = self._generate_report(profile, period)
        
        return AgentResult(
            task_id=task.id,
            agent_id=self.agent_id,
            content={"report": report, "period": period},
            confidence=0.9,
            reasoning="基于学生数据生成综合分析报告"
        )
    
    def _generate_report(self, profile: Dict[str, Any], period: str) -> Dict[str, Any]:
        """生成分析报告"""
        return {
            "period": period,
            "overview": {
                "total_learning_hours": 15,
                "completed_tasks": 28,
                "improvement_rate": 8
            },
            "subject_analysis": profile["recent_performance"],
            "weak_points": profile["weak_points"],
            "strong_points": ["英语-阅读理解", "数学-代数"],
            "suggestions": [
                "建议加强数学-导数的练习",
                "物理-力学需要更多基础知识巩固",
                "英语保持良好状态，可适当拓展"
            ],
            "trend": "整体呈上升趋势，继续保持！"
        }

# ================ 调度中心组件 ================

class IntentRecognizer:
    """意图识别器"""
    
    def recognize(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        """识别意图"""
        input_lower = user_input.lower()

        # 陪伴/情感类优先匹配（情绪问题需要优先处理）
        if any(keyword in input_lower for keyword in [
            "考砸", "难过", "压力", "焦虑", "崩溃", "不想学", "放弃",
            "好难", "心烦", "担心", "害怕", "好累", "心累", "烦躁",
            "丧", "迷茫", "没信心", "学不动", "加油", "鼓励", "支持",
            "抑郁", "绝望", "受不了", "学不进去"
        ]):
            return self._parse_companion_intent(user_input)

        # 规则匹配
        if any(keyword in input_lower for keyword in [
            "怎么办", "不懂", "不会", "解释", "什么是", "为什么",
            "怎么做", "求解", "怎么算", "如何", "解答", "讲解", "教我",
            "这道题", "公式", "定理", "概念", "什么意思", "讲一下",
            "帮我看看", "帮我看", "帮我解答", "题目"
        ]):
            return self._parse_help_intent(user_input)
        elif any(keyword in input_lower for keyword in [
            "计划", "安排", "学习计划", "时间表", "复习", "备考",
            "预习", "规划", "怎么学", "怎么复习", "日程"
        ]):
            return self._parse_plan_intent(user_input)
        elif any(keyword in input_lower for keyword in [
            "批改", "评分", "答案", "对吗", "改一下", "帮我改",
            "批一下", "打分", "评价"
        ]):
            return self._parse_grading_intent(user_input)
        elif any(keyword in input_lower for keyword in [
            "推荐", "资源", "资料", "练习题", "适合", "有没有", "找一下"
        ]):
            return self._parse_recommend_intent(user_input)
        elif any(keyword in input_lower for keyword in [
            "分析", "报告", "成绩", "表现", "下降", "进步", "退步",
            "学习情况", "学情", "统计"
        ]):
            return self._parse_analysis_intent(user_input)

        return Intent(
            intent_type=IntentType.UNKNOWN,
            entities={},
            raw_input=user_input
        )
    
    def _parse_help_intent(self, user_input: str) -> Intent:
        """解析求助意图"""
        entities = {}
        
        # 提取学科
        subjects = {"数学", "物理", "化学", "英语", "语文", "生物", "历史", "地理"}
        for subject in subjects:
            if subject in user_input:
                entities["subject"] = subject
                break
        
        # 提取知识点
        topics = {"导数", "积分", "力学", "电磁", "语法", "阅读", "作文"}
        for topic in topics:
            if topic in user_input:
                entities["topic"] = topic
                break
        
        # 检测情绪
        if any(word in user_input for word in ["总是错", "不会", "不懂"]):
            emotion = "anxious"
        else:
            emotion = "neutral"
        
        return Intent(
            intent_type=IntentType.HELP,
            entities=entities,
            urgency="high" if emotion == "anxious" else "normal",
            preferred_agent="qa",
            emotion_tag=emotion,
            raw_input=user_input
        )
    
    def _parse_plan_intent(self, user_input: str) -> Intent:
        """解析规划意图"""
        entities = {}
        
        # 提取时间范围
        if "周" in user_input or "一周" in user_input:
            entities["duration"] = "week"
        elif "月" in user_input or "一个月" in user_input:
            entities["duration"] = "month"
        else:
            entities["duration"] = "day"
        
        return Intent(
            intent_type=IntentType.PLAN,
            entities=entities,
            preferred_agent="planning",
            raw_input=user_input
        )
    
    def _parse_grading_intent(self, user_input: str) -> Intent:
        """解析批改意图"""
        entities = {"type": "subjective"}
        
        subjects = {"数学", "物理", "化学", "英语"}
        for subject in subjects:
            if subject in user_input:
                entities["subject"] = subject
                break
        
        return Intent(
            intent_type=IntentType.GRADING,
            entities=entities,
            preferred_agent="grading",
            raw_input=user_input
        )
    
    def _parse_recommend_intent(self, user_input: str) -> Intent:
        """解析推荐意图"""
        entities = {}
        
        subjects = {"数学", "物理", "化学", "英语"}
        for subject in subjects:
            if subject in user_input:
                entities["topic"] = subject
                break
        
        return Intent(
            intent_type=IntentType.RECOMMEND,
            entities=entities,
            preferred_agent="recommendation",
            raw_input=user_input
        )
    
    def _parse_analysis_intent(self, user_input: str) -> Intent:
        """解析分析意图"""
        entities = {"period": "week"}
        
        if "月" in user_input:
            entities["period"] = "month"
        
        return Intent(
            intent_type=IntentType.ANALYSIS,
            entities=entities,
            preferred_agent="analytics",
            raw_input=user_input
        )
    
    def _parse_companion_intent(self, user_input: str) -> Intent:
        """解析陪伴意图"""
        emotion = "neutral"
        if "累" in user_input or "烦" in user_input:
            emotion = "tired"
        elif "加油" in user_input or "努力" in user_input:
            emotion = "motivated"
        
        return Intent(
            intent_type=IntentType.COMPANION,
            entities={},
            preferred_agent="companion",
            emotion_tag=emotion,
            raw_input=user_input
        )

class TaskDecomposer:
    """任务分解器"""
    
    def decompose(self, intent: Intent, context: Dict[str, Any]) -> List[Task]:
        """分解任务为子任务"""
        tasks = []
        
        if intent.intent_type == IntentType.HELP:
            # 简单问答：直接分配给答疑Agent
            task = Task(
                id=f"task_{str(uuid.uuid4())[:8]}",
                intent=intent,
                assigned_agent="qa"
            )
            tasks.append(task)
        
        elif intent.intent_type == IntentType.PLAN:
            # 规划任务：规划Agent主导
            main_task = Task(
                id=f"task_{str(uuid.uuid4())[:8]}",
                intent=intent,
                assigned_agent="planning"
            )
            tasks.append(main_task)
            
            # 子任务：获取学生画像、推荐资源
            subtask1 = Task(
                id=f"task_{str(uuid.uuid4())[:8]}",
                intent=Intent(IntentType.ANALYSIS, entities={"period": "recent"}),
                parent_task_id=main_task.id,
                assigned_agent="analytics"
            )
            subtask2 = Task(
                id=f"task_{str(uuid.uuid4())[:8]}",
                intent=Intent(IntentType.RECOMMEND, entities=intent.entities),
                parent_task_id=main_task.id,
                assigned_agent="recommendation"
            )
            tasks.extend([subtask1, subtask2])
            main_task.subtasks = [subtask1, subtask2]
        
        elif intent.intent_type == IntentType.GRADING:
            # 批改任务
            task = Task(
                id=f"task_{str(uuid.uuid4())[:8]}",
                intent=intent,
                assigned_agent="grading"
            )
            tasks.append(task)
            
            # 推荐强化练习
            subtask = Task(
                id=f"task_{str(uuid.uuid4())[:8]}",
                intent=Intent(IntentType.RECOMMEND, entities=intent.entities),
                parent_task_id=task.id,
                assigned_agent="recommendation"
            )
            tasks.append(subtask)
            task.subtasks = [subtask]
        
        else:
            # 其他任务
            agent_mapping = {
                IntentType.COMPANION: "companion",
                IntentType.RECOMMEND: "recommendation",
                IntentType.ANALYSIS: "analytics"
            }
            agent = agent_mapping.get(intent.intent_type, "qa")
            
            task = Task(
                id=f"task_{str(uuid.uuid4())[:8]}",
                intent=intent,
                assigned_agent=agent
            )
            tasks.append(task)
        
        return tasks

class StateManager:
    """状态管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def create_session(self, user_id: str) -> SessionState:
        """创建会话"""
        session = SessionState(
            session_id=f"session_{str(uuid.uuid4())[:8]}",
            user_id=user_id
        )
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """更新会话"""
        session = self.sessions.get(session_id)
        if session:
            for key, value in updates.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.last_active_at = datetime.utcnow()
    
    def add_task(self, session_id: str, task: Task):
        """添加任务"""
        session = self.sessions.get(session_id)
        if session:
            session.tasks.append(task)
            session.last_active_at = datetime.utcnow()
    
    def update_task_status(self, session_id: str, task_id: str, status: TaskStatus):
        """更新任务状态"""
        session = self.sessions.get(session_id)
        if session:
            for task in session.tasks:
                if task.id == task_id:
                    task.status = status
                    task.updated_at = datetime.utcnow()
                    break
    
    def close_session(self, session_id: str):
        """关闭会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]

class MemoryRetriever:
    """记忆检索器"""
    
    def __init__(self):
        self.short_term_memory: Dict[str, List[Dict[str, Any]]] = {}
        self.long_term_memory: Dict[str, Dict[str, Any]] = {}
    
    def add_short_term_memory(self, session_id: str, content: Dict[str, Any]):
        """添加短期记忆"""
        if session_id not in self.short_term_memory:
            self.short_term_memory[session_id] = []
        self.short_term_memory[session_id].append(content)
        # 保留最近10条
        if len(self.short_term_memory[session_id]) > 10:
            self.short_term_memory[session_id] = self.short_term_memory[session_id][-10:]
    
    def get_short_term_memory(self, session_id: str) -> List[Dict[str, Any]]:
        """获取短期记忆"""
        return self.short_term_memory.get(session_id, [])
    
    def add_long_term_memory(self, user_id: str, key: str, value: Any):
        """添加长期记忆"""
        if user_id not in self.long_term_memory:
            self.long_term_memory[user_id] = {}
        self.long_term_memory[user_id][key] = value
    
    def get_long_term_memory(self, user_id: str, key: Optional[str] = None) -> Any:
        """获取长期记忆"""
        if user_id not in self.long_term_memory:
            return {}
        if key:
            return self.long_term_memory[user_id].get(key)
        return self.long_term_memory[user_id]
    
    def retrieve_relevant_memory(self, query: str, session_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """检索相关记忆"""
        memory = {
            "short_term": [],
            "long_term": {},
            "external": {}
        }
        
        if session_id:
            memory["short_term"] = self.get_short_term_memory(session_id)
        
        if user_id:
            memory["long_term"] = self.get_long_term_memory(user_id)
        
        return memory

class ResultAggregator:
    """结果聚合器"""
    
    def __init__(self, conflict_arbiter: 'ConflictArbiter' = None):
        self.conflict_arbiter = conflict_arbiter or ConflictArbiter()
    
    def aggregate(self, results: List[AgentResult]) -> Dict[str, Any]:
        """聚合多个智能体结果"""
        if len(results) == 0:
            return {"error": "无结果可聚合"}
        
        if len(results) == 1:
            return self._format_result(results[0])
        
        # 检查冲突
        conflicting_results = self._detect_conflicts(results)
        if conflicting_results:
            resolved = self.conflict_arbiter.resolve(conflicting_results)
            return self._format_result(resolved)
        
        # 合并结果
        merged = self._merge_results(results)
        return merged
    
    def _detect_conflicts(self, results: List[AgentResult]) -> List[AgentResult]:
        """检测冲突"""
        conflicts = []
        for i, r1 in enumerate(results):
            for j, r2 in enumerate(results[i+1:], i+1):
                if self._has_conflict(r1, r2):
                    conflicts.extend([r1, r2])
        return conflicts
    
    def _has_conflict(self, r1: AgentResult, r2: AgentResult) -> bool:
        """判断两个结果是否冲突"""
        if r1.confidence < 0.7 and r2.confidence < 0.7:
            return True
        # 简单的冲突检测：置信度都较低可能表示不确定
        return False
    
    def _merge_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """合并结果"""
        merged = {
            "sources": [],
            "content": {}
        }
        
        for result in results:
            merged["sources"].append({
                "agent_id": result.agent_id,
                "confidence": result.confidence,
                "reasoning": result.reasoning
            })
            
            if isinstance(result.content, dict):
                merged["content"].update(result.content)
            else:
                merged["content"][result.agent_id] = result.content
        
        return merged
    
    def _format_result(self, result: AgentResult) -> Dict[str, Any]:
        """格式化单个结果"""
        return {
            "agent_id": result.agent_id,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            **result.content
        }

class ConflictArbiter:
    """冲突仲裁器"""
    
    def resolve(self, conflicting_results: List[AgentResult]) -> AgentResult:
        """解决冲突"""
        if not conflicting_results:
            return None
        
        # 策略1：选择置信度最高的
        sorted_results = sorted(conflicting_results, key=lambda x: x.confidence, reverse=True)
        best_result = sorted_results[0]
        
        # 如果置信度都较低，进行综合
        if best_result.confidence < 0.7:
            return self._synthesize_results(conflicting_results)
        
        return best_result
    
    def _synthesize_results(self, results: List[AgentResult]) -> AgentResult:
        """综合多个结果"""
        # 简单综合：取各结果的内容合并
        content = {}
        for result in results:
            if isinstance(result.content, dict):
                content[result.agent_id] = result.content
            else:
                content[result.agent_id] = {"content": result.content}
        
        return AgentResult(
            task_id=results[0].task_id if results else "",
            agent_id="arbiter_synthesized",
            content={
                "synthesized": content,
                "note": "此结果由多个智能体综合得出，建议人工审核"
            },
            confidence=min(r.confidence for r in results) + 0.1,
            reasoning="综合多个智能体的分析结果"
        )

# ================ 智能体调度中心 ================

class AgentScheduler:
    """智能体调度中心"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.intent_recognizer = IntentRecognizer()
        self.task_decomposer = TaskDecomposer()
        self.state_manager = StateManager()
        self.memory_retriever = MemoryRetriever()
        self.result_aggregator = ResultAggregator()
        
        # 注册所有智能体
        self._register_agents()
    
    def _register_agents(self):
        """注册智能体"""
        self.agents["qa"] = QAAgent()
        self.agents["planning"] = PlanningAgent()
        self.agents["grading"] = GradingAgent()
        self.agents["companion"] = CompanionAgent()
        self.agents["recommendation"] = RecommendationAgent()
        self.agents["analytics"] = AnalyticsAgent()
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取智能体"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有智能体"""
        return [
            {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type.value,
                "tools": [t.name for t in agent.tools]
            }
            for agent in self.agents.values()
        ]
    
    async def process_request(self, user_input: str, user_id: str, 
                             session_id: Optional[str] = None) -> Dict[str, Any]:
        """处理用户请求"""
        # 1. 创建或获取会话
        if not session_id:
            session = self.state_manager.create_session(user_id)
            session_id = session.session_id
        else:
            session = self.state_manager.get_session(session_id)
            if not session:
                session = self.state_manager.create_session(user_id)
                session_id = session.session_id
        
        # 2. 识别意图
        context = self.memory_retriever.retrieve_relevant_memory(user_input, session_id, user_id)
        intent = self.intent_recognizer.recognize(user_input, context)
        
        # 3. 分解任务
        tasks = self.task_decomposer.decompose(intent, {"user_id": user_id})
        
        # 4. 添加任务到会话
        for task in tasks:
            self.state_manager.add_task(session_id, task)
        
        # 5. 执行任务（并行执行）
        results = await self._execute_tasks(tasks, user_id)
        
        # 6. 聚合结果
        final_result = self.result_aggregator.aggregate(results)
        
        # 7. 更新记忆
        self.memory_retriever.add_short_term_memory(session_id, {
            "input": user_input,
            "intent": intent.intent_type.value,
            "result_summary": str(final_result)[:200]
        })
        
        # 8. 更新状态
        self.state_manager.update_session(session_id, {
            "last_active_at": datetime.utcnow()
        })
        
        return {
            "session_id": session_id,
            "intent": intent.intent_type.value,
            "result": final_result,
            "tasks_executed": len(tasks)
        }
    
    async def _execute_tasks(self, tasks: List[Task], user_id: str) -> List[AgentResult]:
        """执行任务"""
        results = []
        
        # 并行执行独立任务
        independent_tasks = [t for t in tasks if not t.parent_task_id]
        dependent_tasks = [t for t in tasks if t.parent_task_id]
        
        # 执行独立任务
        for task in independent_tasks:
            result = await self._execute_task(task, user_id)
            results.append(result)
        
        # 执行依赖任务
        for task in dependent_tasks:
            result = await self._execute_task(task, user_id)
            results.append(result)
        
        return results
    
    async def _execute_task(self, task: Task, user_id: str) -> AgentResult:
        """执行单个任务"""
        agent = self.get_agent(task.assigned_agent)
        if not agent:
            return AgentResult(
                task_id=task.id,
                agent_id="unknown",
                content={"error": f"智能体 {task.assigned_agent} 不存在"},
                confidence=0.0
            )
        
        # 更新任务状态
        task.status = TaskStatus.EXECUTING
        
        # 执行
        try:
            result = agent.process(task, {"user_id": user_id})
            task.status = TaskStatus.COMPLETED
            task.result = result.content
        except Exception as e:
            result = AgentResult(
                task_id=task.id,
                agent_id=agent.agent_id,
                content={"error": str(e)},
                confidence=0.0
            )
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        task.updated_at = datetime.utcnow()
        return result

# ================ 全局调度中心实例 ================

# 创建全局调度中心
agent_scheduler = AgentScheduler()

# ================ 便捷函数 ================

async def ask_agent(user_input: str, user_id: str = "default_user", 
                   session_id: Optional[str] = None) -> Dict[str, Any]:
    """便捷函数：向智能体提问"""
    return await agent_scheduler.process_request(user_input, user_id, session_id)

def list_all_agents() -> List[Dict[str, Any]]:
    """便捷函数：列出所有智能体"""
    return agent_scheduler.list_agents()

if __name__ == "__main__":
    # 测试代码
    import asyncio
    
    async def test():
        print("🚀 智能体系统测试")
        print("="*60)
        
        # 测试1: 列出智能体
        agents = list_all_agents()
        print(f"\n已注册智能体 ({len(agents)}个):")
        for agent in agents:
            print(f"  • {agent['agent_type']}: {agent['agent_id']}")
        
        # 测试2: 发送请求
        print("\n测试问答功能...")
        result = await ask_agent("最近数学导数总是错，怎么办", "student_001")
        print(f"会话ID: {result['session_id']}")
        print(f"识别意图: {result['intent']}")
        print(f"结果摘要: {json.dumps(result['result'], ensure_ascii=False, indent=2)[:500]}...")
        
        print("\n✅ 测试完成")
    
    asyncio.run(test())