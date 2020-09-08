from typing import List, Dict, Optional

from nectwiz.core.core import config_man, utils
from nectwiz.core.core.types import CommitOutcome, StepActionKwargs
from nectwiz.core.job import job_client
from nectwiz.model.action.action import Action
from nectwiz.model.base.res_match_rule import ResMatchRule
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.field.field import Field, TARGET_CHART, TARGET_STATE, TARGET_INLIN, TARGET_TYPES
from nectwiz.model.operations.operation_state import OperationState
from nectwiz.model.pre_built.step_apply_action import StepApplyResAction
from nectwiz.model.step import step_exprs, status_computer
from nectwiz.model.step.step_state import StepState


TOS = OperationState
TSS = StepState
TOOS = Optional[OperationState]
TCO = CommitOutcome


class Step(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.expl_applies_manifest = config.get('applies_manifest')
    self.field_keys = config.get('fields', [])
    self.next_step_desc = self.config.get('next')
    self.state_recall_descs = config.get('state_recalls', [])
    self.exit_predicate_descs = self.config.get('exit', {})

  def sig(self):
    return f"{self.parent.id()}::{self.id()}"

  def applies_manifest(self) -> bool:
    if self.expl_applies_manifest:
      return self.expl_applies_manifest
    else:
      return len(self.res_selectors()) > 0

  def has_action(self) -> bool:
    return bool(self.action())

  def action(self) -> Action:
    explicit_action = self.load_child(Action, 'action')
    if explicit_action:
      return explicit_action
    elif self.applies_manifest():
      return StepApplyResAction({})
    else:
      return self.load_child(Action, 'a')

  def next_step_id(self, values: Dict[str, str]) -> str:
    """
    Returns the id of the next step, be it explicit or an if-then-else type step.
    :param values: if-then-else values, if necessary.
    :return: string containing next step.
    """
    root = self.next_step_desc
    return step_exprs.eval_next_expr(root, values)

  def has_explicit_next(self) -> bool:
    """
    Checks if the current step has an explicit next step.
    :return: True if it does, otherwise False.
    """
    return not step_exprs.is_default_next(self.next_step_desc)

  def fields(self) -> List[Field]:
    """
    Loads the Fields associated with the Step.
    :return: List of Field instances.
    """
    return self.load_children('fields', Field)

  def field(self, key) -> Field:
    return self.load_list_child('fields', Field, key)

  def sanitize_field_assigns(self, values: Dict[str, any]) -> dict:
    def transform(k):
      field = self.field(k)
      field.sanitize_value(values[k]) if field else values[k]
    return {key: transform(key) for key, value in values.items()}

  def res_selectors(self) -> List[ResMatchRule]:
    return list(map(ResMatchRule, self.res_selector_descs))

  def state_recall_descriptors2(self, target):
    predicate = lambda d: d.get('target', 'chart') == target
    return filter(predicate, self.state_recall_descs)

  def comp_recalled_asgs(self, target: str, prev_state: TSS) -> dict:
    descriptors = self.state_recall_descriptors2(target)
    state_assigns = prev_state.parent_op.all_assigns()
    recalled_keys = utils.flatten(d['keys'] for d in descriptors)
    return {key: state_assigns.get(key) for key in recalled_keys}

  # noinspection PyUnusedLocal
  def finalize_chart_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_CHART, prev_state)
    return self.sanitize_field_assigns({**recalled_from_state, **assigns})

  # noinspection PyUnusedLocal
  def finalize_inline_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    recalled_from_state = self.comp_recalled_asgs(TARGET_INLIN, prev_state)
    return self.sanitize_field_assigns({**recalled_from_state, **assigns})

  # noinspection PyUnusedLocal
  def finalize_state_asgs(self, assigns: Dict, op_state: TSS) -> Dict:
    return self.sanitize_field_assigns(assigns)

  def find_commit_status(self, op_state):
    pass

  def run(self, assigns: Dict, prev_state: StepState):
    buckets = self.partition_user_asgs(assigns, prev_state)

    if len(buckets[TARGET_CHART]):
      keyed_tuples = list(buckets[TARGET_CHART].items())
      config_man.commit_keyed_tam_assigns(keyed_tuples)

    if self.has_action():
      action_kwargs = g_action_kwargs(buckets)
      action_cls = self.action().__class__
      job_id = job_client.enqueue_action(action_cls, **action_kwargs)
      prev_state.notify_action_started(job_id)
    else:
      prev_state.notify_succeeded()

  def compute_status(self, prev_state: TSS = None) -> bool:
    if prev_state.was_running():
      parallel_job = job_client.find_job(prev_state.job_id)
      if parallel_job.is_finished:
        prev_state.notify_is_settling()
        return self.compute_status_verifying(prev_state)
      else:
        print("Job still running")
        return False

    elif prev_state.was_verifying():
      status_computer.compute_status(self.config.get('exit'), prev_state)
      return self.compute_status_verifying(prev_state)

  def compute_status_verifying(self, prev_state):
    status_computer.compute_status(self.config.get('exit'), prev_state)
    return True

  def partition_user_asgs(self, assigns: Dict, prev_state: TSS) -> Dict:
    buckets = {target_type: {} for target_type in TARGET_TYPES}

    for key, value in assigns.items():
      matcher = lambda f: f.id() == key
      field = next(filter(matcher, self.fields()), None)
      if field:
        buckets[field.target][key] = value

    buckets[TARGET_CHART] = self.finalize_chart_asgs(assigns, prev_state)
    buckets[TARGET_STATE] = self.finalize_state_asgs(assigns, prev_state)
    buckets[TARGET_INLIN] = self.finalize_inline_asgs(assigns, prev_state)

    return buckets


def g_action_kwargs(buckets) -> StepActionKwargs:
  return StepActionKwargs(
    chart_assigns=buckets[TARGET_CHART],
    inline_assigns=buckets[TARGET_INLIN],
    state_assigns=buckets[TARGET_STATE]
  )
