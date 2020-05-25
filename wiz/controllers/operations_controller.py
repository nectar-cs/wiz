from flask import Blueprint, jsonify, request

from wiz.core import res_watch
from wiz.model.field.field import Field
from wiz.model.operations.install_stage import InstallStage
from wiz.model.step import serial as step_serial
from wiz.model.operations.operation import Operation
from wiz.model.step.step import Step

OPERATIONS_PATH = '/api/operations'
OPERATION_PATH = f'/{OPERATIONS_PATH}/<op_id>'
STEPS_PATH = f'{OPERATION_PATH}/steps'
STEP_PATH = f'{STEPS_PATH}/<step_id>'
FIELD_PATH = f'{STEP_PATH}/fields/<field_id>'

controller = Blueprint('operations_controller', __name__)


@controller.route(STEP_PATH)
def steps_show(op_id, step_id):
  step = find_step(op_id, step_id)
  serialized = step_serial.standard(step)
  return jsonify(data=serialized)


@controller.route(f"{STEP_PATH}/res")
def watch_step_res(op_id, step_id):
  serialized_res_list = res_watch.glob([
    'ConfigMap',
    'Pod',
    'Deployment',
    'Secret'
  ])
  return jsonify(data=serialized_res_list)


@controller.route(f"{STEP_PATH}/submit", methods=['POST'])
def step_submit(op_id, step_id):
  values = request.json['values']
  step = find_step(op_id, step_id)
  status, reason = step.commit(values)
  return jsonify(status=status, message=reason)


@controller.route(f"{STEP_PATH}/status")
def step_status(op_id, step_id):
  step = find_step(op_id, step_id)
  return jsonify(status=step.status())


@controller.route(f'{STEP_PATH}/next', methods=['POST'])
def steps_next_id(op_id, step_id):
  values = request.json['values']
  step = find_step(op_id, step_id)
  next_step_id = step.next_step_id(values)
  return jsonify(step_id=next_step_id)


@controller.route(f'{FIELD_PATH}/validate', methods=['POST'])
def fields_validate(op_id, step_id, field_id):
  field = find_field(op_id, step_id, field_id)
  value = request.json['value']
  tone, message = field.validate(value)
  if tone and message:
    return jsonify(data=dict(status=tone, message=message))
  else:
    return jsonify(data=dict(status='valid'))


def find_operation(key) -> Operation:
  return Operation.inflate(key) or \
         InstallStage.inflate(key)


def find_step(op_id, step_key) -> Step:
  operation = find_operation(op_id)
  return operation.step(step_key)


def find_field(op_id, step_key, field_id) -> Field:
  step = find_step(op_id, step_key)
  return step.field(field_id)
