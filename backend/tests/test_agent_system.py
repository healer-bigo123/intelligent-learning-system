"""
智能体系统单元测试

测试内容：
1. 智能体基类测试
2. 各智能体功能测试（答疑、规划、批改、陪伴、推荐、分析）
3. 调度中心组件测试（意图识别、任务分解、状态管理、记忆检索、结果聚合、冲突仲裁）
4. 智能体调度中心综合测试
"""
import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch

# 导入被测试的模块
from app.core.agent_system import (
    # 枚举类型
    IntentType,
    TaskStatus,
    AgentType,
    
    # 数据模型
    Intent,
    Task,
    AgentResult,
    SessionState,
    
    # 工具类
    KnowledgeBaseSearchTool,
    ExerciseBankSearchTool,
    StudentProfileTool,
    ResourceRecommendationTool,
    
    # 智能体类
    Agent,
    QAAgent,
    PlanningAgent,
    GradingAgent,
    CompanionAgent,
    RecommendationAgent,
    AnalyticsAgent,
    
    # 调度中心组件
    IntentRecognizer,
    TaskDecomposer,
    StateManager,
    MemoryRetriever,
    ResultAggregator,
    ConflictArbiter,
    
    # 调度中心
    AgentScheduler,
    agent_scheduler,
    ask_agent
)

# ================ 数据模型测试 ================

class TestDataModels:
    """测试数据模型"""
    
    def test_intent_creation(self):
        """测试意图对象创建"""
        intent = Intent(
            intent_type=IntentType.HELP,
            entities={"subject": "数学", "topic": "导数"},
            urgency="high",
            preferred_agent="qa",
            emotion_tag="anxious",
            raw_input="数学导数总是错"
        )
        
        assert intent.intent_type == IntentType.HELP
        assert intent.entities == {"subject": "数学", "topic": "导数"}
        assert intent.urgency == "high"
        assert intent.preferred_agent == "qa"
        assert intent.emotion_tag == "anxious"
        assert intent.raw_input == "数学导数总是错"
    
    def test_task_creation(self):
        """测试任务对象创建"""
        intent = Intent(intent_type=IntentType.HELP, entities={})
        task = Task(
            id="test_task_001",
            intent=intent,
            status=TaskStatus.EXECUTING,
            assigned_agent="qa"
        )
        
        assert task.id == "test_task_001"
        assert task.status == TaskStatus.EXECUTING
        assert task.assigned_agent == "qa"
        assert task.created_at is not None
        assert task.updated_at is not None
    
    def test_agent_result_creation(self):
        """测试智能体结果对象创建"""
        result = AgentResult(
            task_id="task_001",
            agent_id="qa_001",
            content={"answer": "测试回答"},
            confidence=0.95,
            reasoning="测试推理"
        )
        
        assert result.task_id == "task_001"
        assert result.agent_id == "qa_001"
        assert result.content == {"answer": "测试回答"}
        assert result.confidence == 0.95
        assert result.reasoning == "测试推理"

# ================ 工具类测试 ================

class TestTools:
    """测试工具类"""
    
    def test_knowledge_base_search(self):
        """测试知识库检索工具"""
        tool = KnowledgeBaseSearchTool()
        result = tool.execute(query="数学导数", top_k=3)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert "content" in result[0]
        assert "score" in result[0]
    
    def test_exercise_bank_search(self):
        """测试题库检索工具"""
        tool = ExerciseBankSearchTool()
        result = tool.execute(subject="数学", topic="导数", difficulty=3, count=5)
        
        assert isinstance(result, list)
        assert len(result) == 5
        assert result[0]["subject"] == "数学"
        assert result[0]["topic"] == "导数"
    
    def test_student_profile_tool(self):
        """测试学生画像工具"""
        tool = StudentProfileTool()
        result = tool.execute(user_id="student_001")
        
        assert isinstance(result, dict)
        assert result["user_id"] == "student_001"
        assert "weak_points" in result
        assert "learning_style" in result
    
    def test_resource_recommendation_tool(self):
        """测试资源推荐工具"""
        tool = ResourceRecommendationTool()
        result = tool.execute(user_id="student_001", topic="数学导数", count=3)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert "title" in result[0]
        assert "url" in result[0]

# ================ 智能体类测试 ================

class TestAgents:
    """测试智能体类"""
    
    def test_qa_agent(self):
        """测试答疑Agent"""
        agent = QAAgent()
        assert agent.agent_type == AgentType.QA
        
        intent = Intent(
            intent_type=IntentType.HELP,
            entities={"subject": "数学", "topic": "导数", "issue": "总是错"},
            raw_input="数学导数总是错"
        )
        task = Task(id="test_qa", intent=intent)
        
        result = agent.process(task)
        assert result.task_id == "test_qa"
        assert result.confidence > 0.8
        assert "answer" in result.content
    
    def test_planning_agent(self):
        """测试规划Agent"""
        agent = PlanningAgent()
        assert agent.agent_type == AgentType.PLANNING
        
        intent = Intent(
            intent_type=IntentType.PLAN,
            entities={"duration": "week"}
        )
        task = Task(id="test_planning", intent=intent)
        
        result = agent.process(task, {"user_id": "student_001"})
        assert result.task_id == "test_planning"
        assert "plan" in result.content
        assert "daily_schedule" in result.content["plan"]
    
    def test_grading_agent(self):
        """测试批改Agent"""
        agent = GradingAgent()
        assert agent.agent_type == AgentType.GRADING
        
        intent = Intent(
            intent_type=IntentType.GRADING,
            entities={
                "subject": "数学",
                "type": "subjective",
                "answer": "这是我的答案",
                "correct_answer": "这是正确答案"
            }
        )
        task = Task(id="test_grading", intent=intent)
        
        result = agent.process(task)
        assert result.task_id == "test_grading"
        assert "score" in result.content
        assert "feedback" in result.content
    
    def test_companion_agent(self):
        """测试陪伴Agent"""
        agent = CompanionAgent()
        assert agent.agent_type == AgentType.COMPANION
        
        intent = Intent(
            intent_type=IntentType.COMPANION,
            entities={},
            emotion_tag="anxious",
            raw_input="我好累"
        )
        task = Task(id="test_companion", intent=intent)
        
        result = agent.process(task)
        assert result.task_id == "test_companion"
        assert "response" in result.content
        assert len(result.content["response"]) > 0
    
    def test_recommendation_agent(self):
        """测试推荐Agent"""
        agent = RecommendationAgent()
        assert agent.agent_type == AgentType.RECOMMENDATION
        
        intent = Intent(
            intent_type=IntentType.RECOMMEND,
            entities={"topic": "数学导数"}
        )
        task = Task(id="test_recommend", intent=intent)
        
        result = agent.process(task, {"user_id": "student_001"})
        assert result.task_id == "test_recommend"
        assert "resources" in result.content
        assert "exercises" in result.content
    
    def test_analytics_agent(self):
        """测试分析Agent"""
        agent = AnalyticsAgent()
        assert agent.agent_type == AgentType.ANALYTICS
        
        intent = Intent(
            intent_type=IntentType.ANALYSIS,
            entities={"period": "week"}
        )
        task = Task(id="test_analytics", intent=intent)
        
        result = agent.process(task, {"user_id": "student_001"})
        assert result.task_id == "test_analytics"
        assert "report" in result.content
        assert "overview" in result.content["report"]

# ================ 调度中心组件测试 ================

class TestSchedulerComponents:
    """测试调度中心组件"""
    
    def test_intent_recognizer(self):
        """测试意图识别器"""
        recognizer = IntentRecognizer()
        
        # 测试求助意图
        intent = recognizer.recognize("数学导数总是错，怎么办")
        assert intent.intent_type == IntentType.HELP
        assert intent.entities.get("subject") == "数学"
        assert intent.preferred_agent == "qa"
        
        # 测试规划意图
        intent = recognizer.recognize("帮我制定下周学习计划")
        assert intent.intent_type == IntentType.PLAN
        assert intent.preferred_agent == "planning"
        
        # 测试陪伴意图
        intent = recognizer.recognize("我好累，需要鼓励")
        assert intent.intent_type == IntentType.COMPANION
        assert intent.preferred_agent == "companion"
    
    def test_task_decomposer(self):
        """测试任务分解器"""
        decomposer = TaskDecomposer()
        
        intent = Intent(
            intent_type=IntentType.HELP,
            entities={"subject": "数学", "topic": "导数"}
        )
        tasks = decomposer.decompose(intent, {"user_id": "student_001"})
        
        assert len(tasks) >= 1
        assert tasks[0].assigned_agent == "qa"
    
    def test_state_manager(self):
        """测试状态管理器"""
        manager = StateManager()
        
        # 创建会话
        session = manager.create_session("user_001")
        assert session.session_id is not None
        assert session.user_id == "user_001"
        
        # 获取会话
        retrieved = manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
        
        # 添加任务
        intent = Intent(intent_type=IntentType.HELP, entities={})
        task = Task(id="test_task", intent=intent)
        manager.add_task(session.session_id, task)
        
        assert len(session.tasks) == 1
        
        # 关闭会话
        manager.close_session(session.session_id)
        assert manager.get_session(session.session_id) is None
    
    def test_memory_retriever(self):
        """测试记忆检索器"""
        retriever = MemoryRetriever()
        
        # 测试短期记忆
        retriever.add_short_term_memory("session_001", {"input": "test1"})
        retriever.add_short_term_memory("session_001", {"input": "test2"})
        short_mem = retriever.get_short_term_memory("session_001")
        assert len(short_mem) == 2
        
        # 测试长期记忆
        retriever.add_long_term_memory("user_001", "weak_points", ["数学"])
        long_mem = retriever.get_long_term_memory("user_001")
        assert long_mem.get("weak_points") == ["数学"]
        
        # 测试检索
        memory = retriever.retrieve_relevant_memory(
            "测试查询", "session_001", "user_001"
        )
        assert "short_term" in memory
        assert "long_term" in memory
    
    def test_result_aggregator(self):
        """测试结果聚合器"""
        aggregator = ResultAggregator()
        
        results = [
            AgentResult(
                task_id="task_001",
                agent_id="qa_001",
                content={"answer": "回答1"},
                confidence=0.9
            ),
            AgentResult(
                task_id="task_001",
                agent_id="qa_002",
                content={"answer": "回答2"},
                confidence=0.85
            )
        ]
        
        aggregated = aggregator.aggregate(results)
        assert "sources" in aggregated
        assert "content" in aggregated
        assert len(aggregated["sources"]) == 2
    
    def test_conflict_arbiter(self):
        """测试冲突仲裁器"""
        arbiter = ConflictArbiter()
        
        # 测试冲突解决
        conflicting = [
            AgentResult(
                task_id="task_001",
                agent_id="agent_001",
                content={"result": "A"},
                confidence=0.6
            ),
            AgentResult(
                task_id="task_001",
                agent_id="agent_002",
                content={"result": "B"},
                confidence=0.55
            )
        ]
        
        resolved = arbiter.resolve(conflicting)
        assert resolved is not None
        assert resolved.agent_id == "arbiter_synthesized"

# ================ 智能体调度中心综合测试 ================

class TestAgentScheduler:
    """测试智能体调度中心"""
    
    def test_scheduler_initialization(self):
        """测试调度中心初始化"""
        scheduler = AgentScheduler()
        
        assert len(scheduler.agents) == 6
        assert "qa" in scheduler.agents
        assert "planning" in scheduler.agents
        assert "grading" in scheduler.agents
        assert "companion" in scheduler.agents
        assert "recommendation" in scheduler.agents
        assert "analytics" in scheduler.agents
    
    def test_list_agents(self):
        """测试列出智能体"""
        agents = agent_scheduler.list_agents()
        assert len(agents) == 6
        agent_types = [a["agent_type"] for a in agents]
        assert "qa" in agent_types
        assert "planning" in agent_types
    
    @pytest.mark.anyio
    async def test_process_request(self):
        """测试处理请求"""
        result = await ask_agent(
            "最近数学导数总是错，怎么办",
            "student_001"
        )
        
        assert "session_id" in result
        assert "intent" in result
        assert "result" in result
        assert result["intent"] == "求助"
    
    @pytest.mark.anyio
    async def test_process_request_with_session(self):
        """测试带会话的请求"""
        # 第一次请求创建会话
        result1 = await ask_agent(
            "帮我制定学习计划",
            "student_002"
        )
        session_id = result1["session_id"]
        
        # 第二次请求复用会话
        result2 = await ask_agent(
            "修改计划，增加数学时间",
            "student_002",
            session_id
        )
        
        assert result2["session_id"] == session_id

# ================ 端到端测试 ================

class TestEndToEnd:
    """端到端测试"""
    
    @pytest.mark.anyio
    async def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 用户提问
        user_input = "最近数学导数总是错，怎么办"
        user_id = "test_user"
        
        # 2. 处理请求
        result = await ask_agent(user_input, user_id)
        
        # 3. 验证结果
        assert result["intent"] == "求助"
        assert result["tasks_executed"] >= 1
        assert "answer" in result["result"] or "sources" in result["result"]
        
        # 4. 验证会话创建
        session = agent_scheduler.state_manager.get_session(result["session_id"])
        assert session is not None
        assert session.user_id == user_id
        assert len(session.tasks) >= 1

# ================ 主函数运行测试 ================

if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])
    
    # 输出测试报告摘要
    print("\n" + "="*60)
    print("智能体系统单元测试报告")
    print("="*60)
    print(f"测试时间: {datetime.now().isoformat()}")
    print("测试模块: app.core.agent_system")
    print("测试覆盖: 数据模型、工具类、智能体、调度中心、端到端")
    print("="*60)