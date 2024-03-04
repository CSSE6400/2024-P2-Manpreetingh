from flask import Blueprint, jsonify,request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime,timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []
    completed = request.args.get('completed', default=None, type=bool)
    deadline = request.args.get('window', default=None, type=str)
    if deadline:
         window_end = (datetime.now() + timedelta(days=int(deadline))).strftime("%Y-%m-%dT00:00:00")
    for todo in todos:
         if completed is None and deadline is None:
             result.append(todo.to_dict())  
         elif deadline is None and todo.completed == completed:
             result.append(todo.to_dict())
         # elif completed is None and todo.deadline <= 

         elif completed is None and \
                 todo.deadline_at and \
                 datetime.fromisoformat(str(todo.deadline_at)) <= datetime.fromisoformat(window_end):
             result.append(todo.to_dict())
         elif todo.deadline_at and \
                 todo.completed == completed and \
                 datetime.fromisoformat(str(todo.deadline_at)) <= datetime.fromisoformat(window_end):
             result.append(todo.to_dict())
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
    for todo_key in request.json.keys():
        if todo_key not in TEST_ITEM.keys():
            return jsonify({"error": "invalid key"}), 400
    if todo.id != request.json.get("id", todo.id):
         return jsonify({"error": "Todo id does not match"}), 400
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    
    if "deadline_at" in request.json:
       timeString : str = request.json.get("deadline_at")
       todo.deadline_at = datetime.fromisoformat(timeString)

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
