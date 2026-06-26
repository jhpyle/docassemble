# do not pre-load
from flask import request, jsonify
from flask_cors import cross_origin
from docassemble.webapp.extensions import csrf
from docassemble.webapp.app_object import flaskapp as app
from docassemble.webapp.api.helpers import api_verify
from docassemble.webapp.utils.helpers import jsonify_with_status
from docassemble.webapp.tasks.app import celery_app
from docassemble.base.config import in_celery
if not in_celery:
    from docassemble.demo.custombg import custom_add_four, custom_comma_and_list


@app.route('/api/start_process', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def start_process():
    if not api_verify():
        return jsonify_with_status({"success": False, "error_message": "Access denied."}, 403)
    try:
        operand = int(request.args['operand'])
    except:
        return jsonify_with_status({"success": False, "error_message": "Missing or invalid operand."}, 400)
    task = custom_add_four.delay(operand)  # pylint: disable=possibly-used-before-assignment
    return jsonify({"success": True, 'task_id': task.id})


@app.route('/api/poll_for_result', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def poll_for_result():
    if not api_verify():
        return jsonify_with_status({"success": False, "error_message": "Access denied."}, 403)
    try:
        result = celery_app.AsyncResult(id=request.args['task_id'])
    except:
        return jsonify_with_status({"success": False, "error_message": "Invalid task_id."}, 400)
    if not result.ready():
        return jsonify({"success": True, "ready": False})
    if result.failed():
        return jsonify({"success": False, "ready": True})
    return jsonify({"success": True, "ready": True, "answer": result.get()})


@app.route('/api/start_process_2', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def start_process_2():
    if not api_verify():
        return jsonify_with_status({"success": False, "error_message": "Access denied."}, 403)
    task = custom_comma_and_list.delay('foo', 'bar', 'foobar')  # pylint: disable=possibly-used-before-assignment
    return jsonify({"success": True, 'task_id': task.id})
