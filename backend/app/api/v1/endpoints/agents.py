"""
智能体管理接口

合并了原有的智能体注册表和新的智能体调度系统API
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# 导入新的智能体调度系统
from app.core.agent_system import (
    agent_scheduler,
    ask_agent,
    list_all_agents,
    Intent,
    IntentType,
    Task,
    TaskStatus,
    SessionState,
    AgentType
)

router = APIRouter()

# ================ 原有智能体注册表（保留） ================
REGISTERED_AGENTS = [
    {
        "id": "profile_analyst",
        "name": "画像分析师",
        "description": "通过对话抽取学生特征，构建动态画像",
        "status": "active"
    },
    {
        "id": "resource_designer",
        "name": "资源设计师",
        "description": "生成课程讲解文档、思维导图、拓展阅读",
        "status": "active"
    },
    {
        "id": "question_generator",
        "name": "题库生成师",
        "description": "生成不同类型练习题（选择、填空、编程等）",
        "status": "active"
    },
    {
        "id": "multimedia_creator",
        "name": "多媒体制作师",
        "description": "生成教学视频/动画脚本，调用多模态工具",
        "status": "active"
    },
    {
        "id": "code_mentor",
        "name": "代码导师",
        "description": "生成实操案例、编程项目、代码解析",
        "status": "active"
    },
    {
        "id": "path_planner",
        "name": "路径规划师",
        "description": "整合资源，规划学习路径与推送策略",
        "status": "active"
    }
]

# ================ 请求/响应模型 ================

class AgentTaskRequest(BaseModel):
    agent_id: str
    task_type: str
    parameters: Optional[Dict] = {}
    user_id: Optional[str] = None

class QueryRequest(BaseModel):
    user_input: str
    user_id: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    session_id: str
    intent: str
    result: Dict[str, Any]
    tasks_executed: int
    timestamp: datetime = datetime.utcnow()

class TaskInfo(BaseModel):
    task_id: str
    intent_type: str
    status: str
    assigned_agent: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    task_count: int
    conversation_history_count: int
    created_at: datetime
    last_active_at: datetime

# ================ 原有API（保留并增强） ================

@router.get("/")
async def list_agents():
    """获取所有已注册的智能体列表"""
    # 合并原有智能体和新调度系统的智能体
    new_agents = list_all_agents()
    combined = REGISTERED_AGENTS.copy()
    
    for agent in new_agents:
        existing = next((a for a in combined if a["id"] == agent["agent_id"]), None)
        if not existing:
            combined.append({
                "id": agent["agent_id"],
                "name": agent["agent_type"],
                "description": f"{agent['agent_type']} 智能体",
                "status": "active",
                "tools": agent["tools"]
            })
    
    return {
        "agents": combined,
        "total": len(combined)
    }

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """获取指定智能体详情"""
    # 先查找原有注册表
    agent = next((a for a in REGISTERED_AGENTS if a["id"] == agent_id), None)
    
    # 如果没找到，查找新调度系统
    if not agent:
        new_agent = agent_scheduler.get_agent(agent_id)
        if new_agent:
            return {
                "id": new_agent.agent_id,
                "name": new_agent.agent_type.value,
                "description": f"{new_agent.agent_type.value} 智能体",
                "status": "active",
                "tools": [tool.name for tool in new_agent.tools]
            }
        else:
            raise HTTPException(status_code=404, detail=f"智能体 {agent_id} 不存在")
    
    return agent

@router.post("/task")
async def dispatch_task(request: AgentTaskRequest):
    """向指定智能体派发任务"""
    agent = next((a for a in REGISTERED_AGENTS if a["id"] == request.agent_id), None)
    
    if not agent:
        # 尝试在新调度系统中查找
        new_agent = agent_scheduler.get_agent(request.agent_id)
        if not new_agent:
            return {"error": f"智能体 {request.agent_id} 不存在"}
        agent = {"id": new_agent.agent_id, "name": new_agent.agent_type.value, "status": "active"}
    
    if agent["status"] != "active":
        return {"error": f"智能体 {request.agent_id} 当前不可用"}
    
    # 使用新调度系统执行任务
    try:
        result = await ask_agent(
            f"{request.task_type}: {str(request.parameters)}",
            request.user_id or "default_user"
        )
        return {
            "task_id": result["session_id"],
            "agent_id": request.agent_id,
            "status": "completed",
            "result": result["result"],
            "message": f"任务已提交至 {agent['name']}，处理完成"
        }
    except Exception as e:
        return {
            "task_id": f"task_{request.agent_id}_{hash(str(request.parameters))}",
            "agent_id": request.agent_id,
            "status": "failed",
            "error": str(e)
        }

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    # 遍历所有会话查找任务
    for session in agent_scheduler.state_manager.sessions.values():
        for task in session.tasks:
            if task.id == task_id:
                return TaskInfo(
                    task_id=task.id,
                    intent_type=task.intent.intent_type.value,
                    status=task.status.value,
                    assigned_agent=task.assigned_agent,
                    result=task.result,
                    error=task.error,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
    
    # 模拟旧系统的任务状态
    return {
        "task_id": task_id,
        "status": "completed",
        "result": "任务执行结果（模拟数据）"
    }

# ================ 新增API：智能体调度系统接口 ================

@router.post("/query", response_model=QueryResponse, summary="向智能体调度中心发送请求")
async def query_agent(request: QueryRequest):
    """
    向智能体调度中心发送用户请求，自动识别意图并分配最佳智能体处理
    
    - **user_input**: 用户输入的自然语言查询
    - **user_id**: 用户唯一标识符
    - **session_id**: 可选的会话ID，用于保持对话上下文
    """
    try:
        result = await ask_agent(request.user_input, request.user_id, request.session_id)
        return QueryResponse(
            session_id=result["session_id"],
            intent=result["intent"],
            result=result["result"],
            tasks_executed=result["tasks_executed"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能体处理失败: {str(e)}")

# ================ 会话管理API ================

@router.post("/sessions", response_model=SessionInfo, summary="创建新会话")
async def create_session(user_id: str):
    """
    创建新的用户会话
    
    - **user_id**: 用户唯一标识符
    """
    session = agent_scheduler.state_manager.create_session(user_id)
    return SessionInfo(
        session_id=session.session_id,
        user_id=session.user_id,
        task_count=len(session.tasks),
        conversation_history_count=len(session.conversation_history),
        created_at=session.created_at,
        last_active_at=session.last_active_at
    )

@router.get("/sessions/{session_id}", response_model=SessionInfo, summary="获取会话信息")
async def get_session(session_id: str):
    """
    获取指定会话的详细信息
    
    - **session_id**: 会话ID
    """
    session = agent_scheduler.state_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    return SessionInfo(
        session_id=session.session_id,
        user_id=session.user_id,
        task_count=len(session.tasks),
        conversation_history_count=len(session.conversation_history),
        created_at=session.created_at,
        last_active_at=session.last_active_at
    )

@router.delete("/sessions/{session_id}", summary="关闭会话")
async def close_session(session_id: str):
    """
    关闭指定会话，释放相关资源
    
    - **session_id**: 会话ID
    """
    session = agent_scheduler.state_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    agent_scheduler.state_manager.close_session(session_id)
    return {"message": f"会话 {session_id} 已成功关闭"}

# ================ 任务管理API ================

@router.get("/sessions/{session_id}/tasks", response_model=List[TaskInfo], summary="获取会话中的任务列表")
async def get_session_tasks(session_id: str):
    """
    获取指定会话中的所有任务
    
    - **session_id**: 会话ID
    """
    session = agent_scheduler.state_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    return [
        TaskInfo(
            task_id=task.id,
            intent_type=task.intent.intent_type.value,
            status=task.status.value,
            assigned_agent=task.assigned_agent,
            result=task.result,
            error=task.error,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in session.tasks
    ]

# ================ 意图识别API ================

@router.post("/intent/recognize", summary="识别用户意图")
async def recognize_intent(user_input: str, session_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    单独调用意图识别器
    
    - **user_input**: 用户输入的自然语言
    - **session_id**: 可选的会话ID
    - **user_id**: 可选的用户ID
    """
    try:
        context = {}
        if session_id and user_id:
            context = agent_scheduler.memory_retriever.retrieve_relevant_memory(
                user_input, session_id, user_id
            )
        
        intent = agent_scheduler.intent_recognizer.recognize(user_input, context)
        
        return {
            "intent_type": intent.intent_type.value,
            "entities": intent.entities,
            "urgency": intent.urgency,
            "preferred_agent": intent.preferred_agent,
            "emotion_tag": intent.emotion_tag,
            "raw_input": intent.raw_input
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"意图识别失败: {str(e)}")

# ================ 记忆管理API ================

@router.post("/memory/short-term", summary="添加短期记忆")
async def add_short_term_memory(session_id: str, content: Dict[str, Any]):
    """
    向指定会话添加短期记忆
    
    - **session_id**: 会话ID
    - **content**: 记忆内容
    """
    agent_scheduler.memory_retriever.add_short_term_memory(session_id, content)
    return {"message": "短期记忆添加成功"}

@router.get("/memory/short-term/{session_id}", summary="获取短期记忆")
async def get_short_term_memory(session_id: str):
    """
    获取指定会话的短期记忆
    
    - **session_id**: 会话ID
    """
    memory = agent_scheduler.memory_retriever.get_short_term_memory(session_id)
    return {"session_id": session_id, "memory": memory}

@router.post("/memory/long-term", summary="添加长期记忆")
async def add_long_term_memory(user_id: str, key: str, value: Any):
    """
    向指定用户添加长期记忆
    
    - **user_id**: 用户ID
    - **key**: 记忆键
    - **value**: 记忆值
    """
    agent_scheduler.memory_retriever.add_long_term_memory(user_id, key, value)
    return {"message": "长期记忆添加成功"}

@router.get("/memory/long-term/{user_id}", summary="获取长期记忆")
async def get_long_term_memory(user_id: str, key: Optional[str] = None):
    """
    获取指定用户的长期记忆
    
    - **user_id**: 用户ID
    - **key**: 可选的记忆键，不指定则返回所有
    """
    memory = agent_scheduler.memory_retriever.get_long_term_memory(user_id, key)
    return {"user_id": user_id, "memory": memory}

# ================ 健康检查 ================

@router.get("/health", summary="智能体系统健康检查")
async def health_check():
    """
    检查智能体系统是否正常运行
    """
    return {
        "status": "healthy",
        "agents_count": len(agent_scheduler.agents),
        "sessions_count": len(agent_scheduler.state_manager.sessions),
        "timestamp": datetime.utcnow().isoformat()
    }