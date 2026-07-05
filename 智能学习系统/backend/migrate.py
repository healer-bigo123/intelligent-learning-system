"""
数据库迁移脚本 - 创建 external_data_records 表及必要的索引

执行方式:
    python migrate.py up      # 执行迁移
    python migrate.py down    # 回滚迁移
    python migrate.py status  # 查看状态
"""
import os
import sys
import sqlite3
import uuid
from datetime import datetime

DATABASE_PATH = "./data/smart_learning.db"
MIGRATION_TABLE = "migrations"
MIGRATION_NAME = "20260619_add_external_data_records"

def get_connection():
    """获取数据库连接"""
    os.makedirs("./data", exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_migrations_table(conn):
    """初始化迁移记录表"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            applied_at DATETIME NOT NULL,
            direction TEXT NOT NULL
        )
    """)
    conn.commit()

def is_migration_applied(conn, name):
    """检查迁移是否已应用"""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM migrations WHERE name = ?", (name,))
    return cursor.fetchone() is not None

def apply_migration(conn):
    """应用迁移 - 创建 external_data_records 表"""
    cursor = conn.cursor()
    
    # 创建外部数据记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_data_records (
            id TEXT PRIMARY KEY NOT NULL,
            source_id TEXT NOT NULL,
            data_type TEXT NOT NULL,
            data TEXT NOT NULL,
            title TEXT,
            subject TEXT,
            knowledge_point TEXT,
            is_active BOOLEAN DEFAULT 1,
            sync_time DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_source_id 
        ON external_data_records(source_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_data_type 
        ON external_data_records(data_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_title 
        ON external_data_records(title)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_subject 
        ON external_data_records(subject)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_knowledge_point 
        ON external_data_records(knowledge_point)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_is_active 
        ON external_data_records(is_active)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_created_at 
        ON external_data_records(created_at)
    """)
    
    # 复合索引：按来源和类型查询
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_source_type 
        ON external_data_records(source_id, data_type)
    """)
    
    # 复合索引：按学科和知识点查询
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_external_data_subject_kp 
        ON external_data_records(subject, knowledge_point)
    """)
    
    conn.commit()
    print("[OK] external_data_records 表及索引创建完成")

def rollback_migration(conn):
    """回滚迁移 - 删除 external_data_records 表"""
    cursor = conn.cursor()
    
    # 删除表（会自动删除所有相关索引）
    cursor.execute("DROP TABLE IF EXISTS external_data_records")
    conn.commit()
    print("[OK] external_data_records 表已删除")

def record_migration(conn, name, direction):
    """记录迁移"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO migrations (name, applied_at, direction)
        VALUES (?, ?, ?)
    """, (name, datetime.now().isoformat(), direction))
    conn.commit()

def main():
    if len(sys.argv) < 2:
        print("用法: python migrate.py [up|down|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    conn = None
    
    try:
        conn = get_connection()
        init_migrations_table(conn)
        
        if command == "up":
            if is_migration_applied(conn, MIGRATION_NAME):
                print(f"[INFO] 迁移 {MIGRATION_NAME} 已应用")
                sys.exit(0)
            
            apply_migration(conn)
            record_migration(conn, MIGRATION_NAME, "up")
            print(f"[OK] 迁移 {MIGRATION_NAME} 应用成功")
        
        elif command == "down":
            if not is_migration_applied(conn, MIGRATION_NAME):
                print(f"[INFO] 迁移 {MIGRATION_NAME} 未应用，无需回滚")
                sys.exit(0)
            
            rollback_migration(conn)
            record_migration(conn, MIGRATION_NAME + "_rollback", "down")
            print(f"[OK] 迁移 {MIGRATION_NAME} 回滚成功")
        
        elif command == "status":
            if is_migration_applied(conn, MIGRATION_NAME):
                print(f"[STATUS] 迁移 {MIGRATION_NAME}: 已应用")
            else:
                print(f"[STATUS] 迁移 {MIGRATION_NAME}: 未应用")
        
        else:
            print(f"未知命令: {command}")
            sys.exit(1)
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[ERROR] 迁移失败: {e}")
        sys.exit(1)
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()