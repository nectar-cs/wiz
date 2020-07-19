from flask import Blueprint, jsonify, request

from wiz.core.telem import telem_sync
from wiz.core.telem.audit_sink import AuditConfig, audit_sink
from wiz.core.telem.ost import OperationState
from wiz.core.telem.telem_perms import TelemPerms
from wiz.model.field.field import Field
from wiz.model.operations.operation import Operation
from wiz.model.predicate.predicate import Predicate
from wiz.model.stage.stage import Stage
from wiz.model.operations import serial as operation_serial
from wiz.model.step import serial as step_serial
from wiz.model.step.step import Step, CommitOutcome


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
  dicts = [operation_serial.ser_standard(c) for c in operations_list]
  return jsonify(data=dicts)


@controller.route(OPERATION_PATH)
def operations_show(operation_id):
  operation = find_operation(operation_id)
  return jsonify(data=operation_serial.ser_full(operation))


@controller.route(f"{PREREQUISITE_PATH}/evaluate", methods=['POST'])
def prerequisite_eval(operation_id, prerequisite_id):
  prereq = find_prereq(operation_id, prerequisite_id)
  try:
    condition_met = prereq.evaluate()
  except:
    condition_met = None
  return jsonify(data=dict(
    condition_met=condition_met,
    tone=prereq.tone,
    reason=prereq.reason
  ))


@controller.route(STEP_PATH)
def steps_show(operation_id, stage_id, step_id):
  step = find_step(operation_id, stage_id, step_id)
  serialized = step_serial.standard(step)
  return jsonify(data=serialized)


@controller.route(f"{STEP_PATH}/submit", methods=['POST'])
def step_submit(operation_id, stage_id, step_id):
  values = request.json['values']
  op_state = find_op_state(operation_id)
  step = find_step(operation_id, stage_id, step_id)
  outcome: CommitOutcome = step.commit(values, op_state)
  op_state.record_step_committed(step_id, stage_id, outcome)
  return jsonify(
    status=outcome['status'],
    message=outcome.get('reason'),
    logs=outcome.get('logs')
  )


@controller.route(f"{STEP_PATH}/preview-chart-assignments", methods=['POST'])
def step_stage(operation_id, stage_id, step_id):
  values = request.json['values']
  step = find_step(operation_id, stage_id, step_id)
  op_state = find_op_state(operation_id)
  chart_assigns, _, _ = step.partition_value_assigns(values, op_state)
  return jsonify(data=chart_assigns)


@controller.route(f"{STEP_PATH}/status")
def step_status(operation_id, stage_id, step_id):
  step = find_step(operation_id, stage_id, step_id)
  op_state = find_op_state(operation_id)
  status_bundle = step.compute_status(op_state)
  status_word = status_bundle['status']
  if op_state.is_tracked():
    if status_word == 'pending':
      op_state.record_step_pending(stage_id, step_id, status_bundle)
    else:
      op_state.record_step_terminated(stage_id, step_id, status_bundle)
  return jsonify(data=status_bundle)


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


@controller.route(f'{OPERATION_PATH}/mark_finished', methods=['POST'])
def mark_finished(operation_id):
  token, sync_status = osr_token(), 'avoid'
  active_op_state = OperationState.find(token) if token else None

  if active_op_state and active_op_state.operation_id == operation_id:
    telem_perms, audit_config = TelemPerms(), AuditConfig()

    if telem_perms.can_sync_telem():
      success = telem_sync.upload_operation_outcome(active_op_state)
      sync_status = 'success' if success else 'mem-failed'

    if audit_config.is_persistence_enabled():
      audit_sink.save_op_outcome(active_op_state, sync_status)

    OperationState.delete_if_exists(active_op_state.osr_id)
    return jsonify(data=dict(status='success'))
  else:
    return jsonify(data=dict(status='failure')), 400


def find_operation(operation_id) -> Operation:
  return Operation.inflate(operation_id)


def find_prereq(operation_id, prereq_id) -> Predicate:
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


def osr_token():
  return request.headers.get('ost_id')


def find_op_state(operation_id: str) -> OperationState:
  if osr_token():
    return OperationState.find_or_create(osr_token(), operation_id)
  else:
    return OperationState(operation_id=operation_id)
