from typing import List, Dict, Optional

from nectwiz.core.core.utils import flat2deep
from nectwiz.model.error.errors_man import errors_man

from nectwiz.core.core import job_client
from nectwiz.core.core.config_man import config_man
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
    return self._get_prop(
      'next',
      None,
      resolution_context(op_state, {})
    )

  def has_explicit_next(self) -> bool:
    if self.next_step_kod:
      return not self.next_step_kod == 'default'
    return False

  def validate_field(self, field_id: str, value: str, op_state: TOS) -> PredEval:
    patch = dict(context=resolution_context(op_state, {field_id: value}))
    field = self.inflate_child_in_list('fields', Field, field_id, patch)
    return field.validate(value)

  def fields(self) -> List[Field]:
    return self.inflate_children('fields', Field)

  def visible_fields(self, flat_user_values, op_state: TOS) -> List[Field]:
    context = resolution_context(op_state, flat_user_values)
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
    buckets = self.partition_flat_user_asgs(assigns, state)
    state.notify_vars_assigned(buckets)
    self.commit_pertinent_assignments(buckets)

    if self.runs_action():
      action_config = self.assemble_action_config(state)
      job_id = job_client.enqueue_action(action_config, **buckets)
      state.notify_action_started(job_id)
    else:
      state.notify_succeeded()

  def assemble_action_config(self, state: StepState) -> Dict:
    from nectwiz.model.action.base.action import Action
    resolved_action = self.inflate_child(
      Action,
      self.action_kod,
      context=resolution_context(state.parent_op)
    )

    return dict(
      **resolved_action.config,
      **self.last_minute_action_config(state)
    )

  def partition_flat_user_asgs(self, flat_assigns: Dict, ps: TSS) -> Dict:
    fields = self.visible_fields(flat_assigns, ps.parent_op)

    def find_field(_id):
      return next(filter(lambda f: f.id() == _id, fields), None)

    def seg(_type: str):
      gate = lambda k: find_field(k) and find_field(k).target == _type
      return {k: v for (k, v) in flat_assigns.items() if gate(k)}

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

  @staticmethod
  def commit_pertinent_assignments(buckets: Dict):
    flat_manifest_assigns = buckets[TARGET_CHART]
    flat_pref_assigns = buckets[TARGET_PREFS]

    if len(flat_manifest_assigns) > 0:
      config_man.patch_manifest_vars(flat2deep(flat_manifest_assigns))

    if len(flat_pref_assigns) > 0:
      config_man.patch_prefs(flat2deep(flat_pref_assigns))

  @staticmethod
  def last_minute_action_config(state: StepState) -> Dict:
    op_state = state.parent_op if state else None
    return dict(
      store_telem=False,
      event_type='operation_step',
      event_name=state.step_sig if state else None,
      event_id=op_state.uuid if op_state else None
    )


def resolution_context(op_state: OperationState, user_input: Dict):
  return dict(
    resolvers=dict(
      input=lambda n: user_input.get(n),
      operation=lambda n: op_state.all_assigns().get(n)
    )
  )
