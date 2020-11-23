from typing import List, Dict, Optional

from nectwiz.model.error.errors_man import errors_man

from nectwiz.core.core import job_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.job_client import enqueue_action
from nectwiz.core.core.types import CommitOutcome, PredEval
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.field.field import Field, TARGET_CHART, \
  TARGET_STATE, TARGET_INLIN, TARGET_PREFS
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.operation.step_state import StepState

TOS = OperationState
TSS = StepState
TOOS = Optional[OperationState]
TCO = CommitOutcome


class Step(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.field_keys = config.get('fields', [])
    self.next_step_kod = self.config.get('next')
    self.reassignment_descs = config.get('reassignments', [])
    self.exit_predicate_descs = self.config.get('exit', {})
    self.expl_applies_manifest = config.get('applies_manifest')
    self.action_kod = config.get('action')

  def sig(self) -> str:
    parent_id = self.parent.id() if self.parent else 'orphan'
    return f"{parent_id}::{self.id()}"

  def runs_action(self) -> bool:
    return self.action_kod

  def next_step_id(self, op_state: TOS) -> Optional[str]:
    return self.get_prop(
      'next',
      None,
      resolution_context(op_state)
    )

  def has_explicit_next(self) -> bool:
    if self.next_step_kod:
      return not self.next_step_kod == 'default'
    return False

  def validate_field(self, field_id: str, value: str, op_state: TOS) -> PredEval:
    context = resolution_context(op_state)
    return self.field(field_id).validate(value, context)

  def fields(self) -> List[Field]:
    return self.inflate_children('fields', Field)

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
      _id = desc['id']
      value = desc.get('value', state_assigns.get(_id))
      new_assigns[_id] = value

    return new_assigns

  def finalize_chart_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_CHART, prev_state)
    return {**recalled_from_state, **assigns}

  def finalize_inline_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_INLIN, prev_state)
    return {**recalled_from_state, **assigns}

  def finalize_state_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_STATE, prev_state)
    return {**recalled_from_state, **assigns}

  def finalize_prefs_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_PREFS, prev_state)
    return {**recalled_from_state, **assigns}

  def run(self, assigns: Dict, state: StepState):
    buckets = self.partition_user_asgs(assigns, state)
    manifest_vars, state_vars = buckets[TARGET_CHART], buckets[TARGET_STATE]
    pref_vars = buckets[TARGET_PREFS]
    state.notify_vars_assigned(manifest_vars, state_vars)

    if len(manifest_vars):
      config_man.patch_keyed_manifest_vars(list(manifest_vars.items()))

    if len(pref_vars):
      config_man.patch_keyed_prefs(list(pref_vars.items()))

    if self.runs_action():
      lmc = gen_last_minute_action_config(state)
      from nectwiz.model.action.base.action import Action
      resolved_action = self.inflate_child(
        Action,
        self.action_kod,
        context=resolution_context(state.parent_op)
      )
      job_id = enqueue_action(resolved_action.config, **buckets, lmc=lmc)
      state.notify_action_started(job_id)
    else:
      state.notify_succeeded()

  def partition_user_asgs(self, assigns: Dict, ps: TSS) -> Dict:
    fields = self.visible_fields(assigns, ps.parent_op)

    def find_field(_id):
      return next(filter(lambda f: f.id() == _id, fields), None)

    def seg(_type: str):
      gate = lambda k: find_field(k) and find_field(k).target == _type
      return {k: v for (k, v) in assigns.items() if gate(k)}

    return {
        TARGET_CHART: self.finalize_chart_asgs(seg(TARGET_CHART), ps),
        TARGET_INLIN: self.finalize_inline_asgs(seg(TARGET_INLIN), ps),
        TARGET_STATE: self.finalize_state_asgs(seg(TARGET_STATE), ps),
        TARGET_PREFS: self.finalize_prefs_asgs(seg(TARGET_PREFS), ps),
      }

  @staticmethod
  def compute_status(state: TSS = None) -> Dict:
    if state.is_running():
      action_job = job_client.find_job(state.job_id)
      errdicts = job_client.job_errdicts(state.job_id)
      errors_man.add_errors(errdicts)
      if action_job:
        progress = job_client.job_progress(state.job_id)
        if action_job.is_finished or action_job.is_failed:
          if action_job.is_finished:
            telem = job_client.job_telem(state.job_id)
            state.notify_terminated(action_job.result, telem)
          else:
            state.notify_failed()
          return dict(status=state.status, progress=progress)
        else:
          return dict(status='running', progress=progress)
      else:
        print(f"[nectwiz::step] danger job {state.job_id} lost!")
        return dict(status='negative', progress={})
    else:
      print(f"[nectwiz::step] danger compute_status called when not running")
      state.notify_succeeded()
      return dict(status='negative', progress={})


def gen_last_minute_action_config(state: StepState) -> Dict:
  return dict(
    store_telem=False,
    event_type='operation_step',
    event_name=state.step_sig if state else None,
    event_id=state.parent_op.uuid if state and state.parent_op else None
  )


def resolution_context(op_state: OperationState):
  return dict(
    resolvers=dict(
      operation=lambda n: op_state.all_assigns().get(n)
    )
  )
