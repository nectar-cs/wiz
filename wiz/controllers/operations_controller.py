from flask import Blueprint, jsonify, request

from wiz.core import utils
from wiz.core.telem import telem_sync
from wiz.core.telem.ost import OperationState, operation_states
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


@controller.route(f'{OPERATIONS_PATH}/request-ost')
def operations_gen_ost():
  """
  Generates a new OST (random 10 character string).
  :return: new OST.
  """
  return jsonify(data=utils.rand_str(string_len=10))


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


@controller.route(f"{STEP_PATH}/submit", methods=['POST'])
def step_submit(operation_id, stage_id, step_id):
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
  values = request.json['values']
  op_state = find_op_state(operation_id)
  step = find_step(operation_id, stage_id, step_id)
  op_state.record_step_started(stage_id, step_id)
  outcome: CommitOutcome = step.commit(values, op_state)
  op_state.record_step_committed(stage_id, step_id, outcome)
  return jsonify(
    status=outcome['status'],
    message=outcome.get('reason'),
    logs=outcome.get('logs')
  )


@controller.route(f"{STEP_PATH}/preview-chart-assignments", methods=['POST'])
def step_stage(operation_id, stage_id, step_id):
  """
  Returns the chart assignments that would be committed if the step were submitted
  with current user input.
  :param operation_id: operation id used to locate the right step
  :param stage_id: stage id used to locate the right step
  :param step_id: step id used to locate the right step
  :return: dictionary with chart assigns.
  """
  values = request.json['values']
  step = find_step(operation_id, stage_id, step_id)
  op_state = find_op_state(operation_id)
  chart_assigns, _, _ = step.partition_value_assigns(values, op_state)
  return jsonify(data=chart_assigns)


@controller.route(f"{STEP_PATH}/status")
def step_status(operation_id, stage_id, step_id):
  """
  Computes a step's status based on evaluation of exit conditions and status of
  any related jobs.
  :param operation_id: operation id to find the right step.
  :param stage_id: stage id to find the right step.
  :param step_id: step id to find the right step.
  :return: dict of the following form:
   StepRunningStatus(
    status=status,
    condition_statuses=ExitConditionStatuses(
      positive=pos,
      negative=neg
    ),
    job_status=JobStatus(
      parts=[
        JobStatusPart(
          name=raw.get('name', f'Job Part {index + 1}'),
          status=raw.get('status', 'Working'),
          pct = int(raw.get('pct')) if raw.get('pct') else None
        )
      ],
      logs=logs
    )
  """
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
  """
  computes and returns the id of the next step.
  :param operation_id: operation id to locate the right step.
  :param stage_id: stage id to locate the right step.
  :param step_id: step id to locate the right step.
  :return: computed id of next step or "done" if no more steps left.
  """
  values = request.json['values']
  stage = find_stage(operation_id, stage_id)
  step = find_step(operation_id, stage_id, step_id)
  next_step_id = stage.next_step_id(step, values)
  return jsonify(step_id=next_step_id)


@controller.route(f'{FIELD_PATH}/validate', methods=['POST'])
def fields_validate(operation_id, stage_id, step_id, field_id):
  """
  Validates the given field against all associated Validators.
  :param operation_id: operation id to locate the right field.
  :param stage_id: stage id to locate the right field.
  :param step_id: step id to locate the right field.
  :param field_id: field id to locate the right field.
  :return: dict with tone and status if at least one Validator is unsuccessful,
  dict with "valid" otherwise.
  """
  field = find_field(operation_id, stage_id, step_id, field_id)
  value = request.json['value']
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
  value = request.json['value']
  return jsonify(data=field.decorate_value(value))


@controller.route(f'{OPERATIONS_PATH}/mark-finished', methods=['POST'])
def mark_finished():
  """
  Syncs telemetry information with the database if permissions allow to do so.
  Deletes OperationState after its done.
  :return: success or failure status depending if managed to find and delete
  the appropriate operation.
  """
  token = parse_ost_header()
  _status = OperationState.mark_status_if_exists(token, 'positive')
  return jsonify(data=dict(success=_status))


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


def parse_ost_header() -> str:
  """
  Extracts osr id from the passed header.
  :return: osr id.
  """
  return request.headers.get('Ostid')


def find_op_state(operation_id: str) -> OperationState:
  """
  If osr id supplied, finds/creates the appropriate OperationState. Else creates
  an OperationState without an osr id.
  :param operation_id: id of the operation for which the OperationState is being
  located / created.
  :return: OperationState.
  """
  if parse_ost_header():
    return OperationState.find_or_create(
      parse_ost_header(),
      operation_id
    )
  else:
    return OperationState(operation_id=operation_id)
