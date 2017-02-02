from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_reqparse import RequestParser

import connector
from models import scalers, task

app = Flask(__name__)
parser = RequestParser()

@app.route('/')
def index():
    return jsonify({"response" : "app is running perfectly fine"})

@app.route('/api/tasks', methods = ['POST'])
@parser.validate_arguments([
    {
        "name" : "urgency",
        "type" : str,
        "source" : "json",
        "required" : True
    },
    {
        "name" : "instruction",
        "type" : str,
        "source" : "json",
        "required" : True,
    },
    {
        "name" : "params",
        "type" : dict,
        "source" : "json",
        "required" : True
    },
    {
        "name" : "type",
        "type" : str,
        "source" : "json",
        "required" : True,
    }
])
def create_task(args):
    task_object = task.Task()
    task_object.instruction = args["instruction"]
    if args["urgency"] == "hour":
        task_object.deadLine = datetime.now() + timedelta(hours = 1)
    elif args["urgency"] == "day":
        task_object.deadLine = datetime.now() + timedelta(days = 1)
    elif args["urgency"] == "week":
        task_object.deadLine = datetime.now() + timedelta(days = 7)
    else:
        return jsonify({"response" : "invalid urgency"}), 400
    if validate_params_by_task(args['params'], args['type']) == True:
        task_object.params = args['params']
    else:
        return validate_params_by_task(args['params'], args['type'])

    task_object.save()
    available_scalers = scalers.Scaler.objects.order_by("active_tasks")
    scaler = available_scalers[0]
    scaler.tasksAssigned.append(task_object)
    scaler.active_tasks += 1
    scaler.save()
    return jsonify({"response" : {
        "taskId" : str(task_object.id),
        "params" : task_object.params,
        "type" : task_object.type,
        "createdAt" : task_object.created_at,
        "status" : task_object.status
    }})

@app.route('/api/tasks/<id>', methods=["PUT"])
def complete_task(id):
    task_object = task.Task.objects(id=id).first()
    task_object.completed_at = datetime.now()
    if request.args.get("status") in ["finished", "cancelled"]:
        task_object.status = request.args.get("status")
    else:
        return jsonify({"response" : "invalid status"}), 400
    task_object.save()
    scaler = scalers.Scaler.objects(tasksAssigned__contains=task_object).first()
    scaler.active_tasks -= 1
    scaler.save()
    return jsonify({"response" : {
        "taskId" : str(task_object.id),
        "params" : task_object.params,
        "type" : task_object.type,
        "createdAt" : task_object.created_at,
        "status" : task_object.status
    }})

@app.route('/api/tasks/<scalerId>')
def get_tasks(scalerId):
    try:
        scaler = scalers.Scaler.objects(id=scalerId).first()
        if not scaler:
            return jsonify({"response" : "invalid scaler id"}), 400
    except:
        return jsonify({"response" : "invalid scaler id"}), 400
    responseObject = []
    for t in scaler.tasksAssigned:
        responseObject.append({
        "taskId" : str(t.id),
        "params" : t.params,
        "type" : t.type,
        "createdAt" : t.created_at,
        "status" : t.status
    })
    return jsonify({"response" : {"tasks" : responseObject}})

@app.route('/api/tasks/unassign/<scalerId>', methods=['POST'])
def unassign(scalerId):
    try:
        scaler = scalers.Scaler.objects(id=scalerId).first()
        if not scaler:
            return jsonify({"response" : "invalid scaler id"}), 400
    except:
        return jsonify({"response" : "invalid scaler id"}), 400
    responseObject = []
    for t in scaler.tasksAssigned:
        responseObject.append({
        "taskId" : str(t.id),
        "params" : t.params,
        "type" : t.type,
        "createdAt" : t.created_at,
        "status" : t.status
    })
    scaler.tasksAssigned = []
    scaler.active_tasks = 0
    scaler.save()
    return jsonify({"response" : {"tasks" : responseObject}})

def validate_params_by_task(params, type):
    tasks_attachment_required = ['categorization', 'transcription', 'comparision', 'data_collection']
    if "attachment" not in params and type in tasks_attachment_required:
        return jsonify({"response" : "attachment is required"}), 400

    if type == "categorization":
        if "categories" not in params:
            return jsonify({"response" : "categories is required"}), 400
    elif type == "transcription":
        if "fields" not in params:
            return jsonify({"response" : "fields is required"}), 400
    elif type == "phonecall":
        if "script" not in params:
            return jsonify({"response" : "script is required"}), 400
        if "fields" not in params:
            return jsonify({"response" : "fields is required"}), 400
        if "entity_name" not in params:
            return jsonify({"response" : "entity_name is required"}), 400
        if "phone_number" not in params:
            return jsonify({"response" : "phone_number is required"}), 400
    elif type == 'comparision':
        if "choices" not in params:
            return jsonify({"response" : "choices is required"}), 400

    elif type == 'data_collection':
        if "fields" not in params:
            return jsonify({"response" : "fields is required"}), 400
    else:
        return jsonify({"response" : "invalid type"}), 400

    return True





if __name__ == '__main__':
    app.run(debug=True)