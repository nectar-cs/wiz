from typing import List, Dict, Optional

from werkzeug.utils import cached_property

from nectwiz.core.core.utils import flat2deep
from nectwiz.model.error.errors_man import errors_man

from nectwiz.core.core import job_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import CommitOutcome, PredEval
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.field import Field
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.operation.step_state import StepState

TOS = OperationState
TSS = StepState
TOOS = Optional[OperationState]
TCO = CommitOutcome


class Step(WizModel):

  ACTION_KEY = 'action'
  NEXT_STEP_KEY = 'next'
  FIELDS_KEY = 'fields'

  def __init__(self, config):
    super().__init__(config)
    self.action_kod = config.get('action')

  @cached_property
  def reassignment_descs(self):
    return self.get_prop('reassignments', [])

  def sig(self) -> str:
    parent_id = self.parent.id() if self.parent else 'orphan'
    return f"{parent_id}::{self.id()}"

  def runs_action(self) -> bool:
    return self.action_kod

  def next_step_id(self, op_state: TOS) -> Optional[str]:
    patch = dict(context=resolution_context(op_state, {}))
    return self.resolve_prop(
      self.NEXT_STEP_KEY,
      context_patch=patch
    )

  def has_explicit_next(self) -> bool:
    next_step_kod = self.config.get('next')
    if next_step_kod:
      return not next_step_kod == 'default'
    return False

  def validate_field(self, field_id: str, value: str, op_state: TOS) -> PredEval:
    patch = dict(context=resolution_context(op_state, {field_id: value}))
    return self.inflate_list_child(
      Field,
      prop=self.FIELDS_KEY,
      id=field_id,
      patches=patch
    ).validate(value)

  def visible_fields(self, flat_user_values, op_state: TOS) -> List[Field]:
    patch = dict(context=resolution_context(op_state, flat_user_values))
    fields = self.inflate_children(
      Field,
      prop=self.FIELDS_KEY,
      patches=patch
     )
    return [f for f in fields if f.compute_visibility()]

  def state_recall_descriptors(self, target: str):
    predicate = lambda d: d.get('to', Field.TARGET_CHART) == target
    return filter(predicate, self.reassignment_descs)

  def comp_recalled_asgs(self, target: str, prev_state: TSS) -> Dict:
    state_assigns = prev_state.parent_op.all_assigns()
    new_assigns = {}

    for desc in self.state_recall_descriptors(target):
      _id = desc['id']
      value = desc.get('value', state_assigns.get(_id))
      new_assigns[_id] = value

    return new_assigns

  def gen_chart_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(
      Field.TARGET_CHART,
      prev_state
    )
    return {**recalled_from_state, **assigns}

  def gen_inline_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(
      Field.TARGET_INLIN,
      prev_state
    )
    return {**recalled_from_state, **assigns}

  def gen_state_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(
      Field.TARGET_STATE,
      prev_state
    )
    return {**recalled_from_state, **assigns}

  def gen_prefs_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(
      Field.TARGET_PREFS,
      prev_state
    )
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
    """
    In case action is wrapped by IFTT, we must resolve it
    before it runs in the background process. Also merge in
    event-telem config.
    @param state: step state that IFTT might use to make resolution
    @return: un-IFTT'ed config dict for the action
    """
    from nectwiz.model.action.base.action import Action
    patch = dict(context=resolution_context(state.parent_op, {}))
    resolved_action = self.inflate_child(
      Action,
      prop=self.ACTION_KEY,
      patches=patch
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
      Field.TARGET_CHART: self.gen_chart_asgs(seg(Field.TARGET_CHART), ps),
      Field.TARGET_INLIN: self.gen_inline_asgs(seg(Field.TARGET_INLIN), ps),
      Field.TARGET_STATE: self.gen_state_asgs(seg(Field.TARGET_STATE), ps),
      Field.TARGET_PREFS: self.gen_prefs_asgs(seg(Field.TARGET_PREFS), ps)
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
    flat_manifest_assigns = buckets[Field.TARGET_CHART]
    flat_pref_assigns = buckets[Field.TARGET_PREFS]

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
