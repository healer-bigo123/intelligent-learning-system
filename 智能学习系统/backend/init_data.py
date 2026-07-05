"""
数据库初始化脚本 - 填充示例数据
运行方式: cd backend && python init_data.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.database import (
    get_db, User, UserRole, StudyMaterial, Mistake, Exercise,
    Achievement, LearningPath, Classroom, ClassroomMember,
    LearningResource, StudyActivity, Notification, UserAchievement,
    ExerciseRecord, ExerciseSession, MindMap, AssessmentReport,
    LearningWebsite, StudentProfile, Favorite,
    init_db
)
from app.core.security import get_password_hash


def create_test_users(db: Session):
    """创建测试用户"""
    print("[INIT] 创建测试用户...")

    users_data = [
        {
            "id": "user-001",
            "username": "student1",
            "password": "123456",
            "email": "student1@example.com",
            "nickname": "张同学",
            "role": "student",
        },
        {
            "id": "user-002",
            "username": "teacher1",
            "password": "123456",
            "email": "teacher1@example.com",
            "nickname": "李老师",
            "role": "teacher",
        },
    ]

    for u in users_data:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if existing:
            print(f"  [SKIP] 用户已存在: {u['username']}")
            continue

        user = User(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            hashed_password=get_password_hash(u["password"]),
            nickname=u["nickname"],
            role=u["role"],
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(user)

        # 创建角色记录
        role = UserRole(
            user_id=u["id"],
            role=u["role"],
            permissions='["read", "write", "chat"]',
        )
        db.add(role)
        print(f"  [OK] 创建用户: {u['nickname']} ({u['username']})")

    db.commit()


def create_student_profiles(db: Session):
    """创建学生画像"""
    print("[INIT] 创建学生画像...")

    import json

    profiles = [
        {
            "id": "profile-001",
            "user_id": "user-001",
            "name": "张同学",
            "grade": "高一",
            "major": "理科",
            "target": "高考冲刺",
            "dimensions": json.dumps({
                "数学": {"level": 3, "score": 75},
                "英语": {"level": 2, "score": 65},
                "物理": {"level": 3, "score": 70},
                "化学": {"level": 2, "score": 60},
                "编程": {"level": 4, "score": 85},
            }),
            "knowledge_state": json.dumps({
                "数学": ["函数", "三角函数", "数列"],
                "英语": ["时态", "从句", "词汇"],
                "物理": ["力学", "电磁学"],
            }),
            "weak_points": "三角函数,英语时态,化学方程式",
            "interests": "编程,数学竞赛,物理实验",
        },
    ]

    for p in profiles:
        existing = db.query(StudentProfile).filter(StudentProfile.user_id == p["user_id"]).first()
        if existing:
            print(f"  [SKIP] 画像已存在: {p['user_id']}")
            continue

        profile = StudentProfile(**p, created_at=datetime.utcnow())
        db.add(profile)
        print(f"  [OK] 创建画像: {p['name']}")

    db.commit()


def create_study_materials(db: Session):
    """创建学习资料"""
    print("[INIT] 创建学习资料...")

    materials = [
        {
            "user_id": "user-001",
            "title": "三角函数诱导公式大全",
            "content": "诱导公式是三角函数中的重要公式，用于将任意角的三角函数转化为锐角三角函数。\n\n基本诱导公式：\n1. sin(-a) = -sin(a)\n2. cos(-a) = cos(a)\n3. sin(π-a) = sin(a)\n4. cos(π-a) = -cos(a)\n5. sin(π/2-a) = cos(a)\n6. cos(π/2-a) = sin(a)\n\n记忆口诀：奇变偶不变，符号看象限。",
            "subject": "数学",
            "grade": "高一",
            "material_type": "公式",
            "knowledge_point": "三角函数",
            "tags": "高考,重点,公式",
            "source": "人教版教材",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "一元二次方程求根公式推导",
            "content": "一元二次方程 ax² + bx + c = 0 (a≠0) 的求根公式：\n\nx = (-b ± √(b²-4ac)) / 2a\n\n推导过程：\n1. 方程两边除以 a：x² + (b/a)x + c/a = 0\n2. 配方：x² + (b/a)x = -(c/a)\n3. x² + (b/a)x + (b/2a)² = (b/2a)² - c/a\n4. (x + b/2a)² = (b²-4ac)/4a²\n5. 开方得求根公式\n\n判别式 Δ = b²-4ac\n- Δ > 0：两个不等实根\n- Δ = 0：两个相等实根\n- Δ < 0：无实根",
            "subject": "数学",
            "grade": "初三",
            "material_type": "知识点",
            "knowledge_point": "一元二次方程",
            "tags": "中考,重点,推导",
            "source": "课堂笔记",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "英语时态总结：一般现在时 vs 现在进行时",
            "content": "一般现在时：\n- 表示经常性、习惯性的动作\n- 结构：主语 + 动词原形/第三人称单数\n- 例句：I play basketball every day.\n\n现在进行时：\n- 表示此时此刻正在进行的动作\n- 结构：主语 + am/is/are + doing\n- 例句：I am playing basketball now.\n\n时间标志词：\n- 一般现在时：always, usually, often, every day\n- 现在进行时：now, at the moment, look, listen",
            "subject": "英语",
            "grade": "初一",
            "material_type": "知识点",
            "knowledge_point": "时态",
            "tags": "基础,语法,对比",
            "source": "网络整理",
            "difficulty": 1,
        },
        {
            "user_id": "user-001",
            "title": "牛顿三大定律",
            "content": "第一定律（惯性定律）：\n一切物体在没有受到外力作用时，总保持静止或匀速直线运动状态。\n\n第二定律（加速度定律）：\nF = ma，物体的加速度与所受合力成正比，与质量成反比。\n\n第三定律（作用力与反作用力）：\n两个物体之间的作用力和反作用力总是大小相等、方向相反、作用在同一条直线上。\n\n应用示例：\n- 第一定律：汽车急刹车时乘客向前倾\n- 第二定律：推箱子，力越大加速度越大\n- 第三定律：人走路时脚向后蹬地，地给人向前的力",
            "subject": "物理",
            "grade": "高一",
            "material_type": "知识点",
            "knowledge_point": "力学",
            "tags": "高考,重点,定律",
            "source": "人教版教材",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "化学方程式配平方法",
            "content": "1. 最小公倍数法\n找出左右两边各出现一次且原子个数相差较大的元素，求最小公倍数。\n\n2. 奇数配偶法\n某元素在方程式两边一奇一偶时，将奇数配成偶数。\n\n3. 观察法\n从复杂的化学式入手，推断其他物质的系数。\n\n4. 归一法\n令最复杂物质的系数为1，再推导其他物质。\n\n例：配平 C₂H₆ + O₂ → CO₂ + H₂O\n解：令 C₂H₆ 系数为 1，则 CO₂ 为 2，H₂O 为 3，O₂ 为 7/2，同乘 2 得：\n2C₂H₆ + 7O₂ → 4CO₂ + 6H₂O",
            "subject": "化学",
            "grade": "初三",
            "material_type": "例题",
            "knowledge_point": "化学方程式",
            "tags": "中考,技巧,配平",
            "source": "整理",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "细胞的基本结构",
            "content": "动物细胞结构：\n1. 细胞膜：控制物质进出\n2. 细胞质：细胞代谢的主要场所\n3. 细胞核：含有遗传物质，控制细胞生命活动\n\n植物细胞特有结构：\n1. 细胞壁：支持和保护作用\n2. 叶绿体：光合作用的场所\n3. 液泡：储存物质，维持细胞形态\n\n细胞器功能：\n- 线粒体：有氧呼吸的主要场所，动力车间\n- 核糖体：合成蛋白质\n- 内质网：蛋白质加工和运输\n- 高尔基体：蛋白质加工、分类、包装",
            "subject": "生物",
            "grade": "初一",
            "material_type": "知识点",
            "knowledge_point": "细胞",
            "tags": "基础,结构,对比",
            "source": "人教版教材",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "中国朝代顺序歌",
            "content": "夏商与西周，东周分两段。\n春秋和战国，一统秦两汉。\n三分魏蜀吴，二晋前后延。\n南北朝并立，隋唐五代传。\n宋元明清后，皇朝至此完。\n\n重要朝代记忆点：\n- 夏朝：中国第一个奴隶制王朝\n- 秦朝：第一个统一的封建王朝，秦始皇\n- 唐朝：贞观之治、开元盛世\n- 宋朝：经济文化繁荣，但军事较弱\n- 明朝：郑和下西洋\n- 清朝：中国最后一个封建王朝",
            "subject": "历史",
            "grade": "初一",
            "material_type": "笔记",
            "knowledge_point": "朝代",
            "tags": "基础,记忆,口诀",
            "source": "网络",
            "difficulty": 1,
        },
        {
            "user_id": "user-001",
            "title": "Python 列表推导式",
            "content": "列表推导式是 Python 中简洁创建列表的方式。\n\n基本语法：\n[表达式 for 变量 in 可迭代对象 if 条件]\n\n示例：\n1. 创建平方数列表\n   squares = [x**2 for x in range(10)]\n   # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]\n\n2. 筛选偶数\n   evens = [x for x in range(20) if x % 2 == 0]\n\n3. 嵌套循环\n   pairs = [(x, y) for x in range(3) for y in range(3)]\n\n优点：代码简洁、执行效率高\n注意：过于复杂的推导式会降低可读性",
            "subject": "编程",
            "grade": "大学",
            "material_type": "知识点",
            "knowledge_point": "Python基础",
            "tags": "编程,Python,技巧",
            "source": "教程",
            "difficulty": 2,
        },
    ]

    for i, m in enumerate(materials):
        existing = db.query(StudyMaterial).filter(StudyMaterial.title == m["title"]).first()
        if existing:
            print(f"  [SKIP] 资料已存在: {m['title']}")
            continue

        material = StudyMaterial(
            id=f"material-{i+1:03d}",
            **m,
            views=0,
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(material)
        print(f"  [OK] 创建资料: {m['title']}")

    db.commit()


def create_learning_resources(db: Session):
    """创建学习资源（视频/文档/测验等）"""
    print("[INIT] 创建学习资源...")

    resources = [
        {
            "user_id": "user-001",
            "title": "三角函数动画演示",
            "type": "video",
            "subject": "数学",
            "topics": "三角函数,诱导公式",
            "difficulty": 3,
            "duration": 15,
            "content_text": "通过动画演示三角函数在单位圆上的变化规律",
            "generated_by": "recommendation-agent",
        },
        {
            "user_id": "user-001",
            "title": "英语时态专项练习",
            "type": "quiz",
            "subject": "英语",
            "topics": "时态,语法",
            "difficulty": 2,
            "duration": 20,
            "content_text": "包含30道时态选择题，覆盖一般现在时、进行时、完成时",
            "generated_by": "question-generator",
        },
        {
            "user_id": "user-001",
            "title": "牛顿定律实验视频",
            "type": "video",
            "subject": "物理",
            "topics": "力学,牛顿定律",
            "difficulty": 3,
            "duration": 25,
            "content_text": "通过实验验证牛顿三大定律，包含数据分析",
            "generated_by": "recommendation-agent",
        },
        {
            "user_id": "user-001",
            "title": "化学方程式配平练习",
            "type": "quiz",
            "subject": "化学",
            "topics": "化学方程式,配平",
            "difficulty": 3,
            "duration": 15,
            "content_text": "20道化学方程式配平题，从简单到复杂",
            "generated_by": "question-generator",
        },
        {
            "user_id": "user-001",
            "title": "Python基础教程文档",
            "type": "document",
            "subject": "编程",
            "topics": "Python,基础语法",
            "difficulty": 1,
            "duration": 30,
            "content_text": "Python入门教程，包含变量、数据类型、控制流、函数等基础知识",
            "generated_by": "resource-designer",
        },
        {
            "user_id": "user-001",
            "title": "高考数学真题解析",
            "type": "document",
            "subject": "数学",
            "topics": "高考,综合",
            "difficulty": 5,
            "duration": 60,
            "content_text": "近5年高考数学真题详细解析，按知识点分类",
            "generated_by": "recommendation-agent",
        },
    ]

    for i, r in enumerate(resources):
        existing = db.query(LearningResource).filter(LearningResource.title == r["title"]).first()
        if existing:
            print(f"  [SKIP] 资源已存在: {r['title']}")
            continue

        resource = LearningResource(
            id=f"resource-{i+1:03d}",
            **r,
            rating=4.5,
            created_at=datetime.utcnow(),
        )
        db.add(resource)
        print(f"  [OK] 创建资源: {r['title']}")

    db.commit()


def create_mistakes(db: Session):
    """创建示例错题"""
    print("[INIT] 创建示例错题...")

    mistakes = [
        {
            "user_id": "user-001",
            "subject": "数学",
            "question": "若函数 f(x) = x² - 2x + 3，求 f(2) 的值。",
            "correct_answer": "3",
            "user_answer": "5",
            "analysis": "错误原因：代入时计算错误。f(2) = 2² - 2×2 + 3 = 4 - 4 + 3 = 3",
            "knowledge_point": "函数求值",
            "tags": "易错,计算",
            "source": "课堂练习",
            "difficulty": 2,
            "status": "unsolved",
        },
        {
            "user_id": "user-001",
            "subject": "数学",
            "question": "求解方程：2x + 5 = 13",
            "correct_answer": "x = 4",
            "user_answer": "x = 9",
            "analysis": "错误原因：移项时符号错误。正确步骤：2x = 13 - 5 = 8，x = 4",
            "knowledge_point": "一元一次方程",
            "tags": "基础,移项",
            "source": "作业",
            "difficulty": 1,
            "status": "reviewing",
        },
        {
            "user_id": "user-001",
            "subject": "英语",
            "question": "选择正确的时态：I ______ (play) basketball now.",
            "correct_answer": "am playing",
            "user_answer": "play",
            "analysis": "错误原因：now 是现在进行时的标志词，应该用 be + doing 结构。",
            "knowledge_point": "现在进行时",
            "tags": "时态,标志词",
            "source": "单元测试",
            "difficulty": 1,
            "status": "unsolved",
        },
        {
            "user_id": "user-001",
            "subject": "物理",
            "question": "一个物体质量为 2kg，受到 10N 的力，求加速度。",
            "correct_answer": "5 m/s²",
            "user_answer": "20 m/s²",
            "analysis": "错误原因：公式记错。F=ma，所以 a=F/m=10/2=5 m/s²",
            "knowledge_point": "牛顿第二定律",
            "tags": "公式,计算",
            "source": "期中考试",
            "difficulty": 2,
            "status": "mastered",
        },
        {
            "user_id": "user-001",
            "subject": "化学",
            "question": "配平化学方程式：Fe + O₂ → Fe₂O₃",
            "correct_answer": "4Fe + 3O₂ → 2Fe₂O₃",
            "user_answer": "Fe + O₂ → Fe₂O",
            "analysis": "错误原因：未配平。Fe左边1个右边2个，O左边2个右边3个。最小公倍数法：O的最小公倍数为6，所以O₂系数为3，Fe₂O₃系数为2，Fe系数为4。",
            "knowledge_point": "化学方程式配平",
            "tags": "配平,易错",
            "source": "作业",
            "difficulty": 3,
            "status": "reviewing",
        },
        {
            "user_id": "user-001",
            "subject": "数学",
            "question": "已知 sin(α) = 3/5，α 在第二象限，求 cos(α)。",
            "correct_answer": "-4/5",
            "user_answer": "4/5",
            "analysis": "错误原因：忽略了象限。第二象限 cos 为负值。由 sin²α + cos²α = 1，cos²α = 1 - 9/25 = 16/25，cos α = -4/5（第二象限取负）。",
            "knowledge_point": "三角函数",
            "tags": "象限,符号,易错",
            "source": "月考",
            "difficulty": 3,
            "status": "unsolved",
        },
    ]

    for i, m in enumerate(mistakes):
        existing = db.query(Mistake).filter(Mistake.question == m["question"]).first()
        if existing:
            print(f"  [SKIP] 错题已存在")
            continue

        mistake = Mistake(
            id=f"mistake-{i+1:03d}",
            **m,
            review_count=1,
            created_at=datetime.utcnow(),
        )
        db.add(mistake)
        print(f"  [OK] 创建错题: {m['subject']} - {m['knowledge_point']}")

    db.commit()


def create_exercises(db: Session):
    """创建示例练习题"""
    print("[INIT] 创建示例练习题...")

    exercises = [
        {
            "user_id": "user-001",
            "subject": "数学",
            "type": "choice",
            "question": "下列哪个数是质数？",
            "options": '["9", "15", "17", "21"]',
            "correct_answer": "2",
            "explanation": "17 只能被 1 和 17 整除，是质数。其他数都有其他因数。",
            "knowledge_point": "质数与合数",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "subject": "数学",
            "type": "choice",
            "question": "函数 y = 2x + 1 的图像经过哪个象限？",
            "options": '["第一、二象限", "第一、三象限", "第一、二、三象限", "全部象限"]',
            "correct_answer": "2",
            "explanation": "斜率 k=2>0，截距 b=1>0，图像经过第一、二、三象限。",
            "knowledge_point": "一次函数图像",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "subject": "英语",
            "type": "choice",
            "question": "She ______ to school every day.",
            "options": '["go", "goes", "going", "went"]',
            "correct_answer": "1",
            "explanation": "every day 表示习惯性动作，用一般现在时，主语是第三人称单数，动词加 -es。",
            "knowledge_point": "一般现在时",
            "difficulty": 1,
        },
        {
            "user_id": "user-001",
            "subject": "物理",
            "type": "fill_blank",
            "question": "光在真空中的传播速度约为 ______ m/s。",
            "options": None,
            "correct_answer": "3×10⁸",
            "explanation": "光在真空中的速度是宇宙中最快的速度，约为 3×10⁸ m/s。",
            "knowledge_point": "光学基础",
            "difficulty": 1,
        },
        {
            "user_id": "user-001",
            "subject": "化学",
            "type": "choice",
            "question": "下列物质中，属于氧化物的是？",
            "options": '["NaCl", "H₂O", "O₂", "H₂SO₄"]',
            "correct_answer": "1",
            "explanation": "氧化物是由两种元素组成，其中一种是氧元素的化合物。H₂O 由氢和氧两种元素组成，是氧化物。",
            "knowledge_point": "氧化物",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "subject": "数学",
            "type": "choice",
            "question": "等差数列 {aₙ} 中，a₁=2，d=3，则 a = ?",
            "options": '["11", "14", "17", "20"]',
            "correct_answer": "1",
            "explanation": "等差数列通项公式：aₙ = a₁ + (n-1)d。a₅ = 2 + (5-1)×3 = 2 + 12 = 14。",
            "knowledge_point": "等差数列",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "subject": "英语",
            "type": "choice",
            "question": "I have lived here ______ 2010.",
            "options": '["since", "for", "from", "at"]',
            "correct_answer": "0",
            "explanation": "since + 时间点，表示从某个时间开始一直持续到现在。for + 时间段。2010 是时间点，用 since。",
            "knowledge_point": "现在完成时",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "subject": "物理",
            "type": "choice",
            "question": "一个物体做匀速直线运动，速度为 5m/s，经过 10s 后的位移是？",
            "options": '["15m", "50m", "100m", "5m"]',
            "correct_answer": "1",
            "explanation": "匀速直线运动位移公式：s = vt = 5 × 10 = 50m。",
            "knowledge_point": "匀速直线运动",
            "difficulty": 1,
        },
    ]

    for i, e in enumerate(exercises):
        existing = db.query(Exercise).filter(Exercise.question == e["question"]).first()
        if existing:
            print(f"  [SKIP] 练习题已存在")
            continue

        exercise = Exercise(
            id=f"exercise-{i+1:03d}",
            **e,
            source="manual",
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(exercise)
        print(f"  [OK] 创建练习: {e['subject']} - {e['knowledge_point']}")

    db.commit()


def create_exercise_records_and_sessions(db: Session):
    """创建练习记录和会话（用于学习记录和统计）"""
    print("[INIT] 创建练习记录和会话...")

    now = datetime.utcnow()

    # 创建练习会话
    sessions = [
        {
            "id": "session-001",
            "user_id": "user-001",
            "title": "数学基础练习",
            "subject": "数学",
            "exercise_ids": "exercise-001,exercise-002,exercise-006",
            "total_count": 3,
            "correct_count": 2,
            "score": 67,
            "status": "completed",
            "created_at": now - timedelta(days=6, hours=2),
            "completed_at": now - timedelta(days=6, hours=1),
        },
        {
            "id": "session-002",
            "user_id": "user-001",
            "title": "英语语法测试",
            "subject": "英语",
            "exercise_ids": "exercise-003,exercise-007",
            "total_count": 2,
            "correct_count": 1,
            "score": 50,
            "status": "completed",
            "created_at": now - timedelta(days=5, hours=3),
            "completed_at": now - timedelta(days=5, hours=2),
        },
        {
            "id": "session-003",
            "user_id": "user-001",
            "title": "物理运动学练习",
            "subject": "物理",
            "exercise_ids": "exercise-004,exercise-008",
            "total_count": 2,
            "correct_count": 2,
            "score": 100,
            "status": "completed",
            "created_at": now - timedelta(days=4, hours=1),
            "completed_at": now - timedelta(days=4),
        },
        {
            "id": "session-004",
            "user_id": "user-001",
            "title": "化学基础测试",
            "subject": "化学",
            "exercise_ids": "exercise-005",
            "total_count": 1,
            "correct_count": 1,
            "score": 100,
            "status": "completed",
            "created_at": now - timedelta(days=3, hours=2),
            "completed_at": now - timedelta(days=3, hours=1),
        },
        {
            "id": "session-005",
            "user_id": "user-001",
            "title": "数学综合练习",
            "subject": "数学",
            "exercise_ids": "exercise-001,exercise-002,exercise-006",
            "total_count": 3,
            "correct_count": 3,
            "score": 100,
            "status": "completed",
            "created_at": now - timedelta(days=2, hours=1),
            "completed_at": now - timedelta(days=2),
        },
        {
            "id": "session-006",
            "user_id": "user-001",
            "title": "英语词汇测试",
            "subject": "英语",
            "exercise_ids": "exercise-003,exercise-007",
            "total_count": 2,
            "correct_count": 2,
            "score": 100,
            "status": "completed",
            "created_at": now - timedelta(days=1, hours=2),
            "completed_at": now - timedelta(days=1, hours=1),
        },
        {
            "id": "session-007",
            "user_id": "user-001",
            "title": "今日综合练习",
            "subject": "数学",
            "exercise_ids": "exercise-001,exercise-002,exercise-006,exercise-004",
            "total_count": 4,
            "correct_count": 3,
            "score": 75,
            "status": "completed",
            "created_at": now - timedelta(hours=3),
            "completed_at": now - timedelta(hours=2),
        },
    ]

    for s in sessions:
        existing = db.query(ExerciseSession).filter(ExerciseSession.id == s["id"]).first()
        if existing:
            print(f"  [SKIP] 会话已存在: {s['id']}")
            continue

        session = ExerciseSession(**s)
        db.add(session)
        print(f"  [OK] 创建会话: {s['title']}")

    # 创建练习记录
    records = [
        {"id": "record-001", "user_id": "user-001", "exercise_id": "exercise-001", "user_answer": "2", "is_correct": True, "score": 100, "time_spent": 30, "created_at": now - timedelta(days=6, hours=2)},
        {"id": "record-002", "user_id": "user-001", "exercise_id": "exercise-002", "user_answer": "2", "is_correct": True, "score": 100, "time_spent": 45, "created_at": now - timedelta(days=6, hours=2)},
        {"id": "record-003", "user_id": "user-001", "exercise_id": "exercise-006", "user_answer": "0", "is_correct": False, "score": 0, "time_spent": 60, "created_at": now - timedelta(days=6, hours=1)},
        {"id": "record-004", "user_id": "user-001", "exercise_id": "exercise-003", "user_answer": "1", "is_correct": True, "score": 100, "time_spent": 20, "created_at": now - timedelta(days=5, hours=3)},
        {"id": "record-005", "user_id": "user-001", "exercise_id": "exercise-007", "user_answer": "0", "is_correct": False, "score": 0, "time_spent": 35, "created_at": now - timedelta(days=5, hours=2)},
        {"id": "record-006", "user_id": "user-001", "exercise_id": "exercise-004", "user_answer": "3×10⁸", "is_correct": True, "score": 100, "time_spent": 15, "created_at": now - timedelta(days=4, hours=1)},
        {"id": "record-007", "user_id": "user-001", "exercise_id": "exercise-008", "user_answer": "1", "is_correct": True, "score": 100, "time_spent": 25, "created_at": now - timedelta(days=4)},
        {"id": "record-008", "user_id": "user-001", "exercise_id": "exercise-005", "user_answer": "1", "is_correct": True, "score": 100, "time_spent": 20, "created_at": now - timedelta(days=3, hours=2)},
        {"id": "record-009", "user_id": "user-001", "exercise_id": "exercise-001", "user_answer": "2", "is_correct": True, "score": 100, "time_spent": 25, "created_at": now - timedelta(days=2, hours=1)},
        {"id": "record-010", "user_id": "user-001", "exercise_id": "exercise-002", "user_answer": "2", "is_correct": True, "score": 100, "time_spent": 40, "created_at": now - timedelta(days=2, hours=1)},
        {"id": "record-011", "user_id": "user-001", "exercise_id": "exercise-006", "user_answer": "1", "is_correct": True, "score": 100, "time_spent": 35, "created_at": now - timedelta(days=2)},
        {"id": "record-012", "user_id": "user-001", "exercise_id": "exercise-003", "user_answer": "1", "is_correct": True, "score": 100, "time_spent": 15, "created_at": now - timedelta(days=1, hours=2)},
        {"id": "record-013", "user_id": "user-001", "exercise_id": "exercise-007", "user_answer": "0", "is_correct": True, "score": 100, "time_spent": 30, "created_at": now - timedelta(days=1, hours=1)},
        {"id": "record-014", "user_id": "user-001", "exercise_id": "exercise-001", "user_answer": "2", "is_correct": True, "score": 100, "time_spent": 20, "created_at": now - timedelta(hours=3)},
        {"id": "record-015", "user_id": "user-001", "exercise_id": "exercise-002", "user_answer": "2", "is_correct": True, "score": 100, "time_spent": 35, "created_at": now - timedelta(hours=3)},
        {"id": "record-016", "user_id": "user-001", "exercise_id": "exercise-006", "user_answer": "1", "is_correct": True, "score": 100, "time_spent": 40, "created_at": now - timedelta(hours=2)},
        {"id": "record-017", "user_id": "user-001", "exercise_id": "exercise-004", "user_answer": "50", "is_correct": False, "score": 0, "time_spent": 50, "created_at": now - timedelta(hours=2)},
    ]

    for r in records:
        existing = db.query(ExerciseRecord).filter(ExerciseRecord.id == r["id"]).first()
        if existing:
            continue
        record = ExerciseRecord(**r)
        db.add(record)

    db.commit()
    print(f"  [OK] 创建 {len(records)} 条练习记录")


def create_study_activities(db: Session):
    """创建学习活动记录（用于时间线和统计）"""
    print("[INIT] 创建学习活动记录...")

    now = datetime.utcnow()

    activities = [
        # 今天
        {"id": "activity-001", "user_id": "user-001", "activity_type": "exercise", "target_id": "session-007", "title": "完成数学综合练习", "duration": 3600, "score": 75, "created_at": now - timedelta(hours=2)},
        {"id": "activity-002", "user_id": "user-001", "activity_type": "material_read", "target_id": "material-001", "title": "阅读三角函数诱导公式", "duration": 1800, "score": None, "created_at": now - timedelta(hours=4)},
        {"id": "activity-003", "user_id": "user-001", "activity_type": "mistake_review", "target_id": "mistake-001", "title": "复习错题：函数求值", "duration": 900, "score": None, "created_at": now - timedelta(hours=5)},
        # 昨天
        {"id": "activity-004", "user_id": "user-001", "activity_type": "exercise", "target_id": "session-006", "title": "完成英语词汇测试", "duration": 2700, "score": 100, "created_at": now - timedelta(days=1, hours=1)},
        {"id": "activity-005", "user_id": "user-001", "activity_type": "material_read", "target_id": "material-003", "title": "阅读英语时态总结", "duration": 2400, "score": None, "created_at": now - timedelta(days=1, hours=3)},
        # 前天
        {"id": "activity-006", "user_id": "user-001", "activity_type": "exercise", "target_id": "session-005", "title": "完成数学综合练习", "duration": 3000, "score": 100, "created_at": now - timedelta(days=2)},
        {"id": "activity-007", "user_id": "user-001", "activity_type": "session_complete", "target_id": "path-001", "title": "完成学习路径步骤：三角函数", "duration": 5400, "score": None, "created_at": now - timedelta(days=2, hours=2)},
        # 3天前
        {"id": "activity-008", "user_id": "user-001", "activity_type": "exercise", "target_id": "session-004", "title": "完成化学基础测试", "duration": 1800, "score": 100, "created_at": now - timedelta(days=3, hours=1)},
        # 4天前
        {"id": "activity-009", "user_id": "user-001", "activity_type": "exercise", "target_id": "session-003", "title": "完成物理运动学练习", "duration": 2400, "score": 100, "created_at": now - timedelta(days=4)},
        {"id": "activity-010", "user_id": "user-001", "activity_type": "material_read", "target_id": "material-004", "title": "阅读牛顿三大定律", "duration": 3600, "score": None, "created_at": now - timedelta(days=4, hours=2)},
        # 5天前
        {"id": "activity-011", "user_id": "user-001", "activity_type": "exercise", "target_id": "session-002", "title": "完成英语语法测试", "duration": 2100, "score": 50, "created_at": now - timedelta(days=5, hours=2)},
        # 6天前
        {"id": "activity-012", "user_id": "user-001", "activity_type": "exercise", "target_id": "session-001", "title": "完成数学基础练习", "duration": 3300, "score": 67, "created_at": now - timedelta(days=6, hours=1)},
        {"id": "activity-013", "user_id": "user-001", "activity_type": "material_read", "target_id": "material-002", "title": "阅读一元二次方程求根公式", "duration": 2700, "score": None, "created_at": now - timedelta(days=6, hours=3)},
    ]

    for a in activities:
        existing = db.query(StudyActivity).filter(StudyActivity.id == a["id"]).first()
        if existing:
            print(f"  [SKIP] 活动已存在: {a['id']}")
            continue

        activity = StudyActivity(**a)
        db.add(activity)
        print(f"  [OK] 创建活动: {a['title']}")

    db.commit()


def create_notifications(db: Session):
    """创建通知消息"""
    print("[INIT] 创建通知消息...")

    now = datetime.utcnow()

    notifications = [
        {
            "id": "notif-001",
            "user_id": "user-001",
            "title": "成就解锁：练习新手",
            "content": "恭喜你完成了10道练习题，解锁成就「练习新手」！",
            "type": "achievement",
            "is_read": False,
            "created_at": now - timedelta(hours=1),
        },
        {
            "id": "notif-002",
            "user_id": "user-001",
            "title": "学习提醒",
            "content": "你已经连续学习7天了，继续保持！",
            "type": "reminder",
            "is_read": False,
            "created_at": now - timedelta(hours=3),
        },
        {
            "id": "notif-003",
            "user_id": "user-001",
            "title": "错题复习提醒",
            "content": "你有3道错题待复习，记得及时巩固哦！",
            "type": "exercise",
            "is_read": True,
            "created_at": now - timedelta(days=1),
        },
        {
            "id": "notif-004",
            "user_id": "user-001",
            "title": "新课程推荐",
            "content": "根据你的学习情况，为你推荐「三角函数进阶」课程",
            "type": "system",
            "is_read": True,
            "created_at": now - timedelta(days=2),
        },
        {
            "id": "notif-005",
            "user_id": "user-001",
            "title": "课堂通知",
            "content": "李老师发布了新的随堂测验，请及时完成",
            "type": "classroom",
            "is_read": True,
            "created_at": now - timedelta(days=3),
        },
    ]

    for n in notifications:
        existing = db.query(Notification).filter(Notification.id == n["id"]).first()
        if existing:
            print(f"  [SKIP] 通知已存在: {n['id']}")
            continue

        notification = Notification(**n)
        db.add(notification)
        print(f"  [OK] 创建通知: {n['title']}")

    db.commit()


def create_achievements(db: Session):
    """创建成就定义"""
    print("[INIT] 创建成就定义...")

    achievements = [
        {
            "id": "ach-001",
            "name": "初次登场",
            "description": "完成首次登录",
            "icon": "",
            "condition_type": "exercise_count",
            "condition_value": 1,
        },
        {
            "id": "ach-002",
            "name": "练习新手",
            "description": "完成10道练习题",
            "icon": "📚",
            "condition_type": "exercise_count",
            "condition_value": 10,
        },
        {
            "id": "ach-003",
            "name": "练习达人",
            "description": "完成50道练习题",
            "icon": "🏆",
            "condition_type": "exercise_count",
            "condition_value": 50,
        },
        {
            "id": "ach-004",
            "name": "学霸之路",
            "description": "完成100道练习题",
            "icon": "👑",
            "condition_type": "exercise_count",
            "condition_value": 100,
        },
        {
            "id": "ach-005",
            "name": "坚持就是胜利",
            "description": "连续学习7天",
            "icon": "🔥",
            "condition_type": "streak_days",
            "condition_value": 7,
        },
        {
            "id": "ach-006",
            "name": "学习狂人",
            "description": "连续学习30天",
            "icon": "",
            "condition_type": "streak_days",
            "condition_value": 30,
        },
        {
            "id": "ach-007",
            "name": "收藏夹达人",
            "description": "收藏20条学习资料",
            "icon": "⭐",
            "condition_type": "material_count",
            "condition_value": 20,
        },
        {
            "id": "ach-008",
            "name": "百发百中",
            "description": "练习正确率达到90%",
            "icon": "🎯",
            "condition_type": "accuracy",
            "condition_value": 90,
        },
    ]

    for a in achievements:
        existing = db.query(Achievement).filter(Achievement.id == a["id"]).first()
        if existing:
            print(f"  [SKIP] 成就已存在: {a['name']}")
            continue

        ach = Achievement(**a, created_at=datetime.utcnow())
        db.add(ach)
        print(f"  [OK] 创建成就: {a['name']}")

    db.commit()


def create_user_achievements(db: Session):
    """创建用户已解锁成就"""
    print("[INIT] 创建用户已解锁成就...")

    user_achievements = [
        {"user_id": "user-001", "achievement_id": "ach-001", "unlocked_at": datetime.utcnow() - timedelta(days=7)},
        {"user_id": "user-001", "achievement_id": "ach-002", "unlocked_at": datetime.utcnow() - timedelta(days=3)},
        {"user_id": "user-001", "achievement_id": "ach-005", "unlocked_at": datetime.utcnow() - timedelta(days=1)},
    ]

    for ua in user_achievements:
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == ua["user_id"],
            UserAchievement.achievement_id == ua["achievement_id"]
        ).first()
        if existing:
            print(f"  [SKIP] 用户成就已存在")
            continue

        user_ach = UserAchievement(**ua)
        db.add(user_ach)
        print(f"  [OK] 解锁成就: {ua['achievement_id']}")

    db.commit()


def create_learning_paths(db: Session):
    """创建示例学习路径"""
    print("[INIT] 创建示例学习路径...")

    import json

    paths = [
        {
            "user_id": "user-001",
            "title": "高一数学期末冲刺",
            "description": "系统复习高一数学重点知识，为期末考试做好准备",
            "steps": json.dumps([
                {"title": "函数基础", "description": "复习函数概念、定义域、值域", "duration": 120, "status": "completed"},
                {"title": "三角函数", "description": "掌握诱导公式、图像性质", "duration": 180, "status": "completed"},
                {"title": "数列", "description": "等差数列、等比数列求和", "duration": 150, "status": "active"},
                {"title": "立体几何", "description": "空间向量与线面关系", "duration": 200, "status": "pending"},
                {"title": "模拟测试", "description": "完成2套期末模拟卷", "duration": 180, "status": "pending"},
            ]),
            "status": "active",
        },
        {
            "user_id": "user-001",
            "title": "英语语法通关",
            "description": "从基础语法到高级语法，全面掌握英语语法体系",
            "steps": json.dumps([
                {"title": "时态入门", "description": "一般现在时、一般过去时", "duration": 90, "status": "completed"},
                {"title": "进行时态", "description": "现在进行时、过去进行时", "duration": 90, "status": "completed"},
                {"title": "完成时态", "description": "现在完成时、过去完成时", "duration": 120, "status": "active"},
                {"title": "被动语态", "description": "各种时态的被动形式", "duration": 100, "status": "pending"},
                {"title": "从句", "description": "定语从句、状语从句、名词性从句", "duration": 180, "status": "pending"},
            ]),
            "status": "active",
        },
    ]

    for i, p in enumerate(paths):
        existing = db.query(LearningPath).filter(LearningPath.title == p["title"]).first()
        if existing:
            print(f"  [SKIP] 路径已存在: {p['title']}")
            continue

        path = LearningPath(
            id=f"path-{i+1:03d}",
            **p,
            created_at=datetime.utcnow(),
        )
        db.add(path)
        print(f"  [OK] 创建路径: {p['title']}")

    db.commit()


def create_classrooms(db: Session):
    """创建示例课堂"""
    print("[INIT] 创建示例课堂...")

    classrooms = [
        {
            "id": "class-001",
            "code": "123456",
            "name": "高一数学精英班",
            "description": "针对数学基础较好的同学，深入讲解重点难点",
            "teacher_id": "user-002",
            "status": "active",
        },
    ]

    for c in classrooms:
        existing = db.query(Classroom).filter(Classroom.id == c["id"]).first()
        if existing:
            print(f"  [SKIP] 课堂已存在: {c['name']}")
            continue

        classroom = Classroom(
            **c,
            created_at=datetime.utcnow(),
        )
        db.add(classroom)

        # 添加老师为成员
        member = ClassroomMember(
            classroom_id=c["id"],
            user_id=c["teacher_id"],
            role="teacher",
        )
        db.add(member)

        # 添加学生为成员
        member2 = ClassroomMember(
            classroom_id=c["id"],
            user_id="user-001",
            role="student",
        )
        db.add(member2)

        print(f"  [OK] 创建课堂: {c['name']} (邀请码: {c['code']})")

    db.commit()


def create_mindmaps(db: Session):
    """创建示例思维导图"""
    print("[INIT] 创建示例思维导图...")

    import json

    mindmaps = [
        {
            "user_id": "user-001",
            "title": "三角函数知识体系",
            "subject": "数学",
            "content": json.dumps({
                "name": "三角函数",
                "children": [
                    {"name": "基本概念", "children": [
                        {"name": "角度与弧度"},
                        {"name": "单位圆"},
                        {"name": "三角函数定义"}
                    ]},
                    {"name": "诱导公式", "children": [
                        {"name": "奇变偶不变"},
                        {"name": "符号看象限"}
                    ]},
                    {"name": "图像与性质", "children": [
                        {"name": "正弦函数"},
                        {"name": "余弦函数"},
                        {"name": "正切函数"}
                    ]},
                    {"name": "三角恒等变换", "children": [
                        {"name": "和差公式"},
                        {"name": "倍角公式"},
                        {"name": "半角公式"}
                    ]}
                ]
            }),
            "status": "active",
        },
        {
            "user_id": "user-001",
            "title": "英语时态体系",
            "subject": "英语",
            "content": json.dumps({
                "name": "英语时态",
                "children": [
                    {"name": "现在时态", "children": [
                        {"name": "一般现在时"},
                        {"name": "现在进行时"},
                        {"name": "现在完成时"}
                    ]},
                    {"name": "过去时态", "children": [
                        {"name": "一般过去时"},
                        {"name": "过去进行时"},
                        {"name": "过去完成时"}
                    ]},
                    {"name": "将来时态", "children": [
                        {"name": "一般将来时"},
                        {"name": "将来进行时"}
                    ]}
                ]
            }),
            "status": "active",
        },
    ]

    for i, m in enumerate(mindmaps):
        existing = db.query(MindMap).filter(MindMap.title == m["title"]).first()
        if existing:
            print(f"  [SKIP] 思维导图已存在: {m['title']}")
            continue

        mindmap = MindMap(
            id=f"mindmap-{i+1:03d}",
            **m,
            created_at=datetime.utcnow(),
        )
        db.add(mindmap)
        print(f"  [OK] 创建思维导图: {m['title']}")

    db.commit()


def create_assessment_reports(db: Session):
    """创建评估报告"""
    print("[INIT] 创建评估报告...")

    reports = [
        {
            "user_id": "user-001",
            "content": """## 学习分析报告

### 总体概况
- 学习时长：28小时（本周）
- 完成任务：32个
- 练习正确率：78%

### 学科分析
- **数学**：掌握良好，三角函数需加强
- **英语**：时态理解有进步，词汇量待提升
- **物理**：力学基础扎实，电磁学需预习
- **化学**：方程式配平方法已掌握

### 薄弱知识点
1. 三角函数诱导公式
2. 英语现在完成时
3. 化学方程式配平

### 建议
1. 每天花30分钟复习三角函数公式
2. 多做英语时态练习题
3. 化学方程式配平已掌握，可以进入下一阶段""",
        },
    ]

    for i, r in enumerate(reports):
        report = AssessmentReport(
            id=f"report-{i+1:03d}",
            **r,
            created_at=datetime.utcnow(),
        )
        db.add(report)
        print(f"  [OK] 创建评估报告")

    db.commit()


def create_learning_websites(db: Session):
    """创建学习网站"""
    print("[INIT] 创建学习网站...")

    websites = [
        {"id": "site-001", "name": "可汗学院", "url": "https://www.khanacademy.org", "description": "免费的世界级教育平台", "category": "综合", "is_recommended": True, "sort_order": 1},
        {"id": "site-002", "name": "LeetCode", "url": "https://leetcode.cn", "description": "编程练习平台", "category": "编程", "is_recommended": True, "sort_order": 2},
        {"id": "site-003", "name": "Coursera", "url": "https://www.coursera.org", "description": "全球顶尖大学在线课程", "category": "综合", "is_recommended": True, "sort_order": 3},
        {"id": "site-004", "name": "BBC Learning English", "url": "https://www.bbc.co.uk/learningenglish", "description": "BBC英语学习频道", "category": "英语", "is_recommended": True, "sort_order": 4},
        {"id": "site-005", "name": "MIT OpenCourseWare", "url": "https://ocw.mit.edu", "description": "MIT开放课程", "category": "综合", "is_recommended": False, "sort_order": 5},
        {"id": "site-006", "name": "Duolingo", "url": "https://www.duolingo.com", "description": "趣味语言学习", "category": "英语", "is_recommended": False, "sort_order": 6},
    ]

    for w in websites:
        existing = db.query(LearningWebsite).filter(LearningWebsite.id == w["id"]).first()
        if existing:
            print(f"  [SKIP] 网站已存在: {w['name']}")
            continue

        website = LearningWebsite(
            **w,
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(website)
        print(f"  [OK] 创建网站: {w['name']}")

    db.commit()


def create_favorites(db: Session):
    """创建收藏"""
    print("[INIT] 创建收藏...")

    favorites = [
        {"user_id": "user-001", "target_type": "study_material", "target_id": "material-001"},
        {"user_id": "user-001", "target_type": "study_material", "target_id": "material-004"},
        {"user_id": "user-001", "target_type": "study_material", "target_id": "material-008"},
        {"user_id": "user-001", "target_type": "learning_resource", "target_id": "resource-001"},
        {"user_id": "user-001", "target_type": "learning_resource", "target_id": "resource-003"},
    ]

    for f in favorites:
        existing = db.query(Favorite).filter(
            Favorite.user_id == f["user_id"],
            Favorite.target_type == f["target_type"],
            Favorite.target_id == f["target_id"]
        ).first()
        if existing:
            continue

        favorite = Favorite(**f, created_at=datetime.utcnow())
        db.add(favorite)
        print(f"  [OK] 创建收藏: {f['target_type']} - {f['target_id']}")

    db.commit()


def migrate_database(db: Session):
    """数据库迁移：修复已有表结构缺失的列"""
    print("[INIT] 检查数据库迁移...")

    from sqlalchemy import text, inspect

    inspector = inspect(db.get_bind())

    # 检查 student_profiles 表是否有 user_id 列
    columns = [col["name"] for col in inspector.get_columns("student_profiles")]
    if "user_id" not in columns:
        print("  [MIGRATE] 添加 student_profiles.user_id 列...")
        db.execute(text(
            "ALTER TABLE student_profiles ADD COLUMN user_id VARCHAR(64) UNIQUE"
        ))
        db.commit()
        print("  [OK] 迁移完成: student_profiles.user_id")
    else:
        print("  [OK] 数据库结构已是最新")


def main():
    print("=" * 50)
    print("SmartLearning 数据库初始化")
    print("=" * 50)

    # 确保表已创建
    init_db()

    # 获取数据库会话
    db = next(get_db())

    try:
        migrate_database(db)
        create_test_users(db)
        create_student_profiles(db)
        create_study_materials(db)
        create_learning_resources(db)
        create_mistakes(db)
        create_exercises(db)
        create_exercise_records_and_sessions(db)
        create_study_activities(db)
        create_notifications(db)
        create_achievements(db)
        create_user_achievements(db)
        create_learning_paths(db)
        create_classrooms(db)
        create_mindmaps(db)
        create_assessment_reports(db)
        create_learning_websites(db)
        create_favorites(db)

        print("\n" + "=" * 50)
        print("[OK] 数据初始化完成！")
        print("=" * 50)
        print("\n测试账号：")
        print("  学生: student1 / 123456")
        print("  老师: teacher1 / 123456")
        print("\n数据概览：")
        print(f"  用户: {db.query(User).count()}")
        print(f"  学习资料: {db.query(StudyMaterial).count()}")
        print(f"  学习资源: {db.query(LearningResource).count()}")
        print(f"  错题: {db.query(Mistake).count()}")
        print(f"  练习题: {db.query(Exercise).count()}")
        print(f"  练习记录: {db.query(ExerciseRecord).count()}")
        print(f"  练习会话: {db.query(ExerciseSession).count()}")
        print(f"  学习活动: {db.query(StudyActivity).count()}")
        print(f"  通知: {db.query(Notification).count()}")
        print(f"  成就: {db.query(Achievement).count()}")
        print(f"  学习路径: {db.query(LearningPath).count()}")
        print(f"  课堂: {db.query(Classroom).count()}")
        print(f"  思维导图: {db.query(MindMap).count()}")
        print(f"  学习网站: {db.query(LearningWebsite).count()}")
        print(f"  收藏: {db.query(Favorite).count()}")

    except Exception as e:
        print(f"\n[ERROR] 初始化失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
