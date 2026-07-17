"""
课堂互动接口
"""
import uuid
import json
import random
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import (
    Classroom, ClassroomMember, Vote, Lottery, Quiz,
    LearningResource, get_db
)
from app.core.security import get_current_user_id
from app.core.llm_client import llm_client

router = APIRouter()


# ========== 请求/响应模型 ==========

class ClassroomCreateRequest(BaseModel):
    """创建课堂请求"""
    name: str = Field(..., description="课堂名称")
    description: Optional[str] = Field(None, description="课堂描述")


class ClassroomJoinRequest(BaseModel):
    """加入课堂请求"""
    code: str = Field(..., description="6位邀请码")


class VoteCreateRequest(BaseModel):
    """创建投票请求"""
    title: str = Field(..., description="投票标题")
    options: List[str] = Field(..., description="选项列表")


class VoteCastRequest(BaseModel):
    """投票请求"""
    option_index: int = Field(..., ge=0, description="选项索引")


class LotteryCreateRequest(BaseModel):
    """创建抽签请求"""
    title: str = Field(..., description="抽签标题")
    candidates: List[str] = Field(..., description="候选人列表")


class QuizCreateRequest(BaseModel):
    """创建随堂测验请求"""
    title: str = Field(..., description="测验标题")
    questions: List[dict] = Field(..., description="题目列表")


class QuizSubmitRequest(BaseModel):
    """提交测验答案请求"""
    answers: dict = Field(..., description="答案字典，key为题目索引，value为答案")


class PPTGenerateRequest(BaseModel):
    """生成PPT请求"""
    topic: str = Field(..., description="PPT主题")


class ClassroomResponse(BaseModel):
    """课堂响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: Optional[str] = None
    teacher_id: str
    status: str
    created_at: datetime
    updated_at: datetime


class ClassroomMemberResponse(BaseModel):
    """课堂成员响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    classroom_id: str
    user_id: str
    role: str
    joined_at: datetime


class ClassroomDetailResponse(BaseModel):
    """课堂详情响应"""
    id: str
    code: str
    name: str
    description: Optional[str] = None
    teacher_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    members: List[ClassroomMemberResponse]


class VoteResponse(BaseModel):
    """投票响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    classroom_id: str
    title: str
    options: str
    results: str
    status: str
    created_at: datetime
    ended_at: Optional[datetime] = None


class LotteryResponse(BaseModel):
    """抽签响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    classroom_id: str
    title: str
    candidates: str
    winner: Optional[str] = None
    created_at: datetime


class QuizResponse(BaseModel):
    """测验响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    classroom_id: str
    title: str
    questions: str
    answers: str
    status: str
    created_at: datetime


class PPTGenerateResponse(BaseModel):
    """生成课堂 PPT 响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    type: str
    content_text: Optional[str] = None
    created_at: datetime


class ClassroomListResponse(BaseModel):
    """课堂列表响应"""
    total: int
    items: List[ClassroomResponse]


# ========== 接口实现 ==========

def _generate_code() -> str:
    """生成6位邀请码"""
    return str(random.randint(100000, 999999))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ClassroomResponse)
async def create_classroom(
    request: ClassroomCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建课堂（自动生成6位邀请码）
    """
    classroom_id = str(uuid.uuid4())
    code = _generate_code()

    # 确保邀请码唯一
    while db.query(Classroom).filter(Classroom.code == code).first():
        code = _generate_code()

    classroom = Classroom(
        id=classroom_id,
        code=code,
        name=request.name,
        description=request.description,
        teacher_id=user_id,
        status="active"
    )

    db.add(classroom)
    db.commit()
    db.refresh(classroom)

    # 创建者自动加入为 teacher
    member = ClassroomMember(
        classroom_id=classroom_id,
        user_id=user_id,
        role="teacher"
    )
    db.add(member)
    db.commit()

    return classroom


@router.get("", response_model=ClassroomListResponse)
async def list_classrooms(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取我创建/加入的课堂列表
    """
    # 查询我创建的课堂
    created = db.query(Classroom).filter(Classroom.teacher_id == user_id).all()

    # 查询我加入的课堂
    joined_members = db.query(ClassroomMember).filter(
        ClassroomMember.user_id == user_id
    ).all()
    joined_classroom_ids = [m.classroom_id for m in joined_members]
    joined = db.query(Classroom).filter(Classroom.id.in_(joined_classroom_ids)).all()

    # 合并去重
    all_classrooms = {c.id: c for c in created}
    for c in joined:
        all_classrooms[c.id] = c

    items = list(all_classrooms.values())
    items.sort(key=lambda x: x.created_at, reverse=True)

    return {"total": len(items), "items": items}


@router.post("/{classroom_id}/join")
async def join_classroom(
    classroom_id: str,
    request: ClassroomJoinRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    通过邀请码加入课堂
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    if classroom.code != request.code:
        raise HTTPException(status_code=400, detail="邀请码错误")

    if classroom.status != "active":
        raise HTTPException(status_code=400, detail="课堂已关闭")

    # 检查是否已在课堂中
    existing = db.query(ClassroomMember).filter(
        ClassroomMember.classroom_id == classroom_id,
        ClassroomMember.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已在课堂中")

    member = ClassroomMember(
        classroom_id=classroom_id,
        user_id=user_id,
        role="student"
    )
    db.add(member)
    db.commit()

    return {"message": "加入课堂成功"}


@router.get("/{classroom_id}", response_model=ClassroomDetailResponse)
async def get_classroom(
    classroom_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取课堂详情（包含成员列表）
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    # 检查是否是成员
    is_member = db.query(ClassroomMember).filter(
        ClassroomMember.classroom_id == classroom_id,
        ClassroomMember.user_id == user_id
    ).first()
    if not is_member and classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="无权限查看该课堂")

    members = db.query(ClassroomMember).filter(
        ClassroomMember.classroom_id == classroom_id
    ).all()

    return {
        "id": classroom.id,
        "code": classroom.code,
        "name": classroom.name,
        "description": classroom.description,
        "teacher_id": classroom.teacher_id,
        "status": classroom.status,
        "created_at": classroom.created_at,
        "updated_at": classroom.updated_at,
        "members": members
    }


@router.post("/{classroom_id}/votes", status_code=status.HTTP_201_CREATED, response_model=VoteResponse)
async def create_vote(
    classroom_id: str,
    request: VoteCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    发起投票
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    if classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="只有老师可以发起投票")

    vote_id = str(uuid.uuid4())
    options_str = json.dumps(request.options, ensure_ascii=False)
    results = {str(i): 0 for i in range(len(request.options))}
    results_str = json.dumps(results, ensure_ascii=False)

    vote = Vote(
        id=vote_id,
        classroom_id=classroom_id,
        title=request.title,
        options=options_str,
        results=results_str,
        status="active"
    )

    db.add(vote)
    db.commit()
    db.refresh(vote)

    return vote


@router.get("/{classroom_id}/votes/{vote_id}/result")
async def get_vote_result(
    classroom_id: str,
    vote_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    查看投票结果
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    vote = db.query(Vote).filter(
        Vote.id == vote_id,
        Vote.classroom_id == classroom_id
    ).first()
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在")

    is_member = db.query(ClassroomMember).filter(
        ClassroomMember.classroom_id == classroom_id,
        ClassroomMember.user_id == user_id
    ).first()
    if not is_member and classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="无权限查看")

    options = json.loads(vote.options)
    results = json.loads(vote.results)

    return {
        "id": vote.id,
        "title": vote.title,
        "options": options,
        "results": results,
        "status": vote.status
    }


@router.post("/{classroom_id}/votes/{vote_id}/cast")
async def cast_vote(
    classroom_id: str,
    vote_id: str,
    request: VoteCastRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    投票（传入选项索引）
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    vote = db.query(Vote).filter(
        Vote.id == vote_id,
        Vote.classroom_id == classroom_id
    ).first()
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在")

    if vote.status != "active":
        raise HTTPException(status_code=400, detail="投票已结束")

    is_member = db.query(ClassroomMember).filter(
        ClassroomMember.classroom_id == classroom_id,
        ClassroomMember.user_id == user_id
    ).first()
    if not is_member and classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="无权限投票")

    options = json.loads(vote.options)
    if request.option_index < 0 or request.option_index >= len(options):
        raise HTTPException(status_code=400, detail="选项索引无效")

    results = json.loads(vote.results)
    results[str(request.option_index)] = results.get(str(request.option_index), 0) + 1
    vote.results = json.dumps(results, ensure_ascii=False)

    db.commit()
    db.refresh(vote)

    return {"message": "投票成功", "results": results}


@router.post("/{classroom_id}/lottery", status_code=status.HTTP_201_CREATED, response_model=LotteryResponse)
async def create_lottery(
    classroom_id: str,
    request: LotteryCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    随机抽签（传入候选人列表）
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    if classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="只有老师可以发起抽签")

    if not request.candidates:
        raise HTTPException(status_code=400, detail="候选人列表不能为空")

    winner = random.choice(request.candidates)
    lottery_id = str(uuid.uuid4())
    candidates_str = json.dumps(request.candidates, ensure_ascii=False)

    lottery = Lottery(
        id=lottery_id,
        classroom_id=classroom_id,
        title=request.title,
        candidates=candidates_str,
        winner=winner
    )

    db.add(lottery)
    db.commit()
    db.refresh(lottery)

    return lottery


@router.post("/{classroom_id}/quizzes", status_code=status.HTTP_201_CREATED, response_model=QuizResponse)
async def create_quiz(
    classroom_id: str,
    request: QuizCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    发起随堂测验
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    if classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="只有老师可以发起测验")

    quiz_id = str(uuid.uuid4())
    questions_str = json.dumps(request.questions, ensure_ascii=False)

    quiz = Quiz(
        id=quiz_id,
        classroom_id=classroom_id,
        title=request.title,
        questions=questions_str,
        answers="{}",
        status="active"
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return quiz


@router.post("/{classroom_id}/quizzes/{quiz_id}/submit")
async def submit_quiz(
    classroom_id: str,
    quiz_id: str,
    request: QuizSubmitRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提交测验答案
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.classroom_id == classroom_id
    ).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="测验不存在")

    if quiz.status != "active":
        raise HTTPException(status_code=400, detail="测验已结束")

    is_member = db.query(ClassroomMember).filter(
        ClassroomMember.classroom_id == classroom_id,
        ClassroomMember.user_id == user_id
    ).first()
    if not is_member and classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="无权限提交")

    answers = json.loads(quiz.answers)
    answers[user_id] = request.answers
    quiz.answers = json.dumps(answers, ensure_ascii=False)

    db.commit()
    db.refresh(quiz)

    return {"message": "提交成功"}


@router.get("/{classroom_id}/quizzes/{quiz_id}/result")
async def get_quiz_result(
    classroom_id: str,
    quiz_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    查看测验结果
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.classroom_id == classroom_id
    ).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="测验不存在")

    is_member = db.query(ClassroomMember).filter(
        ClassroomMember.classroom_id == classroom_id,
        ClassroomMember.user_id == user_id
    ).first()
    if not is_member and classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="无权限查看")

    questions = json.loads(quiz.questions)
    answers = json.loads(quiz.answers)

    return {
        "id": quiz.id,
        "title": quiz.title,
        "questions": questions,
        "answers": answers,
        "status": quiz.status
    }


@router.post("/{classroom_id}/ppt", status_code=status.HTTP_201_CREATED, response_model=PPTGenerateResponse)
async def generate_ppt(
    classroom_id: str,
    request: PPTGenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    生成课堂PPT（调用 llm_client.chat 生成PPT大纲内容，保存到 learning_resources 表，type=ppt）
    """
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="课堂不存在")

    if classroom.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="只有老师可以生成PPT")

    system_prompt = (
        "你是一位专业的教育内容生成助手，擅长根据主题生成结构清晰的PPT大纲。"
        "请严格按照以下 JSON 格式返回PPT数据，不要返回任何其他内容：\n"
        "{\n"
        '  "title": "PPT标题",\n'
        '  "slides": [\n'
        '    {"title": "第1页标题", "content": "要点1\\n要点2"},\n'
        '    {"title": "第2页标题", "content": "要点1\\n要点2"}\n'
        "  ]\n"
        "}\n"
        "要求：\n"
        "1. 内容要丰富、有教育意义\n"
        "2. 每页幻灯片包含标题和内容要点\n"
        "3. 内容使用中文"
    )

    user_prompt = f'请为课堂「{classroom.name}」生成一份关于「{request.topic}」的PPT大纲。'

    messages = llm_client.build_messages(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    try:
        response = await llm_client.chat(messages, stream=False)
        content = response["choices"][0]["message"]["content"]

        # 尝试从响应中提取 JSON
        try:
            ppt_data = json.loads(content)
        except json.JSONDecodeError:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            ppt_data = json.loads(json_str)

        title = ppt_data.get("title", f"{request.topic} PPT")
        resource_id = str(uuid.uuid4())

        resource = LearningResource(
            id=resource_id,
            title=title,
            type="ppt",
            subject="",
            content_text=json.dumps(ppt_data, ensure_ascii=False),
            user_id=user_id,
            generated_by="classroom"
        )

        db.add(resource)
        db.commit()
        db.refresh(resource)

        return resource
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PPT生成失败: {str(e)}"
        )
