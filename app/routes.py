from flask import jsonify, request
from .import app, db
from .models import Task, User
from flask import abort 
from .auth import basic_auth, token_auth 

# Create a route to get all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    select_stmt = db.select(Task)
    # Get the tasks from the database
    tasks = db.session.execute(select_stmt).scalars().all()
    return [t.to_dict() for t in tasks]

# Create a route to get a single task by ID
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    # Get the task from the database by ID
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return {'error': f"Task with an ID of {task_id} does not exist"}, 404
    
# Create a route to create a new task
@app.route('/tasks', methods=['POST'])
@token_auth.login_required
def create_task(): 
    if not request.is_json:
        return jsonify({'error': "Where's the JSON buddy?"}), 400
    if 'title' in request.json:
        title = request.json['title']
    else:
        return jsonify({'error': 'Title is required'}), 400
    if 'description' in request.json:
        description = request.json['description']
    else:
        return jsonify({'error': 'Description is required'}), 400
    if 'dueDate' in request.json:
        dueDate = request.json['dueDate']
    else:
        dueDate = None
    user = token_auth.current_user()
    new_task = Task(title=title, description=description, due_date=dueDate, user_id = user.id)
    return new_task.to_dict(), 201

# Create a route to update a task and the PUT function
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_auth.login_required
def update_task(task_id):
    task = get_task(task_id) 
    current_user = token_auth.current_user()
    if not task:
        return jsonify({'error': f"Task with an ID of {task_id} does not exist"}), 404
    if task.user != current_user:
        abort(403)
    if not request.is_json:
        return jsonify({'error': "Where's the JSON buddy?"}), 400
    if 'title' in request.json:
        title = request.json['title']
    else:
        return jsonify({'error': 'Title is required'}), 400
    if 'description' in request.json:
        description = request.json['description']
    else:
        return jsonify({'error': 'Description is required'}), 400
    if 'completed' in request.json:
        completed = request.json['completed']
    else:
        return jsonify({'error': 'Completed field is required'}), 400
    # Update task
    task.title = request.json['title'] 
    task.description = request.json.get('description')
    task.completed = request.json.get('completed')

    db.session.commit()
    return jsonify(task)

# Create a route to delete a task and the DELETE function
@app.route('/tasks/<int:task_id>', methods=['DELETE'])  
@token_auth.login_required
def delete_task(task_id):
    task = get_task(task_id)
    current_user = token_auth.current_user()
    if not task:
        return jsonify({'error': f"Task with an ID of {task_id} does not exist"}), 404
    if task.user != current_user:
        abort(403)

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})

# Route for creating a new user
@app.route('/users', methods=['POST'])
def create_user():
# Request: Is it JSON?
    if not request.is_json:
        return {'error': "Where's the JSON Buddy?"}, 400
    # Get requested data
    data = request.json

    # Validating data fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400

    # Pull the individual data 
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check to see if any current users already have that username and/or email
    check_user = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_user:
        return {'error': "A user with that username and/or email already exists"}, 400

    # Create a new instance of user with the data from the request
    new_user = User(first_name=first_name, last_name=last_name,  username=username, email=email, password=password)

    return new_user.to_dict(), 201

# Route for getting user by id
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

# Create a route to update a user
@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def edit_users(user_id):
    if not request.is_json:
        return {"error": "Where's the JSON Buddy?"}, 400
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': f"user with id #{user_id} does not exist"}, 404
    current_user = token_auth.current_user()
    if not current_user:
        return {'error': "this is not your user. you do not have permission to edit"}, 403
    
    data = request.json
    user.update(**data)
    return user.to_dict()
    
# Create a route to delete a user
@app.route("/users/<int:user_id>", methods=["DELETE"])
@token_auth.login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        return {'Error': f'user with {user_id} does not exist'}, 404
    
    current_user = token_auth.current_user()
    if not current_user:
        return {'error': "you do not have permisson to delete this user"}, 403
    
    # delete the user
    user.delete()
    return {"Success": f'{user.id} was successfully deleted'}, 200

# Route for returning a token based on username and password   
@app.route('/token', methods=['GET'])
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user() 
    return user.get_token(), 200


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)