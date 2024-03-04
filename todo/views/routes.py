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

@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []
    completed = request.args.get('completed', default=None, type=bool)
    deadline = request.args.get('window', default=None, type=str)
    for todo in todos:
      if completed is None and deadline is None:
             result.append(todo.to_dict())  
      elif deadline is None and todo.completed == completed:
             result.append(todo.to_dict())
         # elif completed is None and todo.deadline <= 
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
       return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
   if request.json.get("title") == None:
      return "Invalid todo: title missing", 400
   for todo_key in request.json.keys():
      if todo_key not in TEST_ITEM.keys():
         return jsonify({"error": "invalid key"}), 400
   todo = Todo(
         title=request.json.get("title"),
         description=request.json.get("description"),
         completed=request.json.get("completed", False),
   )
   if "deadline_at" in request.json:
         timeString : str = request.json.get("deadline_at")
         todo.deadline_at = datetime.fromisoformat(timeString)

     # adds a new record to the db or will update an existing record
   db.session.add(todo)
     # commits the changes to the database, must be called for the changes to be saved
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
