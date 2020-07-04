from typing import Optional

from flask import Blueprint, jsonify, request

from wiz.core import res_watch
from wiz.model.field.field import Field
from wiz.model.operations.operation import Operation
from wiz.model.prerequisite.prerequisite import Prerequisite
from wiz.model.stage.stage import Stage
from wiz.model.operations import serial as operation_serial
from wiz.model.step import serial as step_serial
from wiz.model.step.step import Step

OPERATIONS_PATH = '/api/operations'
OPERATION_PATH = f'/{OPERATIONS_PATH}/<operation_id>'

PREREQUISITES_PATH = f'/{OPERATION_PATH}/prerequisites'
PREREQUISITE_PATH = f'/{PREREQUISITES_PATH}/<prerequisite_id>'

STAGES_PATH = f'{OPERATION_PATH}/stages'
STAGE_PATH = f'{STAGES_PATH}/<stage_id>'

STEPS_PATH = f'{STAGE_PATH}/steps'
STEP_PATH = f'{STEPS_PATH}/<step_id>'

FIELDS_PATH = f'{STEP_PATH}/fields'
FIELD_PATH = f'{FIELDS_PATH}/<field_id>'

controller = Blueprint('operations_controller', __name__)


@controller.route(OPERATIONS_PATH)
def operations_index():
  operations_list = [o for o in Operation.inflate_all() if not o.is_system]
  dicts = [operation_serial.standard(c) for c in operations_list]
  return jsonify(data=dicts)


@controller.route(OPERATION_PATH)
def operations_show(operation_id):
  operation = find_operation(operation_id)
  return jsonify(data=operation_serial.full(operation))


@controller.route(f"{PREREQUISITE_PATH}/evaluate", methods=['POST'])
def prerequisite_eval(operation_id, prerequisite_id):
  prereq = find_prereq(operation_id, prerequisite_id)
  tone, message = prereq.decide()
  if tone and message:
    return jsonify(data=dict(status=tone, message=message))
  else:
    return jsonify(data=dict(status='valid'))


@controller.route(STEP_PATH)
def steps_show(operation_id, stage_id, step_id):
  step = find_step(operation_id, stage_id, step_id)
  serialized = step_serial.standard(step)
  return jsonify(data=serialized)


# noinspection PyUnusedLocal
@controller.route(f"{STEP_PATH}/resources")
def steps_show_resources(operation_id, stage_id, step_id):
  serialized_res_list = res_watch.glob([
    'ConfigMap',
    'Pod',
    'Deployment',
    'Secret'
  ])
  return jsonify(data=serialized_res_list)


@controller.route(f"{STEP_PATH}/submit", methods=['POST'])
def step_submit(operation_id, stage_id, step_id):
  values = request.json['values']
  step = find_step(operation_id, stage_id, step_id)
  osr.record_step_started()
  status, reason = step.commit(values)
  osr.record_step_terminated(step)
  return jsonify(status=status, message=reason)


@controller.route(f"{STEP_PATH}/stage", methods=['POST'])
def step_stage(operation_id, stage_id, step_id):
  values = request.json['values']
  step = find_step(operation_id, stage_id, step_id)
  assignments = step.stage(values)
  return jsonify(data=assignments)


@controller.route(f"{STEP_PATH}/status")
def step_status(operation_id, stage_id, step_id):
  step = find_step(operation_id, stage_id, step_id)
  return jsonify(status=step.status())


@controller.route(f'{STEP_PATH}/next', methods=['POST'])
def steps_next_id(operation_id, stage_id, step_id):
  values = request.json['values']
  stage = find_stage(operation_id, stage_id)
  step = find_step(operation_id, stage_id, step_id)
  next_step_id = stage.next_step_id(step, values)
  return jsonify(step_id=next_step_id)


@controller.route(f'{FIELD_PATH}/validate', methods=['POST'])
def fields_validate(operation_id, stage_id, step_id, field_id):
  field = find_field(operation_id, stage_id, step_id, field_id)
  value = request.json['value']
  tone, message = field.validate(value)
  if tone and message:
    return jsonify(data=dict(status=tone, message=message))
  else:
    return jsonify(data=dict(status='valid'))


@controller.route(f'{FIELD_PATH}/decorate', methods=['POST'])
def fields_decorate(operation_id, stage_id, step_id, field_id):
  field = find_field(operation_id, stage_id, step_id, field_id)
  value = request.json['value']
  return jsonify(data=field.decorate_value(value))


def find_operation(operation_id) -> Operation:
  return Operation.inflate(operation_id)


def find_prereq(operation_id, prereq_id) -> Prerequisite:
  operation = find_operation(operation_id)
  return operation.prerequisite(prereq_id)


def find_stage(operation_id, stage_id) -> Stage:
  operation = find_operation(operation_id)
  return operation.stage(stage_id)


def find_step(operation_id, stage_id, step_id) -> Step:
  stage = find_stage(operation_id, stage_id)
  return stage.step(step_id)


def find_field(operation_id, stage_id, step_id, field_id) -> Field:
  step = find_step(operation_id, stage_id, step_id)
  return step.field(field_id)


def find_osr():
  if request.headers.get('osr_id'):
    osr = Osr(request.headers.get('osr_id'))
