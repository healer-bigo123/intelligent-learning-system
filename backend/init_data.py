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
    LearningWebsite, StudentProfile, Favorite, Task,
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
        # 数学（5条）
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
            "title": "等差数列与等比数列",
            "content": "等差数列：相邻两项的差相等。\n通项公式：aₙ = a₁ + (n-1)d\n求和公式：Sₙ = n(a₁+aₙ)/2 = na₁ + n(n-1)d/2\n\n等比数列：相邻两项的比相等。\n通项公式：aₙ = a₁q^(n-1)\n求和公式：Sₙ = a₁(1-qⁿ)/(1-q) (q≠1)\n\n应用场景：\n- 等差：阶梯电价、等速增长\n- 等比：复利计算、细菌繁殖",
            "subject": "数学",
            "grade": "高二",
            "material_type": "知识点",
            "knowledge_point": "数列",
            "tags": "高考,重点,公式",
            "source": "人教版教材",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "函数单调性判断方法",
            "content": "函数单调性定义：\n- 增函数：在区间内，x₁<x₂ 时 f(x₁)<f(x₂)\n- 减函数：在区间内，x₁<x₂ 时 f(x₁)>f(x₂)\n\n判断方法：\n1. 定义法：作差 f(x₁)-f(x₂)，判断正负\n2. 导数法：f'(x)>0 则增，f'(x)<0 则减\n3. 图像法：观察图像走势\n4. 复合函数：同增异减\n\n注意：单调区间不能用并集连接。",
            "subject": "数学",
            "grade": "高一",
            "material_type": "知识点",
            "knowledge_point": "函数性质",
            "tags": "高考,重点,方法",
            "source": "整理",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "立体几何中的线面关系",
            "content": "直线与平面的位置关系：\n1. 直线在平面内：有无数公共点\n2. 直线与平面相交：有且只有一个公共点\n3. 直线与平面平行：没有公共点\n\n判定定理：\n- 线面平行：平面外一条直线与平面内一条直线平行，则线面平行\n- 线面垂直：一条直线与平面内两条相交直线都垂直，则线面垂直\n\n性质定理：\n- 线面平行：过这条直线的平面与原平面交线平行于该直线\n- 线面垂直：垂直于同一平面的两条直线互相平行",
            "subject": "数学",
            "grade": "高二",
            "material_type": "知识点",
            "knowledge_point": "立体几何",
            "tags": "高考,重点,定理",
            "source": "人教版教材",
            "difficulty": 4,
        },
        # 英语（5条）
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
            "title": "现在完成时用法详解",
            "content": "现在完成时表示过去发生的动作对现在造成的影响，或从过去持续到现在的动作。\n\n结构：have/has + 过去分词\n\n用法：\n1. 表示已完成：I have finished my homework.\n2. 表示经历：Have you ever been to Beijing?\n3. 表示持续：I have lived here for 10 years.\n\n时间标志词：\n- already, yet, ever, never, just\n- for + 时间段，since + 时间点",
            "subject": "英语",
            "grade": "初二",
            "material_type": "知识点",
            "knowledge_point": "现在完成时",
            "tags": "中考,语法,重点",
            "source": "课堂笔记",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "被动语态结构总结",
            "content": "被动语态强调动作的承受者。\n\n基本结构：be + 过去分词\n\n各时态被动语态：\n1. 一般现在时：am/is/are + done\n2. 一般过去时：was/were + done\n3. 现在进行时：am/is/are being + done\n4. 现在完成时：have/has been + done\n5. 情态动词：can/may/must be + done\n\n例句：\n主动：Tom wrote the book.\n被动：The book was written by Tom.",
            "subject": "英语",
            "grade": "初三",
            "material_type": "知识点",
            "knowledge_point": "被动语态",
            "tags": "中考,语法,重点",
            "source": "整理",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "宾语从句连接词用法",
            "content": "宾语从句是在主句中作宾语的从句。\n\n连接词：\n1. that：无意义，可省略（陈述句作宾语从句）\n   I think (that) he is right.\n2. if/whether：是否（一般疑问句作宾语从句）\n   I don't know if he will come.\n3. 特殊疑问词：what, where, when, why, how\n   Can you tell me where he lives?\n\n语序：宾语从句必须用陈述句语序。\n时态：主句过去时，从句用相应过去时；客观真理用一般现在时。",
            "subject": "英语",
            "grade": "初三",
            "material_type": "知识点",
            "knowledge_point": "宾语从句",
            "tags": "中考,语法,重点",
            "source": "人教版教材",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "英语阅读理解技巧",
            "content": "阅读理解常见题型及解题技巧：\n\n1. 主旨大意题\n   - 关注首尾段、各段首句\n   - 避免以偏概全\n\n2. 细节理解题\n   - 根据关键词定位原文\n   - 注意同义替换\n\n3. 词义猜测题\n   - 利用上下文线索\n   - 利用构词法\n\n4. 推理判断题\n   - 不要选原文直接陈述的选项\n   - 基于原文合理推断\n\n做题顺序：先看题目，再读文章，带着问题找答案。",
            "subject": "英语",
            "grade": "高中",
            "material_type": "方法",
            "knowledge_point": "阅读理解",
            "tags": "高考,技巧,方法",
            "source": "网络",
            "difficulty": 2,
        },
        # 物理（5条）
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
            "title": "匀变速直线运动公式",
            "content": "基本公式：\n1. v = v₀ + at\n2. x = v₀t + ½at²\n3. v² - v₀² = 2ax\n4. x = (v₀+v)t/2\n\n适用条件：加速度恒定的直线运动。\n\n常用推论：\n- 相邻相等时间间隔位移差：Δx = aT²\n- 中间时刻瞬时速度等于平均速度\n\n注意：\n- 先规定正方向\n- 矢量性：速度与加速度同向加速，反向减速",
            "subject": "物理",
            "grade": "高一",
            "material_type": "公式",
            "knowledge_point": "运动学",
            "tags": "高考,重点,公式",
            "source": "课堂笔记",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "圆周运动基本概念",
            "content": "描述圆周运动的物理量：\n1. 线速度 v = 2πr/T\n2. 角速度 ω = 2π/T = v/r\n3. 周期 T：转动一周所需时间\n4. 转速 n：单位时间转过的圈数\n5. 向心加速度 a = v²/r = ω²r\n6. 向心力 F = mv²/r = mω²r\n\n注意：\n- 向心力是效果力，由具体力提供\n- 匀速圆周运动速度大小不变，方向时刻改变\n- 向心力只改变速度方向，不改变速度大小",
            "subject": "物理",
            "grade": "高一",
            "material_type": "知识点",
            "knowledge_point": "圆周运动",
            "tags": "高考,重点,概念",
            "source": "人教版教材",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "机械能守恒定律",
            "content": "机械能 = 动能 + 重力势能 + 弹性势能\n\n机械能守恒条件：\n只有重力或弹力做功，其他力不做功或做功代数和为零。\n\n表达式：\nEₖ₁ + Eₚ₁ = Eₖ₂ + Eₚ₂\n或 ΔEₖ = -ΔEₚ\n\n应用步骤：\n1. 确定研究对象和过程\n2. 判断机械能是否守恒\n3. 选择参考平面\n4. 列出初末状态机械能相等的方程\n\n注意：有摩擦力做功时机械能不守恒。",
            "subject": "物理",
            "grade": "高一",
            "material_type": "知识点",
            "knowledge_point": "机械能",
            "tags": "高考,重点,定律",
            "source": "整理",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "电场强度与电势",
            "content": "电场强度 E：\n- 定义：E = F/q\n- 方向：正电荷受力方向\n- 点电荷电场：E = kQ/r²\n\n电势 φ：\n- 定义：单位正电荷在电场中某点的电势能\n- 电势差 U = φ₁ - φ₂\n- 电场力做功 W = qU\n\n关系：\n- 沿电场线方向电势降低\n- 电场线密集处电场强度大\n- 等势面与电场线垂直",
            "subject": "物理",
            "grade": "高二",
            "material_type": "知识点",
            "knowledge_point": "电场",
            "tags": "高考,重点,概念",
            "source": "人教版教材",
            "difficulty": 4,
        },
        # 化学（5条）
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
            "title": "物质的量与摩尔质量",
            "content": "物质的量 n：表示含有一定数目粒子的集合体，单位 mol。\n\n阿伏伽德罗常数：Nₐ ≈ 6.02×10²³ mol⁻¹\n\n公式：\n1. n = N/Nₐ\n2. n = m/M\n3. 标准状况下气体体积 V = n × 22.4 L/mol\n\n摩尔质量 M：单位物质的量的物质所具有的质量，单位 g/mol。\n数值上等于相对原子质量或相对分子质量。\n\n例：H₂O 的摩尔质量 = 18 g/mol",
            "subject": "化学",
            "grade": "高一",
            "material_type": "知识点",
            "knowledge_point": "物质的量",
            "tags": "高考,基础,计算",
            "source": "人教版教材",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "氧化还原反应判断",
            "content": "氧化还原反应本质：电子转移（得失或偏移）。\n\n判断方法：\n1. 化合价升降法：有元素化合价变化的反应\n2. 单质参与法：有单质参加或生成的反应一般是氧化还原反应\n\n相关概念：\n- 氧化剂：得电子，化合价降低，被还原\n- 还原剂：失电子，化合价升高，被氧化\n- 氧化反应：失电子，化合价升高\n- 还原反应：得电子，化合价降低\n\n记忆口诀：升失氧，降得还。",
            "subject": "化学",
            "grade": "高一",
            "material_type": "知识点",
            "knowledge_point": "氧化还原",
            "tags": "高考,重点,判断",
            "source": "课堂笔记",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "元素周期律应用",
            "content": "元素周期律：元素的性质随原子序数的递增而呈周期性变化。\n\n同周期（从左到右）：\n- 原子半径减小\n- 金属性减弱，非金属性增强\n- 最高价氧化物对应水化物酸性增强\n\n同主族（从上到下）：\n- 原子半径增大\n- 金属性增强，非金属性减弱\n- 气态氢化物稳定性减弱\n\n应用：\n- 预测元素性质\n- 比较金属性/非金属性强弱\n- 判断化合物酸碱性",
            "subject": "化学",
            "grade": "高一",
            "material_type": "知识点",
            "knowledge_point": "元素周期律",
            "tags": "高考,重点,规律",
            "source": "人教版教材",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "酸碱盐性质总结",
            "content": "酸：电离时生成的阳离子全部是 H⁺ 的化合物。\n- 通性：与指示剂、活泼金属、金属氧化物、碱、盐反应\n\n碱：电离时生成的阴离子全部是 OH⁻ 的化合物。\n- 通性：与指示剂、非金属氧化物、酸、盐反应\n\n盐：由金属离子（或铵根）和酸根离子组成的化合物。\n- 性质：与酸、碱、盐反应，部分可分解\n\n复分解反应条件：生成沉淀、气体或水。\n\n常见沉淀：AgCl、BaSO₄、CaCO₃、Cu(OH)₂、Fe(OH)₃",
            "subject": "化学",
            "grade": "初三",
            "material_type": "知识点",
            "knowledge_point": "酸碱盐",
            "tags": "中考,重点,性质",
            "source": "整理",
            "difficulty": 2,
        },
        # 生物（5条）
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
            "title": "光合作用与呼吸作用",
            "content": "光合作用：\n- 场所：叶绿体\n- 条件：光、色素、酶\n- 反应式：6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂\n- 意义：将光能转化为化学能，合成有机物\n\n呼吸作用：\n- 有氧呼吸：细胞质基质、线粒体\n  C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + 能量\n- 无氧呼吸：细胞质基质\n  产生酒精和 CO₂ 或乳酸\n\n关系：光合作用储存能量，呼吸作用释放能量。",
            "subject": "生物",
            "grade": "高一",
            "material_type": "知识点",
            "knowledge_point": "代谢",
            "tags": "高考,重点,对比",
            "source": "人教版教材",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "DNA复制与遗传",
            "content": "DNA 复制：\n- 时间：细胞分裂间期\n- 条件：模板、原料、能量、酶\n- 特点：半保留复制、边解旋边复制\n- 结果：1 个 DNA 分子复制成 2 个完全相同的 DNA 分子\n\n遗传信息的传递：\n- DNA → RNA → 蛋白质\n- 转录：以 DNA 一条链为模板合成 RNA\n- 翻译：以 mRNA 为模板合成蛋白质\n\n基因：有遗传效应的 DNA 片段。",
            "subject": "生物",
            "grade": "高二",
            "material_type": "知识点",
            "knowledge_point": "遗传",
            "tags": "高考,重点,遗传",
            "source": "人教版教材",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "生态系统能量流动",
            "content": "能量流动的特点：\n1. 单向流动：只能从第一营养级流向更高营养级\n2. 逐级递减：相邻营养级间能量传递效率约 10%-20%\n\n能量流动过程：\n- 生产者固定太阳能\n- 初级消费者摄食生产者\n- 次级消费者摄食初级消费者\n- 各营养级通过呼吸作用散失热能\n\n应用：\n- 合理设计食物链，提高能量利用率\n- 农业生态系统中实现物质循环利用",
            "subject": "生物",
            "grade": "高二",
            "material_type": "知识点",
            "knowledge_point": "生态系统",
            "tags": "高考,重点,能量",
            "source": "整理",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "人体免疫系统",
            "content": "免疫系统的三道防线：\n1. 第一道：皮肤、黏膜\n2. 第二道：体液中的杀菌物质和吞噬细胞\n3. 第三道：免疫器官和免疫细胞（特异性免疫）\n\n特异性免疫：\n- 体液免疫：B 细胞产生抗体，消灭抗原\n- 细胞免疫：T 细胞直接杀伤靶细胞\n\n免疫失调：\n- 过敏反应：已免疫机体再次接触过敏原\n- 自身免疫病：免疫系统攻击自身组织\n- 免疫缺陷病：如艾滋病",
            "subject": "生物",
            "grade": "高二",
            "material_type": "知识点",
            "knowledge_point": "免疫",
            "tags": "高考,重点,人体",
            "source": "人教版教材",
            "difficulty": 3,
        },
        # 编程（5条）
        {
            "user_id": "user-001",
            "title": "Python 变量与数据类型",
            "content": "Python 是一门简洁优雅的编程语言，适合初学者入门。\n\n变量：\n- 变量是存储数据的容器\n- 命名规则：字母、数字、下划线，不能以数字开头\n- 例：name = \"Alice\"，age = 18\n\n基本数据类型：\n1. int：整数，如 10、-5\n2. float：浮点数，如 3.14、-0.5\n3. str：字符串，如 \"Hello\"\n4. bool：布尔值，True 或 False\n5. list：列表，如 [1, 2, 3]\n6. dict：字典，如 {\"name\": \"Tom\", \"age\": 20}\n\n使用 type() 函数可以查看变量类型。",
            "subject": "编程",
            "grade": "入门",
            "material_type": "知识点",
            "knowledge_point": "Python基础",
            "tags": "编程,Python,入门",
            "source": "在线教程",
            "difficulty": 1,
        },
        {
            "user_id": "user-001",
            "title": "条件语句与循环结构",
            "content": "条件语句和循环是程序控制流程的基础。\n\n条件语句 if-elif-else：\n```python\nscore = 85\nif score >= 90:\n    print(\"优秀\")\nelif score >= 60:\n    print(\"及格\")\nelse:\n    print(\"不及格\")\n```\n\nfor 循环：\n```python\nfor i in range(5):\n    print(i)  # 输出 0,1,2,3,4\n```\n\nwhile 循环：\n```python\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n```\n\n注意缩进：Python 使用缩进来表示代码块。",
            "subject": "编程",
            "grade": "入门",
            "material_type": "知识点",
            "knowledge_point": "流程控制",
            "tags": "编程,Python,控制流",
            "source": "在线教程",
            "difficulty": 1,
        },
        {
            "user_id": "user-001",
            "title": "函数定义与调用",
            "content": "函数是组织好的、可重复使用的代码块。\n\n定义函数：\n```python\ndef greet(name):\n    return \"Hello, \" + name\n```\n\n调用函数：\n```python\nmessage = greet(\"Alice\")\nprint(message)  # Hello, Alice\n```\n\n函数参数：\n- 位置参数：按顺序传入\n- 默认参数：def add(a, b=10)\n- 关键字参数：add(a=3, b=5)\n- 可变参数：*args 和 **kwargs\n\n返回值：使用 return 返回结果，可以返回多个值（实际是元组）。",
            "subject": "编程",
            "grade": "入门",
            "material_type": "知识点",
            "knowledge_point": "函数",
            "tags": "编程,Python,函数",
            "source": "在线教程",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "列表与字典操作",
            "content": "列表和字典是 Python 中最常用的数据结构。\n\n列表（list）：有序可变集合\n```python\nfruits = [\"apple\", \"banana\", \"cherry\"]\nfruits.append(\"orange\")  # 添加元素\nfruits[0]  # 访问第一个元素\nlen(fruits)  # 获取长度\n```\n\n字典（dict）：键值对集合\n```python\nstudent = {\"name\": \"Tom\", \"age\": 18}\nstudent[\"name\"]  # 访问值\nstudent[\"grade\"] = \"A\"  # 添加键值对\nstudent.keys()  # 获取所有键\n```\n\n列表推导式：\n```python\nsquares = [x**2 for x in range(10)]\n```",
            "subject": "编程",
            "grade": "入门",
            "material_type": "知识点",
            "knowledge_point": "数据结构",
            "tags": "编程,Python,数据结构",
            "source": "在线教程",
            "difficulty": 2,
        },
        {
            "user_id": "user-001",
            "title": "面向对象编程基础",
            "content": "面向对象编程（OOP）是一种重要的编程思想。\n\n核心概念：\n1. 类（Class）：对象的模板\n2. 对象（Object）：类的实例\n3. 属性（Attribute）：对象的数据\n4. 方法（Method）：对象的行为\n\n示例：\n```python\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n    \n    def bark(self):\n        return f\"{self.name} says woof!\"\n\nmy_dog = Dog(\"Buddy\")\nprint(my_dog.bark())\n```\n\n三大特性：\n- 封装：将数据和方法包装在一起\n- 继承：子类继承父类的属性和方法\n- 多态：不同对象对同一消息作出不同响应",
            "subject": "编程",
            "grade": "进阶",
            "material_type": "知识点",
            "knowledge_point": "面向对象",
            "tags": "编程,Python,OOP",
            "source": "在线教程",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "Python 异常处理机制",
            "content": "异常处理是编写健壮程序的重要技能。\n\n基本语法：\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print(\"不能除以零\")\nfinally:\n    print(\"无论是否异常都会执行\")\n```\n\n常见异常类型：\n- SyntaxError：语法错误\n- TypeError：类型错误\n- ValueError：值错误\n- IndexError：索引越界\n- KeyError：字典中不存在该键\n- FileNotFoundError：文件不存在\n\n自定义异常：\n```python\nclass ValidationError(Exception):\n    pass\n```",
            "subject": "编程",
            "grade": "进阶",
            "material_type": "知识点",
            "knowledge_point": "异常处理",
            "tags": "编程,Python,调试",
            "source": "在线教程",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "文件读写与上下文管理",
            "content": "文件操作是编程中常用的技能。\n\n基本文件读写：\n```python\n# 读取文件\nwith open('data.txt', 'r', encoding='utf-8') as f:\n    content = f.read()\n\n# 写入文件\nwith open('output.txt', 'w', encoding='utf-8') as f:\n    f.write('Hello, World!')\n```\n\n打开模式：\n- 'r'：只读\n- 'w'：写入（覆盖）\n- 'a'：追加\n- 'b'：二进制模式\n\n上下文管理器 with 可以自动关闭文件，避免资源泄漏。\n\nJSON 文件操作：\n```python\nimport json\nwith open('data.json', 'r', encoding='utf-8') as f:\n    data = json.load(f)\n```",
            "subject": "编程",
            "grade": "进阶",
            "material_type": "知识点",
            "knowledge_point": "文件操作",
            "tags": "编程,Python,IO",
            "source": "在线教程",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "Python 模块与包管理",
            "content": "模块和包帮助我们组织和管理代码。\n\n模块：\n- 一个 .py 文件就是一个模块\n- 使用 import 导入模块\n- 使用 from module import name 导入特定内容\n\n包：\n- 包含 __init__.py 的文件夹\n- 用于组织多个模块\n\n常用标准库：\n- os：操作系统接口\n- sys：系统相关\n- datetime：日期时间\n- json：JSON 数据处理\n- re：正则表达式\n- math：数学运算\n\n安装第三方库：\n```bash\npip install requests\n```",
            "subject": "编程",
            "grade": "进阶",
            "material_type": "知识点",
            "knowledge_point": "模块化",
            "tags": "编程,Python,工程化",
            "source": "在线教程",
            "difficulty": 3,
        },
        {
            "user_id": "user-001",
            "title": "正则表达式入门",
            "content": "正则表达式是强大的文本匹配工具。\n\n常用元字符：\n- .：匹配任意单个字符\n- *：匹配前一个字符 0 次或多次\n- +：匹配前一个字符 1 次或多次\n- ?：匹配前一个字符 0 次或 1 次\n- ^：匹配字符串开头\n- $：匹配字符串结尾\n- []：匹配括号内任意字符\n- \\d：匹配数字\n- \\w：匹配字母、数字、下划线\n\nPython 中使用 re 模块：\n```python\nimport re\nresult = re.search(r'\\d+', 'age: 25')\nprint(result.group())  # 25\n```",
            "subject": "编程",
            "grade": "进阶",
            "material_type": "知识点",
            "knowledge_point": "正则表达式",
            "tags": "编程,Python,文本处理",
            "source": "在线教程",
            "difficulty": 4,
        },
        {
            "user_id": "user-001",
            "title": "经典排序算法：冒泡与快速排序",
            "content": "排序算法是计算机科学的基础。\n\n冒泡排序：\n- 重复遍历数组，相邻元素两两比较\n- 时间复杂度：O(n²)\n```python\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n```\n\n快速排序：\n- 分治法：选择基准，将数组分为左右两部分\n- 平均时间复杂度：O(n log n)\n```python\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr)//2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n```",
            "subject": "编程",
            "grade": "进阶",
            "material_type": "知识点",
            "knowledge_point": "算法基础",
            "tags": "编程,算法,排序",
            "source": "在线教程",
            "difficulty": 4,
        },
    ]

    existing_count = db.query(StudyMaterial).count()

    # 预定义浏览量，使排序差异明显
    views_values = [50, 120, 30, 200, 80, 10, 150, 60, 90, 40, 180, 70, 20, 110, 140, 5, 160, 100, 45, 130, 25, 170, 85, 35, 190, 55, 15, 210, 95, 165, 75, 125, 230, 65, 115, 145, 175, 205, 135, 185]

    for i, m in enumerate(materials):
        existing = db.query(StudyMaterial).filter(StudyMaterial.title == m["title"]).first()
        if existing:
            # 更新浏览量，使排序差异明显
            existing.views = views_values[i % len(views_values)]
            print(f"  [UPDATE] 更新资料浏览量: {m['title']} -> {existing.views}")
            continue

        existing_count += 1
        material = StudyMaterial(
            id=f"material-{existing_count:03d}",
            **m,
            views=views_values[i % len(views_values)],
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
        {
            "user_id": "user-001",
            "subject": "英语",
            "question": "选择正确的连接词：I don't know ______ he will come tomorrow.",
            "correct_answer": "if / whether",
            "user_answer": "that",
            "analysis": "错误原因：宾语从句表示'是否'时，要用 if 或 whether 引导，that 无意义。",
            "knowledge_point": "宾语从句",
            "tags": "语法,连接词,易错",
            "source": "单元测试",
            "difficulty": 2,
            "status": "reviewing",
        },
        {
            "user_id": "user-001",
            "subject": "物理",
            "question": "一个物体在水平面上受到 20N 的水平拉力，移动了 5m，求拉力做的功。",
            "correct_answer": "100 J",
            "user_answer": "25 J",
            "analysis": "错误原因：公式记错。功 W = Fs = 20N × 5m = 100J。",
            "knowledge_point": "功的计算",
            "tags": "公式,计算,易错",
            "source": "作业",
            "difficulty": 1,
            "status": "unsolved",
        },
        {
            "user_id": "user-001",
            "subject": "化学",
            "question": "计算 36g 水的物质的量是多少？（已知 H₂O 的摩尔质量为 18g/mol）",
            "correct_answer": "2 mol",
            "user_answer": "0.5 mol",
            "analysis": "错误原因：公式用反了。n = m/M = 36g / 18g/mol = 2mol。",
            "knowledge_point": "物质的量",
            "tags": "计算,摩尔质量,易错",
            "source": "课堂练习",
            "difficulty": 1,
            "status": "mastered",
        },
        {
            "user_id": "user-001",
            "subject": "生物",
            "question": "绿色植物进行光合作用的场所是？",
            "correct_answer": "叶绿体",
            "user_answer": "线粒体",
            "analysis": "错误原因：混淆了光合作用和呼吸作用的场所。光合作用在叶绿体进行，呼吸作用主要在线粒体进行。",
            "knowledge_point": "光合作用",
            "tags": "基础,场所,易错",
            "source": "期中考试",
            "difficulty": 1,
            "status": "unsolved",
        },
    ]

    existing_count = db.query(Mistake).count()

    for i, m in enumerate(mistakes):
        existing = db.query(Mistake).filter(Mistake.question == m["question"]).first()
        if existing:
            print(f"  [SKIP] 错题已存在")
            continue

        existing_count += 1
        mistake = Mistake(
            id=f"mistake-{existing_count:03d}",
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
        {
            "user_id": "user-001",
            "subject": "化学",
            "type": "fill_blank",
            "question": "9g 水的物质的量是 ______ mol。（H₂O 的摩尔质量为 18g/mol）",
            "options": None,
            "correct_answer": "0.5",
            "explanation": "n = m/M = 9g / 18g/mol = 0.5mol。",
            "knowledge_point": "物质的量",
            "difficulty": 1,
        },
        {
            "user_id": "user-001",
            "subject": "生物",
            "type": "choice",
            "question": "植物细胞进行光合作用的场所是？",
            "options": '["线粒体", "叶绿体", "核糖体", "高尔基体"]',
            "correct_answer": "1",
            "explanation": "叶绿体是植物细胞进行光合作用的场所。",
            "knowledge_point": "光合作用",
            "difficulty": 1,
        },
    ]

    existing_count = db.query(Exercise).count()

    for i, e in enumerate(exercises):
        existing = db.query(Exercise).filter(Exercise.question == e["question"]).first()
        if existing:
            print(f"  [SKIP] 练习题已存在")
            continue

        existing_count += 1
        exercise = Exercise(
            id=f"exercise-{existing_count:03d}",
            **e,
            source="manual",
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(exercise)
        print(f"  [OK] 创建练习: {e['subject']} - {e['knowledge_point']}")

    db.commit()


def create_tasks(db: Session):
    """创建今日任务"""
    print("[INIT] 创建今日任务...")

    tasks_data = [
        {
            "user_id": "user-001",
            "title": "完成 5 道数学练习题",
            "description": "重点练习一元二次方程和三角函数",
            "subject": "数学",
            "priority": "high",
            "status": "pending",
        },
        {
            "user_id": "user-001",
            "title": "复习英语现在完成时",
            "description": "阅读现在完成时用法详解并做相关练习",
            "subject": "英语",
            "priority": "medium",
            "status": "pending",
        },
        {
            "user_id": "user-001",
            "title": "整理牛顿三大定律笔记",
            "description": "归纳牛顿三定律内容和应用场景",
            "subject": "物理",
            "priority": "medium",
            "status": "completed",
        },
        {
            "user_id": "user-001",
            "title": "背诵化学元素周期表前 20 号",
            "description": "记忆元素名称、符号和原子序数",
            "subject": "化学",
            "priority": "low",
            "status": "pending",
        },
        {
            "user_id": "user-001",
            "title": "阅读光合作用资料",
            "description": "理解光合作用与呼吸作用的区别",
            "subject": "生物",
            "priority": "medium",
            "status": "completed",
        },
    ]

    existing_count = db.query(Task).count()

    for i, t in enumerate(tasks_data):
        existing = db.query(Task).filter(Task.title == t["title"], Task.user_id == t["user_id"]).first()
        if existing:
            print(f"  [SKIP] 任务已存在: {t['title']}")
            continue

        existing_count += 1
        task = Task(
            id=f"task-{existing_count:03d}",
            **t,
            created_at=datetime.utcnow(),
        )
        db.add(task)
        print(f"  [OK] 创建任务: {t['title']}")

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

    existing_count = db.query(AssessmentReport).count()

    for i, r in enumerate(reports):
        existing = db.query(AssessmentReport).filter(AssessmentReport.user_id == r["user_id"]).first()
        if existing:
            print(f"  [SKIP] 评估报告已存在")
            continue

        existing_count += 1
        report = AssessmentReport(
            id=f"report-{existing_count:03d}",
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
        create_tasks(db)
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
        print(f"  今日任务: {db.query(Task).count()}")
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
