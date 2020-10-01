from typing import Dict

from flask import Blueprint, jsonify, request

from nectwiz.controllers.ctrl_utils import jparse
from nectwiz.core.core import job_client
from nectwiz.core.telem import telem_sync
from nectwiz.model.field import field
from nectwiz.model.field.field import Field, TARGET_CHART
from nectwiz.serializers import operation_serial as operation_serial, step_serial
from nectwiz.model.operation.operation import Operation
from nectwiz.model.operation.operation_state import OperationState, operation_states
from nectwiz.model.operation.stage import Stage
from nectwiz.model.operation.step import Step

OPERATIONS_PATH = '/api/operations'
OPERATION_PATH = f'/{OPERATIONS_PATH}/<operation_id>'

STAGES_PATH = f'{OPERATION_PATH}/stages'
STAGE_PATH = f'{STAGES_PATH}/<stage_id>'

STEPS_PATH = f'{STAGE_PATH}/steps'
STEP_PATH = f'{STEPS_PATH}/<step_id>'

FIELDS_PATH = f'{STEP_PATH}/fields'
FIELD_PATH = f'{FIELDS_PATH}/<field_id>'

controller = Blueprint('operations_controller', __name__)


@controller.route(OPERATIONS_PATH)
def operations_index():
  """
  Lists all existing Operations for a local app, except system ones.
  :return: list of minimally serialized Operation objects.
  """
  operations_list = [o for o in Operation.inflate_all() if not o.is_system]
  dicts = [operation_serial.ser_standard(c) for c in operations_list]
  return jsonify(data=dicts)


@controller.route(OPERATION_PATH)
def operations_show(operation_id):
  """
  Finds and returns a particular Operation using operation_id.
  :param operation_id: operation id to search by.
  :return: fully serialized Operation object.
  """
  operation = find_operation(operation_id)
  return jsonify(data=operation_serial.ser_full(operation))


@controller.route(f'{OPERATIONS_PATH}/osts')
def operations_ost_index():
  """
  Generates a list of currently available OperationStates.
  :return: list of currently available OperationStates.
  """
  return jsonify(data=operation_states)


@controller.route(f'{OPERATION_PATH}/generate-ost', methods=['POST'])
def operations_gen_ost(operation_id):
  """
  Generates a new OST (random 10 character string).
  :return: new OST.
  """
  uuid = OperationState.gen(operation_id)
  return jsonify(data=uuid)


@controller.route(f"{OPERATION_PATH}/eval-preflight", methods=['POST'])
def eval_preflight(operation_id):
  """
  Finds the Prerequisite with a matching operation_id and prerequisite_id,
  and evaluates it.
  :param operation_id: operation id to search by.
  :return: dict containing results of evaluation.
  """
  operation = find_operation(operation_id)
  preflight_action = operation.preflight_action_config()
  job_id = job_client.enqueue_action(preflight_action)
  return jsonify(data=dict(job_id=job_id))


@controller.route(f"{STEP_PATH}/refresh", methods=['POST'])
def step_refresh(operation_id, stage_id, step_id):
  """
  Finds the Step with a matching operation_id, stage_id and step_id.
  :param operation_id: operation id to search by.
  :param stage_id: stage id to search by.
  :param step_id: step id to search by.
  :return: serialized Step object.
  """
  values: Dict = jparse()['values']
  op_state = find_op_state()
  step = find_step(operation_id, stage_id, step_id)
  synth_step_state = find_op_state().gen_step_state(step, keep=False)
  asgs = step.partition_user_asgs(values, synth_step_state)
  serialized = step_serial.ser_refreshed(step, values, op_state)
  return jsonify(data=dict(
    step=serialized,
    assignments=asgs.get(field.TARGET_CHART)
  ))


@controller.route(f"{STEP_PATH}/preview-chart-assignments", methods=['POST'])
def step_preview_chart_assigns(operation_id, stage_id, step_id):
  """
  Returns the chart assignments that would be committed if the step were submitted
  with current user input.
  :param operation_id: operation id used to locate the right step
  :param stage_id: stage id used to locate the right step
  :param step_id: step id used to locate the right step
  :return: dictionary with chart assigns.
  """
  values = jparse()['values']
  step = find_step(operation_id, stage_id, step_id)
  synth_step_state = find_op_state().gen_step_state(step, keep=False)
  asgs = step.partition_user_asgs(values, synth_step_state)
  return jsonify(data=asgs[TARGET_CHART])


@controller.route(f"{STEP_PATH}/run", methods=['POST'])
def step_run(operation_id, stage_id, step_id):
  """
  Submits a step. This includes:
    1. Finding the appropriate OperationState
    2. Appending a new StepState to OperationState
    3. Committing the step (See docs for step commit)
    4. Updating the StepState with the details of the commit outcome
  :param operation_id: operation id to search by.
  :param stage_id: stage id to search by.
  :param step_id: step id to search by.
  :return: dict containing submit status, message and logs.
  """
  values = jparse()['values']
  step = find_step(operation_id, stage_id, step_id)
  step_state = find_op_state().gen_step_state(step)
  step.run(values, step_state)
  return jsonify(status=step_state.status)


@controller.route(f"{STEP_PATH}/status")
def step_compute_settle_status(operation_id, stage_id, step_id):
  step = find_step(operation_id, stage_id, step_id)
  prev_state = find_op_state().find_step_state(step)
  status = step.compute_status(prev_state)
  return jsonify(
    status=status.get('status'),
    progress=status.get('progress')
  )


@controller.route(f'{STEP_PATH}/next')
def steps_next_id(operation_id, stage_id, step_id):
  """
  computes and returns the id of the next step.
  :param operation_id: operation id to locate the right step.
  :param stage_id: stage id to locate the right step.
  :param step_id: step id to locate the right step.
  :return: computed id of next step or "done" if no more steps left.
  """
  stage = find_stage(operation_id, stage_id)
  step = find_step(operation_id, stage_id, step_id)
  op_state = find_op_state()
  result = stage.next_step_id(step, op_state)
  return jsonify(step_id=result)


@controller.route(f'{FIELD_PATH}/validate', methods=['POST'])
def step_field_validate(operation_id, stage_id, step_id, field_id):
  value = jparse()['value']
  step = find_step(operation_id, stage_id, step_id)
  op_state = find_op_state()
  eval_result = step.validate_field(field_id, value, op_state)
  status = 'valid' if eval_result['met'] else eval_result['tone']
  message = None if eval_result['met'] else eval_result['reason']
  return jsonify(data=dict(status=status, message=message))


@controller.route(f'{FIELD_PATH}/decorate', methods=['POST'])
def fields_decorate(operation_id, stage_id, step_id, field_id):
  """
  Decorates the field wit the passed values. Decorating refers to displaying
  values next to the field in question.
  :param operation_id: operation id to locate the right field.
  :param stage_id: stage id to locate the right field.
  :param step_id: step id to locate the right field.
  :param field_id: field id to locate the right field.
  :return: dict with decorations.
  """
  field = find_field(operation_id, stage_id, step_id, field_id)
  value = jparse()['value']
  return jsonify(data=field.decorate_value(value))


@controller.route(f'{OPERATIONS_PATH}/mark-finished', methods=['POST'])
def mark_finished():
  """
  Syncs telemetry information with the database if permissions allow to do so.
  Deletes OperationState after its done.
  :return: success or failure status depending if managed to find and delete
  the appropriate operation.
  """
  find_op_state().notify_succeeded()
  return jsonify(data=dict(success='yeah'))


@controller.route(f'{OPERATIONS_PATH}/flush-telem', methods=['POST'])
def flush_telem():
  telem_sync.upload_operation_outcomes()
  return jsonify(status='success')


def find_operation(operation_id: str) -> Operation:
  """
  Inflates (instantiates) an instance of an Operation by operation_id.
  :param operation_id: desired operation to be inflated.
  :return: Operation instance.
  """
  return Operation.inflate(operation_id)


def find_stage(operation_id, stage_id) -> Stage:
  """
  Finds the Stage with a matching operation_id and stage_id.
  :param operation_id: operation id to search by.
  :param stage_id: stage id to search by.
  :return: Stage class instance.
  """
  operation = find_operation(operation_id)
  return operation.stage(stage_id)


def find_step(operation_id, stage_id, step_id) -> Step:
  """
  Finds the Step with a matching operation_id, stage_id and step_id.
  :param operation_id: operation id to search by.
  :param stage_id: stage id to search by.
  :param step_id: step id to search by.
  :return: Step class instance.
  """
  stage = find_stage(operation_id, stage_id)
  return stage.step(step_id)


def find_field(operation_id, stage_id, step_id, field_id) -> Field:
  """
  Finds the Field with a matching operation_id, stage_id, step_id and field_id.
  :param operation_id: operation id to search by.
  :param stage_id: stage id to search by.
  :param step_id: step id to search by.
  :param field_id: field id to search by.
  :return: Field class instance.
  """
  step = find_step(operation_id, stage_id, step_id)
  return step.field(field_id)


def find_op_state() -> OperationState:
  token = request.headers.get('Ostid')
  if not token:
    raise RuntimeError('OST ID not provided in headers!')
  return OperationState.find(token)
