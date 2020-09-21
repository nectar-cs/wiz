from flask import Blueprint, jsonify, request

from nectwiz.controllers.ctrl_utils import jparse
from nectwiz.core.telem import telem_sync
from nectwiz.model.field.field import Field, TARGET_CHART
from nectwiz.model.operation import serial as operation_serial
from nectwiz.model.operation.operation import Operation
from nectwiz.model.operation.operation_state import OperationState, operation_states
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.stage.stage import Stage
from nectwiz.model.step import step_serial
from nectwiz.model.step.step import Step

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


@controller.route(f'{OPERATION_PATH}/request-ost')
def operations_gen_ost(operation_id):
  """
  Generates a new OST (random 10 character string).
  :return: new OST.
  """
  uuid = OperationState.gen(operation_id)
  return jsonify(data=uuid)


@controller.route(f'{OPERATIONS_PATH}/osts')
def operations_ost_index():
  """
  Generates a list of currently available OperationStates.
  :return: list of currently available OperationStates.
  """
  return jsonify(data=operation_states)


@controller.route(f"{PREREQUISITE_PATH}/evaluate", methods=['POST'])
def prerequisite_eval(operation_id, prerequisite_id):
  """
  Finds the Prerequisite with a matching operation_id and prerequisite_id,
  and evaluates it.
  :param operation_id: operation id to search by.
  :param prerequisite_id: prerequisite id to search by.
  :return: dict containing results of evaluation.
  """
  prereq = find_prereq(operation_id, prerequisite_id)
  # noinspection PyBroadException
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
  """
  Finds the Step with a matching operation_id, stage_id and step_id.
  :param operation_id: operation id to search by.
  :param stage_id: stage id to search by.
  :param step_id: step id to search by.
  :return: serialized Step object.
  """
  step = find_step(operation_id, stage_id, step_id)
  serialized = step_serial.standard(step)
  return jsonify(data=serialized)


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


@controller.route(f"{STEP_PATH}/compute-settling-status")
def step_compute_settle_status(operation_id, stage_id, step_id):
  step = find_step(operation_id, stage_id, step_id)
  prev_state = find_op_state().find_step_state(step)
  step.compute_status(prev_state)
  return jsonify(
    status=prev_state.status,
    condition_statuses=prev_state.exit_statuses
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
  step = find_step(operation_id, stage_id, step_id)
  step_state = find_op_state().gen_step_state(step)
  return jsonify(step_id=step.next_step_id(step_state))


@controller.route(f'{FIELD_PATH}/validate', methods=['POST'])
def fields_validate(operation_id, stage_id, step_id, field_id):
  step = find_step(operation_id, stage_id, step_id)
  step_state = find_op_state()
  value = jparse()['value']
  tone, message = field.validate(value)
  if tone and message:
    return jsonify(data=dict(status=tone, message=message))
  else:
    return jsonify(data=dict(status='valid'))


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


def find_prereq(operation_id, prereq_id) -> Predicate:
  """
  Finds the Prerequisite with a matching operation_id and prereq_id.
  :param operation_id: operation id to search by.
  :param prereq_id: prerequisite id to search by.
  :return: Predicate class instance.
  """
  operation = find_operation(operation_id)
  return operation.prerequisite(prereq_id)


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
