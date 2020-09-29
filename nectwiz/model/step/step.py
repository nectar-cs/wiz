from typing import List, Dict, Optional

from nectwiz.core.core import job_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.job_client import enqueue_action, find_job
from nectwiz.core.core.types import CommitOutcome, PredEval
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.field.field import Field, TARGET_CHART, TARGET_STATE, TARGET_INLIN
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.step import step_exprs
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

  def sig(self) -> str:
    parent_id = self.parent.id() if self.parent else 'orphan'
    return f"{parent_id}::{self.id()}"

  def runs_action(self) -> bool:
    return self.action_kod is not None

  def next_step_id(self, op_state: OperationState) -> str:
    root = self.next_step_desc
    context = resolution_context(op_state)
    return step_exprs.eval_next_expr(root, context)

  def has_explicit_next(self) -> bool:
    expr = step_exprs.none_if_default(self.next_step_desc)
    return expr is not None

  def validate_field(self, field_id: str, value: str, op_state: TOS) -> PredEval:
    context = resolution_context(op_state)
    return self.field(field_id).validate(value, context)

  def fields(self) -> List[Field]:
    return self.load_children('fields', Field)

  def field(self, _id) -> Field:
    finder = lambda field: field.id() == _id
    return next(filter(finder, self.fields()), None)

  def visible_fields(self, user_values, op_state: TOS) -> List[Field]:
    context = dict(**(user_values or {}), **resolution_context(op_state))
    result = [f for f in self.fields() if f.compute_visibility(context)]
    return result

  def state_recall_descriptors(self, target: str):
    predicate = lambda d: d.get('to', TARGET_CHART) == target
    return filter(predicate, self.reassignment_descs)

  def comp_recalled_asgs(self, target: str, prev_state: TSS) -> Dict:
    state_assigns = prev_state.parent_op.all_assigns()
    new_assigns = {}

    for desc in self.state_recall_descriptors(target):
      _id, value = desc['id'], desc.get('value', state_assigns.get(desc))
      new_assigns[_id] = value

    return new_assigns

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
    mfst_vars, state_vars = buckets[TARGET_CHART], buckets[TARGET_STATE]
    prev_state.notify_vars_assigned(mfst_vars, state_vars)

    if len(mfst_vars):
      keyed_tuples = list(mfst_vars.items())
      config_man.commit_keyed_mfst_vars(keyed_tuples)

    if self.runs_action():
      job_id = enqueue_action(self.action_kod, **buckets)
      prev_state.notify_action_started(job_id)
    else:
      prev_state.notify_succeeded()

  # noinspection PyMethodMayBeStatic
  def compute_status(self, prev_state: TSS = None) -> Dict:
    if prev_state.is_running():
      action_job = find_job(prev_state.job_id)
      if action_job:
        status = job_client.ternary_job_status(prev_state.job_id)
        progress = job_client.job_progress(prev_state.job_id)
        if action_job.is_finished:
          prev_state.notify_succeeded()
        elif action_job.is_failed:
          prev_state.notify_failed()
        return dict(status=status, progress=progress)
      else:
        print(f"[nectwiz::step] DANGER job {prev_state.job_id} lost!")
        return dict(status='negative', progress={})
    else:
      print(f"[nectwiz::step] DANGER compute_status called when not running")
      prev_state.notify_succeeded()
      return dict(status='positive', progress={})

  def partition_user_asgs(self, assigns: Dict, ps: TSS) -> Dict:
    fields = self.visible_fields(assigns, ps.parent_op)

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


def resolution_context(op_state: OperationState):
  return dict(
    resolvers=dict(
      operation=lambda n: op_state.all_assigns().get(n)
    )
  )
