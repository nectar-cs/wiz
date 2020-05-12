import base64
import json
from flask import Blueprint, jsonify, request

from wiz.core import res_watch
from wiz.model.concern import serial as concern_serial
from wiz.model.field.field import Field
from wiz.model.step import serial as step_serial
from wiz.model.concern.concern import Concern
from wiz.model.step.step import Step

CONCERNS_PATH = '/api/concerns'
CONCERN_PATH = f'/{CONCERNS_PATH}/<concern_id>'
STEPS_PATH = f'{CONCERN_PATH}/steps'
STEP_PATH = f'{STEPS_PATH}/<step_id>'
FIELD_PATH = f'{STEP_PATH}/fields/<field_id>'

controller = Blueprint('setup_controller', __name__)


@controller.route(CONCERNS_PATH)
def concerns_index():
  concerns = Concern.inflate_all()
  dicts = [concern_serial.standard(c) for c in concerns]
  return jsonify(data=dicts)


@controller.route(STEP_PATH)
def steps_show(concern_id, step_id):
  step = find_step(concern_id, step_id)
  serialized = step_serial.standard(step)
  return jsonify(data=serialized)


@controller.route(f"{STEP_PATH}/res")
def watch_step_res(concern_id, step_id):
  step = find_step(concern_id, step_id)
  # kinds = step.watch_res_kinds
  serialized_res_list = res_watch.glob(['ConfigMap', 'Pod', 'Deployment', 'Secret'])
  return jsonify(data=serialized_res_list)


@controller.route(f"{STEP_PATH}/submit", methods=['POST'])
def step_submit(concern_id, step_id):
  values = request.json['values']
  step = find_step(concern_id, step_id)
  status, reason = step.commit(values)
  return jsonify(status=status, message=reason)


@controller.route(f"{STEP_PATH}/status")
def step_status(concern_id, step_id):
  step = find_step(concern_id, step_id)
  return jsonify(status=step.status())


@controller.route(f'{STEP_PATH}/next', methods=['POST'])
def steps_next_id(concern_id, step_id):
  values = request.json['values']
  step = find_step(concern_id, step_id)
  next_step_id = step.next_step_id(values)
  return jsonify(step_id=next_step_id)


@controller.route(f'{FIELD_PATH}/validate', methods=['POST'])
def fields_validate(concern_id, step_id, field_id):
  field = find_field(concern_id, step_id, field_id)
  value = request.json['value']
  tone, message = field.validate(value)
  if tone and message:
    return jsonify(data=dict(status=tone, message=message))
  else:
    return jsonify(data=dict(status='valid'))


@controller.route('/api/concerns-echo-state')
def echo_state():
  inflated_state = inflate_step_state()
  if inflated_state:
    return jsonify(pong=inflated_state)
  else:
    return dict("Decode Failed")


def find_concern(key) -> Concern:
  return Concern.inflate(key)


def find_step(concern_key, step_key) -> Step:
  concern = find_concern(concern_key)
  return concern.step(step_key)


def find_field(concern_key, step_key, field_id) -> Field:
  step = find_step(concern_key, step_key)
  return step.field(field_id)


def inflate_step_state():
  try:
    base64_message = request.headers.get('step_state')
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return json.loads(message)
  except:
    return dict()
