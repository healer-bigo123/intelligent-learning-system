import sqlite3
import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any

class DatabaseChecker:
    """数据库全面检查器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.results = {
            'connection': None,
            'tables': [],
            'indexes': [],
            'data_integrity': [],
            'performance': [],
            'issues': [],
            'recommendations': []
        }
        self.issue_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

    def add_issue(self, severity: str, title: str, description: str, recommendation: str):
        """添加问题记录"""
        issue = {
            'severity': severity,
            'title': title,
            'description': description,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }
        self.results['issues'].append(issue)
        if severity in self.issue_severity:
            self.issue_severity[severity].append(issue)

    def add_recommendation(self, title: str, description: str, priority: str):
        """添加建议"""
        self.results['recommendations'].append({
            'title': title,
            'description': description,
            'priority': priority
        })

    def check_connection(self) -> bool:
        """检查数据库连接状态"""
        try:
            start_time = time.time()
            self.conn = sqlite3.connect(self.db_path, timeout=10)
            self.cursor = self.conn.cursor()
            connect_time = (time.time() - start_time) * 1000
            
            self.cursor.execute("SELECT 1")
            test_result = self.cursor.fetchone()
            
            self.results['connection'] = {
                'status': 'SUCCESS',
                'connect_time_ms': round(connect_time, 2),
                'test_query_result': test_result,
                'database_path': os.path.abspath(self.db_path),
                'database_size_mb': self._get_database_size()
            }
            return True
        except sqlite3.Error as e:
            self.results['connection'] = {
                'status': 'FAILED',
                'error': str(e),
                'database_path': os.path.abspath(self.db_path)
            }
            self.add_issue(
                'critical',
                '数据库连接失败',
                '无法连接到数据库: ' + str(e),
                '检查数据库文件路径是否正确，文件是否被其他进程占用，文件权限是否正确'
            )
            return False
        except Exception as e:
            self.results['connection'] = {
                'status': 'FAILED',
                'error': str(e),
                'database_path': os.path.abspath(self.db_path)
            }
            self.add_issue(
                'critical',
                '数据库连接异常',
                '连接数据库时发生未知错误: ' + str(e),
                '检查系统资源是否充足，尝试重启数据库相关服务'
            )
            return False

    def _get_database_size(self) -> float:
        """获取数据库文件大小（MB）"""
        if os.path.exists(self.db_path):
            return round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
        return 0.0

    def check_tables(self):
        """检查所有表的状态"""
        if not self.conn:
            return

        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                table_info = self._inspect_table(table_name)
                self.results['tables'].append(table_info)
                
                if not table_info.get('has_primary_key', False) and table_name != 'sqlite_sequence':
                    self.add_issue(
                        'medium',
                        '表 ' + table_name + ' 缺少主键',
                        '表 ' + table_name + ' 没有定义主键约束，可能影响数据完整性和查询性能',
                        '为表 ' + table_name + ' 添加主键字段'
                    )
        except sqlite3.Error as e:
            self.add_issue(
                'high',
                '表检查失败',
                '无法获取表信息: ' + str(e),
                '检查数据库结构是否损坏，考虑运行数据库修复工具'
            )

    def _inspect_table(self, table_name: str) -> Dict[str, Any]:
        """检查单个表的详细信息"""
        try:
            self.cursor.execute("PRAGMA table_info(" + table_name + ");")
            columns = self.cursor.fetchall()
            
            self.cursor.execute("SELECT COUNT(*) FROM " + table_name + ";")
            row_count = self.cursor.fetchone()[0]
            
            has_primary_key = any(col[5] == 1 for col in columns)
            
            self.cursor.execute("PRAGMA index_list(" + table_name + ");")
            indexes = self.cursor.fetchall()
            index_count = len(indexes)
            
            col_names = [col[1] for col in columns]
            if col_names:
                self.cursor.execute("SELECT SUM(LENGTH(CAST(" + ', '.join(col_names) + " AS TEXT))) FROM " + table_name + ";")
                size_bytes = self.cursor.fetchone()[0] or 0
            else:
                size_bytes = 0
            
            return {
                'name': table_name,
                'column_count': len(columns),
                'columns': col_names,
                'row_count': row_count,
                'has_primary_key': has_primary_key,
                'index_count': index_count,
                'indexes': [idx[1] for idx in indexes],
                'estimated_size_bytes': size_bytes,
                'estimated_size_mb': round(size_bytes / (1024 * 1024), 4)
            }
        except sqlite3.Error as e:
            return {
                'name': table_name,
                'error': str(e)
            }

    def check_indexes(self):
        """检查索引使用情况"""
        if not self.conn:
            return

        try:
            self.cursor.execute("""
                SELECT name, tbl_name, sql 
                FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
                ORDER BY tbl_name, name;
            """)
            indexes = self.cursor.fetchall()
            
            for idx in indexes:
                index_name, table_name, index_sql = idx
                self.results['indexes'].append({
                    'name': index_name,
                    'table_name': table_name,
                    'sql': index_sql
                })
            
            for table in self.results['tables']:
                if isinstance(table, dict) and table.get('row_count', 0) > 1000:
                    if table.get('index_count', 0) == 0:
                        self.add_issue(
                            'high',
                            '大表 ' + table["name"] + ' 缺少索引',
                            '表 ' + table["name"] + ' 包含 ' + str(table["row_count"]) + ' 条记录但没有索引，可能导致查询性能问题',
                            '为表 ' + table["name"] + ' 的常用查询字段添加索引'
                        )
        except sqlite3.Error as e:
            self.add_issue(
                'high',
                '索引检查失败',
                '无法获取索引信息: ' + str(e),
                '检查数据库权限，验证数据库文件完整性'
            )

    def check_data_integrity(self):
        """检查数据完整性"""
        if not self.conn:
            return

        try:
            self.cursor.execute("PRAGMA integrity_check;")
            integrity_result = self.cursor.fetchone()[0]
            
            if integrity_result != 'ok':
                self.add_issue(
                    'critical',
                    '数据库完整性检查失败',
                    'PRAGMA integrity_check 返回: ' + integrity_result,
                    '立即备份数据库，运行修复工具，如 sqlite3 .recover 或使用专业修复工具'
                )
            else:
                self.results['data_integrity'].append({
                    'check': 'integrity_check',
                    'result': 'OK'
                })
            
            self.cursor.execute("PRAGMA foreign_keys;")
            foreign_keys_status = self.cursor.fetchone()[0]
            self.results['data_integrity'].append({
                'check': 'foreign_keys_enabled',
                'result': foreign_keys_status == 1
            })
            
            if foreign_keys_status == 0:
                self.add_issue(
                    'medium',
                    '外键约束未启用',
                    'PRAGMA foreign_keys 返回 0，外键约束检查未启用',
                    '在数据库连接时执行 PRAGMA foreign_keys = ON 启用外键约束检查'
                )
            
            self._check_duplicate_data()
            
        except sqlite3.Error as e:
            self.add_issue(
                'critical',
                '数据完整性检查失败',
                '无法完成完整性检查: ' + str(e),
                '检查数据库文件是否损坏，尝试使用 sqlite3 命令行工具进行检查'
            )

    def _check_duplicate_data(self):
        """检查重复数据"""
        duplicate_checks = [
            ('users', 'username'),
            ('users', 'email'),
            ('users', 'phone'),
            ('learning_websites', 'url')
        ]
        
        for table, column in duplicate_checks:
            try:
                self.cursor.execute("""
                    SELECT """ + column + """, COUNT(*) as cnt 
                    FROM """ + table + """ 
                    WHERE """ + column + """ IS NOT NULL 
                    GROUP BY """ + column + """ 
                    HAVING COUNT(*) > 1;
                """)
                duplicates = self.cursor.fetchall()
                
                if duplicates:
                    self.add_issue(
                        'high',
                        '表 ' + table + ' 存在重复数据',
                        '字段 ' + column + ' 存在 ' + str(len(duplicates)) + ' 组重复值',
                        '清理表 ' + table + ' 中 ' + column + ' 字段的重复数据，考虑添加唯一约束'
                    )
            except sqlite3.Error:
                pass

    def check_performance(self):
        """检查查询性能"""
        if not self.conn:
            return

        try:
            performance_tests = []
            
            for table in self.results['tables'][:5]:
                if isinstance(table, dict) and table.get('row_count', 0) > 0:
                    table_name = table['name']
                    start_time = time.time()
                    self.cursor.execute("SELECT COUNT(*) FROM " + table_name + ";")
                    self.cursor.fetchone()
                    query_time = (time.time() - start_time) * 1000
                    
                    performance_tests.append({
                        'table': table_name,
                        'operation': 'COUNT',
                        'time_ms': round(query_time, 2),
                        'row_count': table['row_count']
                    })
                    
                    if query_time > 100:
                        self.add_issue(
                            'medium',
                            '表 ' + table_name + ' 查询性能较慢',
                            'COUNT(*) 查询耗时 ' + str(round(query_time, 2)) + 'ms，可能需要优化',
                            '检查表 ' + table_name + ' 是否有合适的索引，考虑优化查询语句'
                        )
            
            start_time = time.time()
            self.cursor.execute("""
                SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as cnt
                FROM study_activities 
                GROUP BY month 
                ORDER BY month DESC 
                LIMIT 12;
            """)
            self.cursor.fetchall()
            complex_query_time = (time.time() - start_time) * 1000
            
            performance_tests.append({
                'table': 'study_activities',
                'operation': 'GROUP_BY',
                'time_ms': round(complex_query_time, 2),
                'description': '按月分组统计'
            })
            
            self.results['performance'] = performance_tests
            
        except sqlite3.Error as e:
            self.add_issue(
                'medium',
                '性能测试失败',
                '无法完成性能测试: ' + str(e),
                '检查数据库是否有足够的资源，考虑在低峰期重新测试'
            )

    def check_disk_space(self):
        """检查磁盘空间"""
        try:
            if os.name == 'nt':
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(os.path.dirname(self.db_path)),
                    None,
                    ctypes.pointer(total_bytes),
                    ctypes.pointer(free_bytes)
                )
                total_gb = round(total_bytes.value / (1024 ** 3), 2)
                free_gb = round(free_bytes.value / (1024 ** 3), 2)
                used_gb = round(total_gb - free_gb, 2)
                free_percent = round((free_bytes.value / total_bytes.value) * 100, 2)
            else:
                statvfs = os.statvfs(self.db_path)
                total_gb = round(statvfs.f_frsize * statvfs.f_blocks / (1024 ** 3), 2)
                free_gb = round(statvfs.f_frsize * statvfs.f_bfree / (1024 ** 3), 2)
                used_gb = round(total_gb - free_gb, 2)
                free_percent = round((free_gb / total_gb) * 100, 2)
            
            self.results['disk_space'] = {
                'database_path': os.path.abspath(self.db_path),
                'drive_total_gb': total_gb,
                'drive_used_gb': used_gb,
                'drive_free_gb': free_gb,
                'drive_free_percent': free_percent,
                'database_size_mb': self.results['connection'].get('database_size_mb', 0)
            }
            
            if free_percent < 10:
                self.add_issue(
                    'critical',
                    '磁盘空间不足',
                    '数据库所在磁盘仅剩 ' + str(free_percent) + '% 可用空间 (' + str(free_gb) + ' GB)',
                    '立即清理磁盘空间或迁移数据库到空间充足的磁盘'
                )
            elif free_percent < 20:
                self.add_issue(
                    'high',
                    '磁盘空间即将不足',
                    '数据库所在磁盘剩余 ' + str(free_percent) + '% 可用空间 (' + str(free_gb) + ' GB)',
                    '规划磁盘清理或扩展，确保有足够的存储空间'
                )
                
        except Exception as e:
            self.add_issue(
                'low',
                '磁盘空间检查失败',
                '无法获取磁盘空间信息: ' + str(e),
                '手动检查数据库所在磁盘的可用空间'
            )

    def check_backup_status(self):
        """检查备份状态"""
        try:
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
            backups = []
            
            if os.path.exists(backup_dir):
                for filename in os.listdir(backup_dir):
                    if filename.endswith('.db') or filename.endswith('.backup'):
                        filepath = os.path.join(backup_dir, filename)
                        backups.append({
                            'filename': filename,
                            'path': filepath,
                            'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                            'modified_at': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                        })
            
            self.results['backup_status'] = {
                'backup_dir_exists': os.path.exists(backup_dir),
                'backup_count': len(backups),
                'backups': backups,
                'last_backup_time': backups[0]['modified_at'] if backups else None
            }
            
            if len(backups) == 0:
                self.add_issue(
                    'high',
                    '未找到数据库备份',
                    '在备份目录中未发现任何备份文件',
                    '立即执行数据库备份，建立定期备份计划'
                )
            else:
                last_backup = datetime.fromisoformat(backups[0]['modified_at'].replace('Z', '+00:00'))
                days_since_backup = (datetime.now() - last_backup).days
                if days_since_backup > 7:
                    self.add_issue(
                        'medium',
                        '备份已过期',
                        '最近一次备份是 ' + str(days_since_backup) + ' 天前',
                        '执行新的数据库备份，考虑设置自动备份任务'
                    )
                    
        except Exception as e:
            self.add_issue(
                'medium',
                '备份检查失败',
                '无法检查备份状态: ' + str(e),
                '手动检查备份目录和备份文件'
            )

    def run_full_check(self):
        """运行全面检查"""
        print("Starting full database check...")
        print("=" * 70)
        
        print("\n[1/6] Checking database connection...")
        if not self.check_connection():
            print("Database connection failed, cannot continue")
            return
        
        print("[2/6] Checking database tables...")
        self.check_tables()
        
        print("[3/6] Checking indexes...")
        self.check_indexes()
        
        print("[4/6] Checking data integrity...")
        self.check_data_integrity()
        
        print("[5/6] Checking performance...")
        self.check_performance()
        
        print("[6/6] Checking disk space and backup status...")
        self.check_disk_space()
        self.check_backup_status()
        
        print("\nCheck completed")
        print("=" * 70)

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 数据库全面检查报告")
        report.append("")
        report.append("检查时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        report.append("数据库路径: " + os.path.abspath(self.db_path))
        report.append("")
        report.append("---")
        report.append("")
        
        conn = self.results['connection']
        report.append("## 一、数据库连接状态")
        report.append("")
        if conn:
            if conn['status'] == 'SUCCESS':
                report.append("| 项目 | 状态 |")
                report.append("|------|------|")
                report.append("| 连接状态 | 成功 |")
                report.append("| 连接耗时 | " + str(conn['connect_time_ms']) + " ms |")
                report.append("| 数据库大小 | " + str(conn['database_size_mb']) + " MB |")
            else:
                report.append("| 项目 | 状态 |")
                report.append("|------|------|")
                report.append("| 连接状态 | 失败 |")
                report.append("| 错误信息 | " + conn['error'] + " |")
        report.append("")
        
        report.append("## 二、表结构统计")
        report.append("")
        tables = self.results['tables']
        report.append("总表数: " + str(len(tables)))
        report.append("")
        report.append("| 表名 | 记录数 | 字段数 | 索引数 | 主键 |")
        report.append("|------|-------|--------|--------|------|")
        for table in tables:
            if isinstance(table, dict) and 'name' in table:
                if 'error' in table:
                    report.append("| " + table['name'] + " | 错误 | " + table['error'] + " | - | - |")
                else:
                    pk_status = '有' if table.get('has_primary_key') else '无'
                    row_count = table.get('row_count', 0)
                    col_count = table.get('column_count', 0)
                    idx_count = table.get('index_count', 0)
                    report.append("| " + table['name'] + " | " + str(row_count) + " | " + str(col_count) + " | " + str(idx_count) + " | " + pk_status + " |")
        report.append("")
        
        report.append("## 三、问题发现")
        report.append("")
        issues = self.results['issues']
        if not issues:
            report.append("未发现问题")
        else:
            report.append("发现问题总数: " + str(len(issues)))
            report.append("")
            
            for severity in ['critical', 'high', 'medium', 'low']:
                severity_issues = self.issue_severity.get(severity, [])
                if severity_issues:
                    severity_labels = {
                        'critical': '严重',
                        'high': '高',
                        'medium': '中',
                        'low': '低'
                    }
                    report.append("### " + severity_labels[severity] + " (" + str(len(severity_issues)) + "个)")
                    report.append("")
                    for i, issue in enumerate(severity_issues, 1):
                        report.append("#### " + str(i) + ". " + issue['title'])
                        report.append("")
                        report.append("描述: " + issue['description'])
                        report.append("")
                        report.append("建议: " + issue['recommendation'])
                        report.append("")
        report.append("")
        
        report.append("## 四、优先级修复建议")
        report.append("")
        if not issues:
            report.append("数据库状态良好，无需紧急修复")
        else:
            sorted_issues = sorted(issues, key=lambda x: {
                'critical': 0, 'high': 1, 'medium': 2, 'low': 3
            }[x['severity']])
            
            report.append("| 优先级 | 问题标题 | 修复建议 |")
            report.append("|--------|---------|---------|")
            for i, issue in enumerate(sorted_issues[:10], 1):
                priority = {
                    'critical': 'P0 - 立即',
                    'high': 'P1 - 紧急',
                    'medium': 'P2 - 重要',
                    'low': 'P3 - 一般'
                }[issue['severity']]
                rec = issue['recommendation'][:50] + '...' if len(issue['recommendation']) > 50 else issue['recommendation']
                report.append("| " + priority + " | " + issue['title'] + " | " + rec + " |")
        report.append("")
        
        report.append("## 五、资源状态")
        report.append("")
        disk = self.results.get('disk_space')
        if disk:
            report.append("### 磁盘空间")
            report.append("")
            report.append("| 项目 | 值 |")
            report.append("|------|------|")
            report.append("| 磁盘总容量 | " + str(disk['drive_total_gb']) + " GB |")
            report.append("| 已使用 | " + str(disk['drive_used_gb']) + " GB |")
            report.append("| 可用空间 | " + str(disk['drive_free_gb']) + " GB |")
            report.append("| 可用比例 | " + str(disk['drive_free_percent']) + "% |")
            report.append("| 数据库文件 | " + str(disk['database_size_mb']) + " MB |")
            report.append("")
        
        backup = self.results.get('backup_status')
        if backup:
            report.append("### 备份状态")
            report.append("")
            report.append("| 项目 | 值 |")
            report.append("|------|------|")
            report.append("| 备份目录存在 | " + ('是' if backup['backup_dir_exists'] else '否') + " |")
            report.append("| 备份文件数 | " + str(backup['backup_count']) + " |")
            report.append("| 最近备份 | " + (backup['last_backup_time'] or '无') + " |")
            report.append("")
        
        perf = self.results.get('performance')
        if perf:
            report.append("## 六、性能测试")
            report.append("")
            report.append("| 表名 | 操作 | 耗时(ms) |")
            report.append("|------|------|---------|")
            for test in perf:
                report.append("| " + test.get('table', '-') + " | " + test.get('operation', '-') + " | " + str(test.get('time_ms', '-')) + " |")
            report.append("")
        
        report.append("---")
        report.append("")
        report.append("报告结束")
        
        return '\n'.join(report)

def find_database() -> str:
    possible_paths = [
        'data/smart_learning.db',
        'smart_learning.db',
        'app.db',
        '../data/smart_learning.db',
        os.path.join(os.path.dirname(__file__), 'data', 'smart_learning.db'),
        os.path.join(os.path.dirname(__file__), 'smart_learning.db')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

if __name__ == "__main__":
    db_path = find_database()
    
    if not db_path:
        print("Database file not found")
        print("Please verify database file location")
        sys.exit(1)
    
    print("Found database: " + os.path.abspath(db_path))
    print("")
    
    checker = DatabaseChecker(db_path)
    checker.run_full_check()
    
    report = checker.generate_report()
    
    print("\n" + "=" * 70)
    print("Database Check Report")
    print("=" * 70)
    print(report)
    
    report_filename = "database_check_report_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\nReport saved to: " + report_filename)
    print("\n" + "=" * 70)