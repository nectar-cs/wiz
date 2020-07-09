from abc import abstractmethod
from typing import List, Dict, Union, Tuple, Optional

from wiz.core import tedi_client, step_job_prep, utils
from wiz.core.osr import OperationState, StepState
from wiz.core.types import CommitOutcome, StepRunningStatus
from wiz.model.base.res_match_rule import ResMatchRule
from wiz.model.base.wiz_model import WizModel
from wiz.model.field.field import Field, TARGET_CHART, TARGET_STATE, TARGET_INLINE, TARGET_TYPES
from wiz.model.step import step_exprs
from wiz.model.step.step_exprs import parse_recalled_state

TOS = OperationState
TOOS = Optional[OperationState]
TCO = CommitOutcome


class Step(WizModel):

  @property
  def field_keys(self):
    return self.config.get('fields', [])

  def updates_chart(self) -> bool:
    if 'updates_chart' in self.config.keys():
      return self.config.get('updates_chart', True)
    else:
      manifest_fields = filter(Field.is_chart_var, self.fields())
      return len(list(manifest_fields)) > 0

  def applies_manifest(self) -> bool:
    if 'applies_manifest' in self.config.keys():
      return self.config.get('applies_manifest', True)
    else:
      manifest_fields = filter(Field.is_manifest_bound, self.fields())
      return len(list(manifest_fields)) > 0

  def runs_job(self) -> bool:
    return bool(self.job_descriptor)

  def is_long_running(self):
    return self.runs_job() or self.applies_manifest()

  @property
  def res_selector_descs(self) -> List[Union[str, Dict]]:
    return self.config.get('resource_apply_filter', [])

  @property
  def next_step_descriptor(self) -> Union[Dict, str]:
    return self.config.get('next')

  @property
  def job_descriptor(self) -> Dict:
    return self.config.get('job', {})

  def next_step_id(self, values: Dict[str, str]) -> str:
    root = self.next_step_descriptor
    return step_exprs.eval_next_expr(root, values)

  def has_explicit_next(self):
    return not step_exprs.is_default_next(self.next_step_descriptor)

  def fields(self) -> List[Field]:
    return self.load_children('fields', Field)

  def field(self, key) -> Field:
    return self.load_list_child('fields', Field, key)

  def sanitize_field_assigns(self, values: Dict[str, any]) -> Dict:
    transform = lambda k: self.field(k).sanitize_value(values[k])
    return {key: transform(key) for key, value in values.items()}

  def res_selectors(self) -> List[ResMatchRule]:
    return [ResMatchRule(obj) for obj in self.res_selector_descs]

  @abstractmethod
  def gen_job_params(self, values, op_state: OperationState) -> Dict:
    return values

  def compute_recalled_assigns(self, target: str, op_state: TOS) -> Dict:
    predicate = lambda d: d.get('target', 'chart') == target
    descriptors = filter(predicate, self.config.get('state_recalls', []))
    state_assigns = op_state.state_assigns()
    gather_keys = lambda d: parse_recalled_state(d, state_assigns.keys())
    recalled_keys = utils.flatten(map(gather_keys, descriptors))
    return {key: state_assigns.get(key) for key in recalled_keys}

  def finalize_chart_values(self, assigns: Dict, op_state: TOS):
    recalled_from_state = self.compute_recalled_assigns('chart', op_state)
    return self.sanitize_field_assigns({**recalled_from_state, **assigns})

  def finalize_inline_values(self, assigns: Dict, op_state: TOS):
    recalled_from_state = self.compute_recalled_assigns('inline', op_state)
    return self.sanitize_field_assigns({**recalled_from_state, **assigns})

  # noinspection PyUnusedLocal
  def finalize_state_values(self, assigns: Dict, op_state: TOS):
    return self.sanitize_field_assigns(assigns)

  def begin_job(self, values, op_state: OperationState) -> str:
    image = self.job_descriptor.get('image', 'busybox')
    command = self.job_descriptor.get('command')
    args = self.job_descriptor.get('args', [])
    params = self.gen_job_params(values, op_state)
    return step_job_prep.create_and_run(image, command, args, params)

  def commit(self, assigns: Dict, op_state: OperationState = None) -> TCO:
    op_state = op_state or OperationState()
    final_assigns = self.partition_value_assigns(assigns, op_state)
    chart_assigns, inline_assigns, state_assigns = final_assigns
    outcome = CommitOutcome(
      chart_assigns=chart_assigns,
      state_assigns=state_assigns
    )

    if len(chart_assigns):
      tedi_client.commit_values(chart_assigns.items())

    rules = list(map(ResMatchRule, self.res_selector_descs))
    if len(rules):
      tedi_client.apply(rules=rules, inlines=inline_assigns.items())
      return CommitOutcome(**outcome, status='pending')

    if self.runs_job():
      job_id = self.begin_job(state_assigns, op_state)
      return CommitOutcome(**outcome, status='pending', job_id=job_id)

    return CommitOutcome(**outcome, status='positive')

  def compute_status(self, op_state: TOOS = None) -> StepRunningStatus:
    from wiz.model.step.step_status_computer import StepStatusComputer
    own_state = self.find_own_state(op_state) if op_state else None
    computer = StepStatusComputer(self, own_state)
    return computer.compute_status()

  def is_state_owner(self, ss: StepState) -> bool:
    return ss.step_id == self.key and \
           ss.stage_id == self.parent.key

  def find_own_state(self, op_state: OperationState) -> Optional[StepState]:
    return next(filter(self.is_state_owner, op_state.step_states), None)

  def flags(self):
    _flags: List[str] = self.config.get('flags', [])
    if self.applies_manifest():
      _flags.append('manifest_applying')
    if self.runs_job():
      _flags.append('job_running')
    return list(set(_flags))

  def partition_value_assigns(self, assigns, op_state) -> Tuple:
    buckets = {target_type: {} for target_type in TARGET_TYPES}

    for key, value in assigns.items():
      field = next((f for f in self.fields() if f.key == key), None)
      if field:
        buckets[field.target][key] = value

    for target_type in TARGET_TYPES:
      finalizer = target_type_to_finalizer_mapping[target_type]
      # noinspection PyArgumentList
      buckets[target_type] = finalizer(self, buckets[target_type], op_state)

    return tuple(buckets[target_type] for target_type in TARGET_TYPES)


target_type_to_finalizer_mapping = {
  TARGET_CHART: Step.finalize_chart_values,
  TARGET_INLINE: Step.finalize_inline_values,
  TARGET_STATE: Step.finalize_state_values
}
