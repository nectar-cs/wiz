import json

from flask import Blueprint, jsonify, request

from wiz.model.wizard import Wizard

CONCERNS_PATH = '/api/concerns'
STEPS_PATH = f'{CONCERNS_PATH}/<concern_id>/steps'
PARTS_PATH = f'{STEPS_PATH}/<step_id>/parts'

controller = Blueprint('setup_controller', __name__)


@controller.route(CONCERNS_PATH)
def concerns():
  meta_objects = [concern.meta() for concern in model_class().concerns()]
  return jsonify(data=meta_objects)

@controller.route(f'{STEPS_PATH}/<step_id>')
def step(concern_id, step_id):
  concern = model_class().concern(concern_id)

@controller.route(f'{PARTS_PATH}/<part_id>')
def validate_part(concern_id, step_id, part_id):
  pass

def concern_step(concern, step_id):
  step_id = None if step_id == 'first' else step_id
  state = inflate_step_state()


def inflate_step_state():
  raw_state = request.headers.get('step_state')
  return json.loads(raw_state)

def model_class() -> Wizard:
  from wiz.server import app
  return app.config['model_class']
