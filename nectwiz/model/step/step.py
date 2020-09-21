from typing import List, Dict, Optional

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import CommitOutcome
from nectwiz.core.job.job_client import enqueue_action, find_job
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.field.field import Field, TARGET_CHART, TARGET_STATE, TARGET_INLIN
from nectwiz.model.operations.operation_state import OperationState
from nectwiz.model.predicate import default_predicates
from nectwiz.model.step import step_exprs, status_computer
from nectwiz.model.step.step_state import StepState


TOS = OperationState
TSS = StepState
TOOS = Optional[OperationState]
TCO = CommitOutcome


class Step(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.field_keys = config.get('fields', [])
    self.next_step_desc = self.config.get('next')
    self.reassignment_descs = config.get('reassignments', [])
    self.exit_predicate_descs = self.config.get('exit', {})
    self.expl_applies_manifest = config.get('applies_manifest')
    self.action_kod = config.get('action')

  def sig(self):
    parent_id = self.parent.id() if self.parent else 'orphan'
    return f"{parent_id}::{self.id()}"

  def runs_action(self) -> bool:
    return self.action_kod is not None

  def next_step_id(self, step_state: StepState) -> str:
    root = self.next_step_desc
    context = resolution_context(step_state)
    return step_exprs.eval_next_expr(root, context)

  def has_explicit_next(self) -> bool:
    return step_exprs.none_if_default(self.next_step_desc) is None

  def validate_field(self, field_id, value, step_state):
    context = resolution_context(step_state)
    return self.field(field_id).validate(value, context)

  def fields(self) -> List[Field]:
    return self.load_children('fields', Field)

  def field(self, _id) -> Field:
    finder = lambda field: field.id() == _id
    return next(filter(finder, self.fields()), None)

  def fields2(self) -> List[Field]:
    descs = self.config.get('fields')
    return list(map(Field.from_expr, descs))

  def state_recall_descriptors2(self, target):
    predicate = lambda d: d.get('target', TARGET_CHART) == target
    return filter(predicate, self.reassignment_descs)

  def comp_recalled_asgs(self, target: str, prev_state: TSS) -> dict:
    descriptors = self.state_recall_descriptors2(target)
    state_assigns = prev_state.parent_op.all_assigns()
    recalled_keys = utils.flatten(d['ids'] for d in descriptors)
    return {key: state_assigns.get(key) for key in recalled_keys}

  # noinspection PyUnusedLocal
  def finalize_chart_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_CHART, prev_state)
    return {**recalled_from_state, **assigns}

  # noinspection PyUnusedLocal
  def finalize_inline_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_INLIN, prev_state)
    return {**recalled_from_state, **assigns}

  # noinspection PyUnusedLocal
  def finalize_state_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_STATE, prev_state)
    return {**recalled_from_state, **assigns}

  def run(self, assigns: Dict, prev_state: StepState):
    buckets = self.partition_user_asgs(assigns, prev_state)

    if len(buckets[TARGET_CHART]):
      keyed_tuples = list(buckets[TARGET_CHART].items())
      config_man.commit_keyed_mfst_vars(keyed_tuples)

    if self.runs_action():
      job_id = enqueue_action(self.action_kod, **buckets)
      prev_state.notify_action_started(job_id)
    else:
      prev_state.notify_succeeded()

    prev_state.notify_vars_assigned(
      buckets[TARGET_CHART],
      buckets[TARGET_STATE]
    )

  def compute_status(self, prev_state: TSS = None) -> bool:
    if prev_state.was_running():
      action_job = find_job(prev_state.job_id)
      if action_job.is_finished:
        outcome = action_job.result
        print("[nectwiz::step::run] OUTCOME")
        print(outcome)
        prev_state.notify_is_settling(outcome)
        return self.compute_settling_status(prev_state)
      elif action_job.is_failed:
        print("Oh crap job failed!")
        return True
      else:
        print("Job still going...")
        return False
    elif prev_state.is_awaiting_settlement():
      return self.compute_settling_status(prev_state)

  def compute_settling_status(self, step_state: StepState):
    exit_predicates = self.exit_predicates(step_state)
    status_computer.compute(exit_predicates, step_state)
    return step_state.has_settled()

  def exit_predicates(self, step_state: StepState):
    if self.exit_predicate_descs:
      return self.exit_predicate_descs
    elif step_state.action_was("StepApplyResAction"):
      logs = step_state.action_outcome['data'].get('logs', [])
      return default_predicates.from_apply_outcome(logs)
    else:
      print("DANGER I SHOULD HAVE PREDS BUT DONT")
      print(self.exit_predicate_descs)
      print(step_state.action_outcome)
      return {}

  def partition_user_asgs(self, assigns: Dict, ps: TSS) -> Dict:
    fields = self.fields()

    def find_field(_id):
      return next(filter(lambda f: f.id() == _id, fields), None)

    def seg(_type: str):
      transv = lambda k, v: find_field(k) and find_field(k).sanitize_value(v)
      gate = lambda k: find_field(k) and find_field(k).target == _type
      return {k: transv(k, v) for (k, v) in assigns.items() if gate(k)}

    return {
        TARGET_CHART: self.finalize_chart_asgs(seg(TARGET_CHART), ps),
        TARGET_INLIN: self.finalize_inline_asgs(seg(TARGET_INLIN), ps),
        TARGET_STATE: self.finalize_state_asgs(seg(TARGET_STATE), ps),
      }


def resolution_context(step_state: StepState):
  return dict(
    resolvers=dict(
      step=lambda n: step_state.all_assigns().get(n),
      operation=lambda n: step_state.parent_op.all_assigns().get(n)
    )
  )
