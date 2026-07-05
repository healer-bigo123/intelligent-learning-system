"""
数据库备份管理脚本

功能特性:
1. 支持完整备份和增量备份
2. 自动清理过期备份
3. 备份成功/失败通知
4. 备份恢复测试
5. 配置灵活的备份策略

执行方式:
    python backup.py full         # 执行完整备份
    python backup.py incremental  # 执行增量备份
    python backup.py list         # 列出所有备份
    python backup.py restore <备份文件名>  # 恢复指定备份
    python backup.py test         # 测试备份恢复
    python backup.py clean        # 清理过期备份

配置说明:
    - BACKUP_DIR: 备份存储目录 (默认: ./data/backups)
    - FULL_BACKUP_INTERVAL: 完整备份间隔(小时) (默认: 24)
    - INCREMENTAL_INTERVAL: 增量备份间隔(小时) (默认: 1)
    - RETENTION_DAYS: 备份保留天数 (默认: 30)
    - MAX_BACKUPS: 最大备份数限制 (默认: 100)
"""
import os
import sys
import shutil
import sqlite3
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# 配置参数
BACKUP_DIR = "./data/backups"
FULL_BACKUP_INTERVAL = 24  # 小时
INCREMENTAL_INTERVAL = 1   # 小时
RETENTION_DAYS = 30        # 天
MAX_BACKUPS = 100         # 最大备份数
DATABASE_PATH = "./data/smart_learning.db"

def get_backup_dir():
    """获取备份目录"""
    backup_dir = Path(BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir

def get_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_datetime_from_filename(filename):
    """从备份文件名提取时间"""
    try:
        parts = filename.split("_")
        if len(parts) >= 2:
            date_str = parts[0]
            time_str = parts[1].split(".")[0]
            return datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
    except:
        return None
    return None

def create_full_backup():
    """创建完整数据库备份"""
    try:
        backup_dir = get_backup_dir()
        backup_name = f"full_backup_{get_timestamp()}.db"
        backup_path = backup_dir / backup_name
        
        # 确保数据库目录存在
        os.makedirs("./data", exist_ok=True)
        
        # 执行备份
        conn = sqlite3.connect(DATABASE_PATH)
        with backup_path.open("wb") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n".encode("utf-8"))
        conn.close()
        
        # 记录备份元数据
        metadata = {
            "type": "full",
            "timestamp": datetime.now().isoformat(),
            "size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2),
            "database": DATABASE_PATH
        }
        metadata_path = backup_dir / f"{backup_name}.metadata.json"
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"[OK] 完整备份创建成功: {backup_name} ({metadata['size_mb']} MB)")
        send_notification("success", f"完整备份成功: {backup_name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 完整备份失败: {e}")
        send_notification("error", f"完整备份失败: {str(e)}")
        return False

def create_incremental_backup():
    """创建增量备份"""
    try:
        backup_dir = get_backup_dir()
        backup_name = f"inc_backup_{get_timestamp()}.db"
        backup_path = backup_dir / backup_name
        
        # 检查上一次完整备份
        last_full = find_last_full_backup()
        if not last_full:
            print("[INFO] 未找到完整备份，执行完整备份")
            return create_full_backup()
        
        # 获取上一次备份时间
        last_time = get_datetime_from_filename(last_full)
        if not last_time:
            last_time = datetime.now() - timedelta(hours=24)
        
        # 执行增量备份（获取变化的数据）
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 创建增量备份文件
        with backup_path.open("w", encoding="utf-8") as f:
            # 记录增量备份的基准时间
            f.write(f"-- INCREMENTAL BACKUP FROM {last_time.isoformat()}\n")
            f.write(f"-- BACKUP TIME: {datetime.now().isoformat()}\n")
            f.write("\n")
            
            # 备份自上次备份以来变化的数据
            tables_to_backup = [
                "users", "mistakes", "exercises", "exercise_records", 
                "study_activities", "chat_messages", "notifications"
            ]
            
            for table in tables_to_backup:
                try:
                    cursor.execute(f"SELECT * FROM {table} WHERE created_at >= ?", 
                                  (last_time.strftime("%Y-%m-%d %H:%M:%S"),))
                    rows = cursor.fetchall()
                    if rows:
                        f.write(f"-- TABLE: {table} ({len(rows)} rows)\n")
                        for row in rows:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, str):
                                    values.append(f"'{val.replace(\"'\", \"''\")}'")
                                else:
                                    values.append(str(val))
                            f.write(f"INSERT INTO {table} VALUES ({', '.join(values)});\n")
                        f.write("\n")
                except Exception as e:
                    print(f"[WARN] 表 {table} 备份失败: {e}")
        
        conn.close()
        
        # 记录元数据
        metadata = {
            "type": "incremental",
            "timestamp": datetime.now().isoformat(),
            "based_on": last_full,
            "size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2),
            "database": DATABASE_PATH
        }
        metadata_path = backup_dir / f"{backup_name}.metadata.json"
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"[OK] 增量备份创建成功: {backup_name} ({metadata['size_mb']} MB)")
        send_notification("success", f"增量备份成功: {backup_name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 增量备份失败: {e}")
        send_notification("error", f"增量备份失败: {str(e)}")
        return False

def find_last_full_backup():
    """查找上一次完整备份"""
    backup_dir = get_backup_dir()
    full_backups = sorted(backup_dir.glob("full_backup_*.db"))
    if full_backups:
        return full_backups[-1].name
    return None

def list_backups():
    """列出所有备份"""
    backup_dir = get_backup_dir()
    backups = []
    
    for file in backup_dir.glob("*.db"):
        if file.name.endswith(".metadata.json"):
            continue
        
        metadata_path = backup_dir / f"{file.name}.metadata.json"
        metadata = {}
        if metadata_path.exists():
            with metadata_path.open("r", encoding="utf-8") as f:
                metadata = json.load(f)
        
        backups.append({
            "name": file.name,
            "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(file.stat().st_mtime),
            "type": metadata.get("type", "unknown"),
            "metadata": metadata
        })
    
    # 按时间排序
    backups.sort(key=lambda x: x["created_at"], reverse=True)
    
    print(f"{'名称':<40} {'类型':<10} {'大小(MB)':<10} {'创建时间'}")
    print("-" * 80)
    for backup in backups:
        print(f"{backup['name']:<40} {backup['type']:<10} {backup['size_mb']:<10.2f} {backup['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n总计: {len(backups)} 个备份")
    return backups

def restore_backup(backup_name):
    """恢复指定备份"""
    try:
        backup_dir = get_backup_dir()
        backup_path = backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"[ERROR] 备份文件不存在: {backup_name}")
            return False
        
        # 确保目标目录存在
        os.makedirs("./data", exist_ok=True)
        
        # 先备份当前数据库
        current_backup = f"./data/smart_learning.db.bak_{get_timestamp()}"
        if os.path.exists(DATABASE_PATH):
            shutil.copy(DATABASE_PATH, current_backup)
            print(f"[INFO] 已备份当前数据库到: {current_backup}")
        
        # 检查备份类型
        if backup_name.startswith("full_backup_"):
            # 完整备份恢复
            conn = sqlite3.connect(DATABASE_PATH)
            with backup_path.open("r", encoding="utf-8") as f:
                sql_script = f.read()
            conn.executescript(sql_script)
            conn.commit()
            conn.close()
            print(f"[OK] 完整备份恢复成功: {backup_name}")
            send_notification("success", f"备份恢复成功: {backup_name}")
        
        elif backup_name.startswith("inc_backup_"):
            # 增量备份恢复需要先恢复完整备份
            print("[INFO] 增量备份需要先恢复完整备份")
            last_full = find_last_full_backup()
            if last_full:
                restore_backup(last_full)
                # 应用增量备份
                conn = sqlite3.connect(DATABASE_PATH)
                with backup_path.open("r", encoding="utf-8") as f:
                    sql_script = f.read()
                conn.executescript(sql_script)
                conn.commit()
                conn.close()
                print(f"[OK] 增量备份恢复成功: {backup_name}")
                send_notification("success", f"增量备份恢复成功: {backup_name}")
            else:
                print("[ERROR] 未找到完整备份，无法恢复增量备份")
                return False
        
        else:
            print(f"[ERROR] 未知备份类型: {backup_name}")
            return False
        
        # 验证恢复
        verify_database()
        return True
        
    except Exception as e:
        print(f"[ERROR] 备份恢复失败: {e}")
        # 尝试恢复原数据库
        if os.path.exists(current_backup):
            shutil.copy(current_backup, DATABASE_PATH)
            print(f"[INFO] 已恢复到恢复前的数据库状态")
        send_notification("error", f"备份恢复失败: {str(e)}")
        return False

def verify_database():
    """验证数据库完整性"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("PRAGMA integrity_check")
        result = conn.execute("PRAGMA integrity_check").fetchone()
        if result and result[0] == "ok":
            print("[OK] 数据库完整性检查通过")
            conn.close()
            return True
        else:
            print(f"[ERROR] 数据库完整性检查失败: {result}")
            conn.close()
            return False
    except Exception as e:
        print(f"[ERROR] 数据库验证失败: {e}")
        return False

def test_backup_restore():
    """测试备份恢复功能"""
    print("[INFO] 开始备份恢复测试...")
    
    # 创建测试备份
    if not create_full_backup():
        print("[ERROR] 测试失败: 备份创建失败")
        return False
    
    # 查找最新备份
    backup_dir = get_backup_dir()
    backups = sorted(backup_dir.glob("full_backup_*.db"))
    if not backups:
        print("[ERROR] 测试失败: 未找到备份文件")
        return False
    
    latest_backup = backups[-1]
    print(f"[INFO] 测试恢复: {latest_backup.name}")
    
    # 恢复备份到临时位置
    test_db = "./data/test_restore.db"
    try:
        shutil.copy(latest_backup, test_db)
        conn = sqlite3.connect(test_db)
        result = conn.execute("PRAGMA integrity_check").fetchone()
        conn.close()
        
        if result and result[0] == "ok":
            print(f"[OK] 备份恢复测试通过: {latest_backup.name}")
            send_notification("success", "备份恢复测试通过")
            os.remove(test_db)
            return True
        else:
            print("[ERROR] 测试失败: 备份恢复后完整性检查失败")
            os.remove(test_db)
            return False
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        if os.path.exists(test_db):
            os.remove(test_db)
        return False

def clean_old_backups():
    """清理过期备份"""
    try:
        backup_dir = get_backup_dir()
        backups = []
        
        for file in backup_dir.glob("*.db"):
            if file.name.endswith(".metadata.json"):
                continue
            backups.append((file, datetime.fromtimestamp(file.stat().st_mtime)))
        
        # 按时间排序
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # 删除过期备份
        deleted_count = 0
        for file, mtime in backups:
            # 检查是否过期
            if datetime.now() - mtime > timedelta(days=RETENTION_DAYS):
                os.remove(file)
                metadata_path = backup_dir / f"{file.name}.metadata.json"
                if metadata_path.exists():
                    os.remove(metadata_path)
                deleted_count += 1
        
        # 检查是否超过最大备份数
        backups = list(backup_dir.glob("*.db"))
        backups = [f for f in backups if not f.name.endswith(".metadata.json")]
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        while len(backups) > MAX_BACKUPS:
            oldest = backups.pop()
            os.remove(oldest)
            metadata_path = backup_dir / f"{oldest.name}.metadata.json"
            if metadata_path.exists():
                os.remove(metadata_path)
            deleted_count += 1
        
        print(f"[OK] 清理完成，共删除 {deleted_count} 个过期备份")
        return True
        
    except Exception as e:
        print(f"[ERROR] 清理备份失败: {e}")
        return False

def send_notification(level, message):
    """发送备份通知"""
    # 可以扩展为邮件、钉钉、微信等通知
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 记录到日志文件
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "backup.log"
    
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{level.upper()}] {message}\n")
    
    # 控制台输出
    if level == "success":
        print(f"[NOTIFY] ✅ {message}")
    elif level == "error":
        print(f"[NOTIFY] ❌ {message}")
    else:
        print(f"[NOTIFY] ℹ️ {message}")

def show_help():
    """显示帮助信息"""
    print("数据库备份管理脚本")
    print("=" * 50)
    print("用法: python backup.py <命令>")
    print("")
    print("命令列表:")
    print("  full         - 执行完整备份")
    print("  incremental  - 执行增量备份")
    print("  list         - 列出所有备份")
    print("  restore <文件> - 恢复指定备份")
    print("  test         - 测试备份恢复功能")
    print("  clean        - 清理过期备份")
    print("  help         - 显示此帮助信息")
    print("")
    print("配置参数:")
    print(f"  备份目录: {BACKUP_DIR}")
    print(f"  完整备份间隔: {FULL_BACKUP_INTERVAL} 小时")
    print(f"  增量备份间隔: {INCREMENTAL_INTERVAL} 小时")
    print(f"  备份保留天数: {RETENTION_DAYS} 天")
    print(f"  最大备份数: {MAX_BACKUPS}")
    print("=" * 50)

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "full":
        create_full_backup()
    
    elif command == "incremental":
        create_incremental_backup()
    
    elif command == "list":
        list_backups()
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("用法: python backup.py restore <备份文件名>")
            sys.exit(1)
        backup_name = sys.argv[2]
        restore_backup(backup_name)
    
    elif command == "test":
        test_backup_restore()
    
    elif command == "clean":
        clean_old_backups()
    
    elif command == "help":
        show_help()
    
    else:
        print(f"未知命令: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()