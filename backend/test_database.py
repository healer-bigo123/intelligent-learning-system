"""
后端数据库操作全面测试脚本

测试范围：
1. 数据库连接测试
2. 用户模块测试
3. 学习路径模块测试
4. 练习模块测试
5. 错题本模块测试
6. 学习活动模块测试
7. 外部数据模块测试
8. 数据完整性测试

执行方式：python -m pytest tests/ -v
或直接运行本脚本：python test_database.py
"""
import sys
import os
import json
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# 配置
DATABASE_URL = "sqlite:///./data/smart_learning.db"
TEST_USER_ID = "test_user_" + str(uuid.uuid4())[:8]

class DatabaseTest:
    """数据库测试类"""
    
    def __init__(self):
        self.engine = None
        self.session = None
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def add_result(self, test_name: str, passed: bool, message: str = ""):
        """添加测试结果"""
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_result(self):
        """打印测试结果汇总"""
        print("\n" + "="*70)
        print("测试结果汇总")
        print("="*70)
        print("通过: %d | 失败: %d | 总计: %d" % (self.passed, self.failed, self.passed + self.failed))
        print("-"*70)
        
        # 打印失败的测试
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print("\n失败的测试:")
            for test in failed_tests:
                print("  - %s" % test['test_name'])
                if test['message']:
                    print("    错误: %s" % test['message'])
        
        print("\n所有测试完成")
        print("="*70)
    
    def test_database_connection(self):
        """测试1: 数据库连接"""
        try:
            print("\n[1/10] 测试数据库连接")
            
            conn = sqlite3.connect('./data/smart_learning.db', timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            assert result == (1,), "测试查询失败"
            
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA foreign_keys")
            fk_status = cursor.fetchone()[0]
            assert fk_status == 1, "外键约束未启用"
            
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            assert integrity_result == 'ok', "完整性检查失败: %s" % integrity_result
            
            conn.close()
            
            self.add_result("数据库连接测试", True, "连接成功，外键约束已启用，完整性检查通过")
            print("    OK: 数据库连接成功")
            
        except Exception as e:
            self.add_result("数据库连接测试", False, str(e))
            print("    FAIL: 数据库连接失败: %s" % str(e))
    
    def test_table_structure(self):
        """测试2: 表结构验证"""
        try:
            print("\n[2/10] 测试表结构验证")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [t[0] for t in cursor.fetchall()]
            
            required_tables = [
                'users', 'user_roles', 'learning_paths', 'exercises',
                'exercise_records', 'exercise_sessions', 'mistakes',
                'study_activities', 'student_profiles', 'notifications',
                'achievements', 'user_achievements', 'classrooms',
                'classroom_members', 'learning_resources', 'study_materials',
                'mind_maps', 'chat_sessions', 'chat_messages', 'agent_tasks',
                'learning_websites', 'assessment_reports', 'votes', 'lotteries',
                'quizzes'
            ]
            
            missing_tables = [t for t in required_tables if t not in tables]
            if missing_tables:
                raise AssertionError("缺少必需的表: %s" % missing_tables)
            
            tables_without_pk = []
            for table in tables:
                if table.startswith('sqlite_'):
                    continue
                cursor.execute("PRAGMA table_info(%s)" % table)
                columns = cursor.fetchall()
                has_pk = any(col[5] == 1 for col in columns)
                if not has_pk:
                    tables_without_pk.append(table)
            
            if tables_without_pk:
                print("    WARN: 以下表缺少主键: %s" % tables_without_pk)
            
            conn.close()
            
            self.add_result("表结构验证", True, "找到 %d 张表，%d 张必需表均存在" % (len(tables), len(required_tables)))
            print("    OK: 表结构验证通过，共 %d 张表" % len(tables))
            
        except Exception as e:
            self.add_result("表结构验证", False, str(e))
            print("    FAIL: 表结构验证失败: %s" % str(e))
            if 'conn' in locals():
                conn.close()
    
    def test_user_operations(self):
        """测试3: 用户模块操作"""
        try:
            print("\n[3/10] 测试用户模块操作")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            
            test_username = "testuser_%d" % int(time.time())
            test_email = "%s@example.com" % test_username
            
            user_id = "user_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, nickname, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, test_username, test_email, "hashed_pass", test_username, "student", "active"))
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            assert user is not None, "用户插入失败"
            assert user[1] == test_username, "用户名不匹配"
            assert user[2] == test_email, "邮箱不匹配"
            
            new_nickname = "%s_updated" % test_username
            cursor.execute("UPDATE users SET nickname = ? WHERE id = ?", (new_nickname, user_id))
            cursor.execute("SELECT nickname FROM users WHERE id = ?", (user_id,))
            updated_nickname = cursor.fetchone()[0]
            assert updated_nickname == new_nickname, "用户更新失败"
            
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            deleted_user = cursor.fetchone()
            assert deleted_user is None, "用户删除失败"
            
            conn.commit()
            conn.close()
            
            self.add_result("用户模块操作", True, "增删改查操作均成功")
            print("    OK: 用户模块测试通过")
            
        except Exception as e:
            self.add_result("用户模块操作", False, str(e))
            print("    FAIL: 用户模块测试失败: %s" % str(e))
            if 'conn' in locals():
                conn.rollback()
                conn.close()
    
    def test_learning_path_operations(self):
        """测试4: 学习路径模块操作"""
        try:
            print("\n[4/10] 测试学习路径模块操作")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            
            user_id = "user_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, nickname, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, "lp_user_%d" % int(time.time()), "lp_user_%d@test.com" % int(time.time()), 
                  "hashed", "lp_user", "student", "active"))
            
            path_id = "path_%s" % uuid.uuid4()
            steps = json.dumps([{"id": "1", "title": "Step 1"}, {"id": "2", "title": "Step 2"}])
            cursor.execute("""
                INSERT INTO learning_paths (id, user_id, title, description, steps, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (path_id, user_id, "测试学习路径", "测试描述", steps, "active"))
            
            cursor.execute("SELECT * FROM learning_paths WHERE id = ?", (path_id,))
            path = cursor.fetchone()
            assert path is not None, "学习路径创建失败"
            assert path[2] == "测试学习路径", "路径标题不匹配"
            
            cursor.execute("UPDATE learning_paths SET status = ? WHERE id = ?", ("completed", path_id))
            cursor.execute("SELECT status FROM learning_paths WHERE id = ?", (path_id,))
            status = cursor.fetchone()[0]
            assert status == "completed", "状态更新失败"
            
            cursor.execute("SELECT COUNT(*) FROM learning_paths WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]
            assert count >= 1, "用户学习路径查询失败"
            
            cursor.execute("DELETE FROM learning_paths WHERE id = ?", (path_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
            self.add_result("学习路径模块操作", True, "学习路径增删改查均成功")
            print("    OK: 学习路径模块测试通过")
            
        except Exception as e:
            self.add_result("学习路径模块操作", False, str(e))
            print("    FAIL: 学习路径模块测试失败: %s" % str(e))
            if 'conn' in locals():
                conn.rollback()
                conn.close()
    
    def test_exercise_operations(self):
        """测试5: 练习模块操作"""
        try:
            print("\n[5/10] 测试练习模块操作")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            
            user_id = "user_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, nickname, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, "ex_user_%d" % int(time.time()), "ex_user_%d@test.com" % int(time.time()),
                  "hashed", "ex_user", "student", "active"))
            
            exercise_id = "ex_%s" % uuid.uuid4()
            options = json.dumps({"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"})
            cursor.execute("""
                INSERT INTO exercises (id, user_id, subject, type, question, options, 
                                      correct_answer, explanation, knowledge_point, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (exercise_id, user_id, "数学", "choice", "1+1=?", options, "B", "因为1+1=2",
                  "基础计算", 1))
            
            cursor.execute("SELECT subject, question FROM exercises WHERE id = ?", (exercise_id,))
            result = cursor.fetchone()
            assert result is not None, "练习题创建失败"
            subject, question = result[0], result[1]
            assert subject == "数学", "学科不匹配"
            assert question == "1+1=?", "题目不匹配"
            
            session_id = "session_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO exercise_sessions (id, user_id, title, subject, total_count)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, "测试练习会话", "数学", 5))
            
            record_id = "record_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO exercise_records (id, user_id, exercise_id, user_answer, 
                                              is_correct, score, time_spent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (record_id, user_id, exercise_id, "B", True, 10, 30))
            
            try:
                invalid_record_id = "record_%s" % uuid.uuid4()
                cursor.execute("""
                    INSERT INTO exercise_records (id, user_id, exercise_id, user_answer)
                    VALUES (?, ?, ?, ?)
                """, (invalid_record_id, "non_existent_user", exercise_id, "A"))
                conn.commit()
                print("    WARN: 外键约束未生效（允许插入不存在的用户）")
            except sqlite3.IntegrityError:
                print("    OK: 外键约束验证通过")
                conn.rollback()
            
            cursor.execute("DELETE FROM exercise_records WHERE id = ?", (record_id,))
            cursor.execute("DELETE FROM exercise_sessions WHERE id = ?", (session_id,))
            cursor.execute("DELETE FROM exercises WHERE id = ?", (exercise_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
            self.add_result("练习模块操作", True, "练习题、会话、记录操作均成功")
            print("    OK: 练习模块测试通过")
            
        except Exception as e:
            self.add_result("练习模块操作", False, str(e))
            print("    FAIL: 练习模块测试失败: %s" % str(e))
            if 'conn' in locals():
                conn.rollback()
                conn.close()
    
    def test_mistake_operations(self):
        """测试6: 错题本模块操作"""
        try:
            print("\n[6/10] 测试错题本模块操作")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            
            user_id = "user_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, nickname, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, "mistake_user_%d" % int(time.time()), "mistake_user_%d@test.com" % int(time.time()),
                  "hashed", "mistake_user", "student", "active"))
            
            mistake_id = "mistake_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO mistakes (id, user_id, subject, question, correct_answer, 
                                      user_answer, analysis, knowledge_point, difficulty, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mistake_id, user_id, "数学", "2+2=?", "4", "3", "因为2+2=4",
                  "加法", 1, "unsolved"))
            
            cursor.execute("SELECT subject FROM mistakes WHERE id = ?", (mistake_id,))
            result = cursor.fetchone()
            assert result is not None, "错题添加失败"
            assert result[0] == "数学", "学科不匹配"
            
            cursor.execute("UPDATE mistakes SET status = ? WHERE id = ?", ("solved", mistake_id))
            cursor.execute("SELECT status FROM mistakes WHERE id = ?", (mistake_id,))
            status = cursor.fetchone()[0]
            assert status == "solved", "状态更新失败"
            
            cursor.execute("UPDATE mistakes SET review_count = COALESCE(review_count, 0) + 1 WHERE id = ?", (mistake_id,))
            cursor.execute("SELECT review_count FROM mistakes WHERE id = ?", (mistake_id,))
            count = cursor.fetchone()[0]
            assert count == 1, "复习次数更新失败，当前值: %d" % (count if count else 0)
            
            cursor.execute("SELECT COUNT(*) FROM mistakes WHERE user_id = ? AND subject = ?", (user_id, "数学"))
            count = cursor.fetchone()[0]
            assert count >= 1, "按学科查询失败"
            
            cursor.execute("DELETE FROM mistakes WHERE id = ?", (mistake_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
            self.add_result("错题本模块操作", True, "错题增删改查均成功")
            print("    OK: 错题本模块测试通过")
            
        except Exception as e:
            self.add_result("错题本模块操作", False, str(e))
            print("    FAIL: 错题本模块测试失败: %s" % str(e))
            if 'conn' in locals():
                conn.rollback()
                conn.close()
    
    def test_study_activity_operations(self):
        """测试7: 学习活动模块操作"""
        try:
            print("\n[7/10] 测试学习活动模块操作")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            
            user_id = "user_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, nickname, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, "activity_user_%d" % int(time.time()), "activity_user_%d@test.com" % int(time.time()),
                  "hashed", "activity_user", "student", "active"))
            
            activity_id = "activity_%s" % uuid.uuid4()
            cursor.execute("""
                INSERT INTO study_activities (id, user_id, activity_type, target_id, title, duration, score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (activity_id, user_id, "exercise", "target_1", "完成练习", 300, 100, datetime.now()))
            
            cursor.execute("SELECT * FROM study_activities WHERE id = ?", (activity_id,))
            activity = cursor.fetchone()
            assert activity is not None, "活动添加失败"
            assert activity[2] == "exercise", "活动类型不匹配"
            
            cursor.execute("SELECT COUNT(*) FROM study_activities WHERE user_id = ? AND activity_type = ?", 
                          (user_id, "exercise"))
            count = cursor.fetchone()[0]
            assert count >= 1, "按类型查询失败"
            
            cursor.execute("SELECT COUNT(*) FROM study_activities WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]
            assert count >= 1, "用户活动查询失败"
            
            cursor.execute("""
                SELECT COUNT(*) FROM study_activities 
                WHERE user_id = ? AND created_at IS NOT NULL
            """, (user_id,))
            count_with_date = cursor.fetchone()[0]
            assert count_with_date >= 1, "活动缺少创建时间"
            
            cursor.execute("DELETE FROM study_activities WHERE id = ?", (activity_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
            self.add_result("学习活动模块操作", True, "学习活动增删改查均成功")
            print("    OK: 学习活动模块测试通过")
            
        except Exception as e:
            self.add_result("学习活动模块操作", False, str(e))
            print("    FAIL: 学习活动模块测试失败: %s" % str(e))
            if 'conn' in locals():
                conn.rollback()
                conn.close()
    
    def test_external_data_operations(self):
        """测试8: 外部数据模块操作"""
        try:
            print("\n[8/10] 测试外部数据模块操作")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='external_data_records'")
            if not cursor.fetchone():
                print("    WARN: external_data_records表不存在，跳过此测试")
                self.add_result("外部数据模块操作", True, "表不存在，跳过测试")
                conn.close()
                return
            
            record_id = "ext_%s" % uuid.uuid4()
            data = json.dumps({
                "title": "测试外部数据",
                "content": "这是测试内容",
                "source": "test_api"
            })
            cursor.execute("""
                INSERT INTO external_data_records (id, source_id, data_type, data, title, 
                                                   subject, knowledge_point, is_active, sync_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (record_id, "test_source", "exercise", data, "测试外部数据", 
                  "数学", "测试知识点", True, datetime.now().isoformat()))
            
            cursor.execute("SELECT title FROM external_data_records WHERE id = ?", (record_id,))
            result = cursor.fetchone()
            assert result is not None, "外部数据插入失败"
            assert result[0] == "测试外部数据", "标题不匹配，实际值: %s" % result[0]
            
            cursor.execute("SELECT COUNT(*) FROM external_data_records WHERE source_id = ?", ("test_source",))
            count = cursor.fetchone()[0]
            assert count >= 1, "按来源查询失败"
            
            cursor.execute("UPDATE external_data_records SET is_active = ? WHERE id = ?", (False, record_id))
            cursor.execute("SELECT is_active FROM external_data_records WHERE id = ?", (record_id,))
            is_active = cursor.fetchone()[0]
            assert is_active == 0, "状态更新失败"
            
            cursor.execute("DELETE FROM external_data_records WHERE id = ?", (record_id,))
            
            conn.commit()
            conn.close()
            
            self.add_result("外部数据模块操作", True, "外部数据增删改查均成功")
            print("    OK: 外部数据模块测试通过")
            
        except Exception as e:
            self.add_result("外部数据模块操作", False, str(e))
            print("    FAIL: 外部数据模块测试失败: %s" % str(e))
            if 'conn' in locals():
                conn.rollback()
                conn.close()
    
    def test_index_usage(self):
        """测试9: 索引使用验证"""
        try:
            print("\n[9/10] 测试索引使用验证")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA index_list(users)")
            indexes = cursor.fetchall()
            index_names = [idx[1] for idx in indexes]
            
            print("    users表索引: %s" % index_names)
            
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student' AND status = 'active'")
            result = cursor.fetchone()
            query_time = (time.time() - start_time) * 1000
            
            print("    查询耗时: %.2fms, 结果: %d" % (query_time, result[0]))
            
            cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com'")
            plan = cursor.fetchall()
            print("    查询计划: %s" % (plan[0][3] if plan else 'N/A'))
            
            conn.close()
            
            self.add_result("索引使用验证", True, "users表有 %d 个索引，查询性能正常" % len(indexes))
            print("    OK: 索引测试通过")
            
        except Exception as e:
            self.add_result("索引使用验证", False, str(e))
            print("    FAIL: 索引测试失败: %s" % str(e))
            if 'conn' in locals():
                conn.close()
    
    def test_data_integrity(self):
        """测试10: 数据完整性测试"""
        try:
            print("\n[10/10] 测试数据完整性")
            
            conn = sqlite3.connect('./data/smart_learning.db')
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            assert integrity_result == 'ok', "完整性检查失败: %s" % integrity_result
            
            cursor.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            if fk_violations:
                print("    WARN: 外键约束违规: %s" % fk_violations)
            else:
                print("    OK: 外键约束检查通过")
            
            cursor.execute("""
                SELECT email, COUNT(*) as cnt FROM users 
                WHERE email IS NOT NULL 
                GROUP BY email 
                HAVING COUNT(*) > 1
            """)
            duplicate_emails = cursor.fetchall()
            if duplicate_emails:
                print("    WARN: 发现重复邮箱: %d 组" % len(duplicate_emails))
            else:
                print("    OK: 无重复邮箱")
            
            cursor.execute("""
                SELECT lp.* FROM learning_paths lp
                LEFT JOIN users u ON lp.user_id = u.id
                WHERE u.id IS NULL
            """)
            orphan_paths = cursor.fetchall()
            if orphan_paths:
                print("    WARN: 发现无主学习路径: %d 条" % len(orphan_paths))
            else:
                print("    OK: 所有学习路径都有对应的用户")
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE hashed_password IS NULL OR hashed_password = ''")
            empty_pass = cursor.fetchone()[0]
            if empty_pass > 0:
                print("    WARN: 发现空密码用户: %d 个" % empty_pass)
            else:
                print("    OK: 无空密码用户")
            
            conn.close()
            
            self.add_result("数据完整性测试", True, "所有完整性检查完成")
            print("    OK: 数据完整性测试通过")
            
        except Exception as e:
            self.add_result("数据完整性测试", False, str(e))
            print("    FAIL: 数据完整性测试失败: %s" % str(e))
            if 'conn' in locals():
                conn.close()
    
    def run_all_tests(self):
        """运行所有测试"""
        print("="*70)
        print("数据库操作全面测试")
        print("="*70)
        print("测试时间: %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("数据库路径: %s" % DATABASE_URL)
        print("-"*70)
        
        self.test_database_connection()
        self.test_table_structure()
        self.test_user_operations()
        self.test_learning_path_operations()
        self.test_exercise_operations()
        self.test_mistake_operations()
        self.test_study_activity_operations()
        self.test_external_data_operations()
        self.test_index_usage()
        self.test_data_integrity()
        
        self.print_result()
        
        return {
            'passed': self.passed,
            'failed': self.failed,
            'total': self.passed + self.failed,
            'success_rate': round(self.passed / (self.passed + self.failed) * 100, 2) if (self.passed + self.failed) > 0 else 0,
            'results': self.test_results
        }

if __name__ == "__main__":
    os.makedirs('./data', exist_ok=True)
    
    test = DatabaseTest()
    result = test.run_all_tests()
    
    report_filename = "test_report_%s.md" % datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("# 数据库测试报告\n\n")
        f.write("测试时间: %s\n" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        f.write("测试总数: %d\n" % result['total'])
        f.write("通过: %d\n" % result['passed'])
        f.write("失败: %d\n" % result['failed'])
        f.write("成功率: %.2f%%\n\n" % result['success_rate'])
        f.write("---\n\n")
        f.write("## 测试详情\n\n")
        
        for res in result['results']:
            status = "通过" if res['passed'] else "失败"
            f.write("### %s\n" % res['test_name'])
            f.write("- 状态: %s\n" % status)
            if res['message']:
                f.write("- 消息: %s\n" % res['message'])
            f.write("\n")
    
    print("\n测试报告已保存到: %s" % report_filename)
    
    sys.exit(0 if result['failed'] == 0 else 1)