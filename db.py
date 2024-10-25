
import sqlite3

# 创建并连接到 SQLite 数据库
conn = sqlite3.connect('thesis.db')
cursor = conn.cursor()

# 创建表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS thesis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        supervisor TEXT NOT NULL,
        date TEXT NOT NULL
    )
''')

# 保存更改并关闭连接
conn.commit()
conn.close()


