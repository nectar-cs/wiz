from flask import Blueprint, jsonify


controller = Blueprint('setup_controller', __name__)

@controller.route('/api/concerns')
def concerns():
  from wiz.server import model_class
  meta_objects = [concern.meta() for concern in model_class().concerns()]
  return jsonify(data=meta_objects)

@controller.route('/api/concerns/<concern_id>/steps/<step_id>')
def step(concern_id, step_id):
  from wiz.server import model_class
  wizard = model_class()
  concern = model_class().concern(concern_id)


def concern_step(concern, step_id):
  if step_id == 'first':
    return None
  else:
    return None
