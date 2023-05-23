from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS


conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        isCompleted INTEGER NOT NULL,
        color TEXT NOT NULL,
        date TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

app = Flask(__name__)
CORS(app)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    is_completed = request.args.get('isCompleted')

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    if is_completed is not None and is_completed.lower() == 'true':
        cursor.execute('SELECT * FROM tasks WHERE isCompleted = 1')
    else:
        cursor.execute('SELECT * FROM tasks')

    tasks = []
    for row in cursor.fetchall():
        task = {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'isCompleted': bool(row[3]),
            'color': row[4],
            'date': row[5]
        }
        tasks.append(task)

    conn.close()

    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    new_task = {
        'title': request.json['title'],
        'description': request.json['description'],
        'isCompleted': request.json['isCompleted'],
        'color': request.json['color'],
        'date': request.json['date']
    }

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (title, description, isCompleted, color, date) VALUES (?, ?, ?, ?, ?)',
                   (new_task['title'], new_task['description'], new_task['isCompleted'], new_task['color'], new_task['date']))
    conn.commit()
    new_task_id = cursor.lastrowid
    conn.close()

    new_task['id'] = new_task_id

    return jsonify(new_task), 201


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    is_completed = data.get('isCompleted')
    color = data.get('color')
    date = data.get('date')
    cursor.execute('UPDATE tasks SET title=?, description=?, isCompleted=?, color=?, date=? WHERE id=?',
                   (title, description, is_completed, color, date, task_id))
    conn.commit()
    if cursor.rowcount > 0:
        response = {'message': 'Task updated successfully'}
    else:
        response = {'message': 'Task not found'}

    conn.close()

    return jsonify(response)


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    if task is None:
        conn.close()
        return jsonify({'message': 'Task not found'})
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task deleted successfully'})


@app.route('/tasks/completed', methods=['DELETE'])
def delete_completed_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE isCompleted = 1')
    conn.commit()
    conn.close()
    return jsonify({'message': 'Completed tasks deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)