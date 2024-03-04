from flask import Blueprint, jsonify,request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime,timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 


@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []
    window = request.args.get('window', None)
    completed = request.args.get('completed', None)
    if completed is not None:
         completed = bool(completed)
         todos = Todo.query.filter_by(completed=completed)
    if window is not None:
         window = int(window)
         todos = Todo.query.filter(Todo.deadline_at <= (datetime.now() + timedelta(days=int(window))))
    for todo in todos:
       result.append(todo.to_dict())
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
       return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    todo = Todo(
       title=request.json.get('title'),
       description=request.json.get('description'),
       completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
       todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    if 'title' not in request.json:
         return jsonify({"error": "Title is required"}), 400
    if 'extra' in request.json:
         return jsonify({"error": "Extra is not allowed"}), 400
    # Adds a new record to the database or will update an existing record
    db.session.add(todo)
    # Commits the changes to the database, this must be called for the changes to be saved
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
       return jsonify({'error': 'Todo not found'}), 404
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
       return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
