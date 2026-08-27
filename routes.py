import json
from flask import request, jsonify

TASKS_FILE = 'tasks.json'

def load_tasks():
    try:
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
            # Ensure tasks are in a list if the file is empty or malformed
            if not isinstance(tasks, list):
                return []
            return tasks
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # If the file is empty or contains invalid JSON, return an empty list
        # This also prevents the API from crashing if tasks.json is empty on first run.
        return [] 

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def get_next_id(tasks):
    if not tasks:
        return 1
    # Find the maximum ID and add 1
    return max(task.get('id', 0) for task in tasks) + 1

def initialize_routes(app):
    @app.route('/tasks', methods=['GET'])
    def get_tasks():
        tasks = load_tasks()
        return jsonify(tasks)

    @app.route('/tasks', methods=['POST'])
    def create_task():
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400

        tasks = load_tasks()
        new_task = {
            'id': get_next_id(tasks),
            'title': data['title'],
            'description': data.get('description', ''),
            'status': data.get('status', 'pending') # Default status
        }
        tasks.append(new_task)
        save_tasks(tasks)
        return jsonify(new_task), 201

    @app.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        tasks = load_tasks()
        # Find task by ID
        task = next((t for t in tasks if t.get('id') == task_id), None)
        if task:
            return jsonify(task)
        return jsonify({'error': 'Task not found'}), 404

    @app.route('/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        tasks = load_tasks()
        task_index = next((i for i, t in enumerate(tasks) if t.get('id') == task_id), None)

        if task_index is None:
            return jsonify({'error': 'Task not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No update data provided'}), 400

        # Update fields if they exist in the request data
        # Ensure we don't overwrite fields if they are not provided
        if 'title' in data:
            tasks[task_index]['title'] = data['title']
        if 'description' in data:
            tasks[task_index]['description'] = data['description']
        if 'status' in data:
            tasks[task_index]['status'] = data['status']
            
        save_tasks(tasks)
        return jsonify(tasks[task_index])

    @app.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        tasks = load_tasks()
        initial_length = len(tasks)
        # Filter out the task to be deleted
        tasks = [t for t in tasks if t.get('id') != task_id]
        
        if len(tasks) == initial_length:
            # If the length didn't change, the task was not found
            return jsonify({'error': 'Task not found'}), 404

        save_tasks(tasks)
        return jsonify({'message': 'Task deleted successfully'})
