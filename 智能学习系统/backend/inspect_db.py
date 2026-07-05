import sqlite3
import json

db_path = "c:/Users/admin/Desktop/plan/backend/data/smart_learning.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

report = {"tables": []}

for t in tables:
    table = t[0]
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    col_info = []
    for col in columns:
        col_info.append({
            "cid": col[0],
            "name": col[1],
            "type": col[2],
            "notnull": col[3],
            "default_value": col[4],
            "pk": col[5]
        })

    cursor.execute(f"PRAGMA index_list({table})")
    indexes = cursor.fetchall()
    idx_info = []
    for idx in indexes:
        idx_info.append({
            "seq": idx[0],
            "name": idx[1],
            "unique": idx[2],
            "origin": idx[3],
            "partial": idx[4]
        })

    try:
        cursor.execute(f"SELECT * FROM {table} LIMIT 20")
        rows = cursor.fetchall()
        data = rows
    except Exception as e:
        data = [f"Error: {e}"]

    report["tables"].append({
        "name": table,
        "columns": col_info,
        "indexes": idx_info,
        "data": data
    })

conn.close()
print(json.dumps(report, ensure_ascii=False, indent=2))
