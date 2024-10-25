from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)

# SQLite
DATABASE = 'thesis.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 创建数据库和表
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS thesis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            supervisor TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 添加论文
@app.route('/add', methods=['POST'])
def add_thesis():
    data = request.json
    query = "INSERT INTO thesis (title, author, supervisor, date) VALUES (?, ?, ?, ?)"
    values = (data['title'], data['author'], data['supervisor'], data['date'])
    
    conn = get_db_connection()
    conn.execute(query, values)
    conn.commit()
    conn.close()
    
    socketio.emit('update_theses')
    return jsonify({"message": "Thesis added successfully!"}), 201

# 更新论文信息
@app.route('/update/<int:thesis_id>', methods=['PUT'])
def update_thesis(thesis_id):
    data = request.json
    query = "UPDATE thesis SET title=?, author=?, supervisor=?, date=? WHERE id=?"
    values = (data['title'], data['author'], data['supervisor'], data['date'], thesis_id)
    
    conn = get_db_connection()
    conn.execute(query, values)
    conn.commit()
    conn.close()
    
    socketio.emit('update_theses')
    return jsonify({"message": "Thesis updated successfully!"})

# 删除论文
@app.route('/delete/<int:thesis_id>', methods=['DELETE'])
def delete_thesis(thesis_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM thesis WHERE id=?", (thesis_id,))
    conn.commit()
    conn.close()
    
    socketio.emit('update_theses')
    return jsonify({"message": "Thesis deleted successfully!"})

# 获取所有论文
@app.route('/theses', methods=['GET'])
def get_theses():
    conn = get_db_connection()
    theses = conn.execute("SELECT * FROM thesis").fetchall()
    conn.close()
    
    theses_list = [dict(thesis) for thesis in theses]
    return jsonify(theses_list)

# 搜索论文
@app.route('/search', methods=['GET'])
def search_thesis():
    query = request.args.get('query', '')
    conn = get_db_connection()
    theses = conn.execute("SELECT * FROM thesis WHERE title LIKE ? OR author LIKE ? OR supervisor LIKE ?", 
                          ('%' + query + '%', '%' + query + '%', '%' + query + '%')).fetchall()
    conn.close()
    
    theses_list = [dict(thesis) for thesis in theses]
    return jsonify(theses_list)

# 主页显示论文表格
@app.route('/')
def index():
    conn = get_db_connection()
    theses = conn.execute("SELECT * FROM thesis").fetchall()
    conn.close()
    
    return render_template('index.html', theses=theses)

if __name__ == '__main__':
    init_db()  # Initialize the database
    socketio.run(app,
                 host='0.0.0.0',
                 port=5000,
                 allow_unsafe_werkzeug=True)
