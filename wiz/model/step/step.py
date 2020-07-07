from typing import List, Dict, Union, Tuple, Optional

from wiz.core import tedi_client, step_job_client, step_job_prep, utils
from wiz.core.osr import OperationState, StepState
from wiz.model.base.res_match_rule import ResMatchRule
from wiz.core.types import CommitOutcome
from wiz.model.base.wiz_model import WizModel
from wiz.model.field.field import Field, TARGET_CHART, TARGET_STATE, TARGET_INLINE, TARGET_TYPES
from wiz.model.step import step_exprs
from wiz.model.step.exit_condition import ExitCondition
from wiz.model.step.step_exprs import parse_recalled_state


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
  def next_step_descriptor(self):
    return self.config.get('next')

  @property
  def job_descriptor(self):
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

  def sanitize_field_assigns(self, values: Dict[str, any]):
    transform = lambda k: self.field(k).sanitize_value(values[k])
    return {key: transform(key) for key, value in values.items()}

  def res_selectors(self) -> List[ResMatchRule]:
    return [ResMatchRule(obj) for obj in self.res_selector_descs]

  # noinspection PyMethodMayBeStatic,PyUnusedLocal
  def gen_job_params(self, values, op_state):
    return values

  def begin_job(self, values, op_state) -> str:
    image = self.job_descriptor.get('image', 'busybox')
    command = self.job_descriptor.get('command')
    args = self.job_descriptor.get('args', [])
    params = self.gen_job_params(values, op_state)
    return step_job_prep.create_and_run(image, command, args, params)

  def compute_recalled_assigns(self, target: str, op_state: OperationState) -> Dict:
    predicate = lambda d: d.get('target', 'chart') == target
    descriptors = filter(predicate, self.config.get('state_recalls', []))
    state_assigns, state_keys = op_state.bank(), op_state.bank().keys()
    gather_keys = lambda d: parse_recalled_state(d, state_keys)
    recalled_keys = utils.flatten(map(gather_keys, descriptors))
    return {key: state_assigns[key] for key in recalled_keys}

  def finalize_chart_values(self, assigns: Dict, op_state: OperationState):
    recalled_from_state = self.compute_recalled_assigns('chart', op_state)
    return self.sanitize_field_assigns({**recalled_from_state, **assigns})

  def finalize_inline_values(self, assigns: Dict, op_state: OperationState):
    recalled_from_state = self.compute_recalled_assigns('inline', op_state)
    return self.sanitize_field_assigns({**recalled_from_state, **assigns})

  # noinspection PyUnusedLocal
  def finalize_state_values(self, assigns: Dict, op_state: OperationState):
    return self.sanitize_field_assigns(assigns)

  def commit(self, assigns: Dict, op_state: OperationState) -> CommitOutcome:
    final_assigns = self.partition_value_assigns(assigns, op_state)
    chart_assigns, inline_assigns, state_assigns = final_assigns
    outcome = CommitOutcome(chart_assigns=chart_assigns, state_assigns=state_assigns)

    if len(chart_assigns) > 0:
      tedi_client.commit_values(chart_assigns.items())

    if self.applies_manifest():
      rules = [ResMatchRule(rule_expr) for rule_expr in self.res_selector_descs]
      tedi_client.apply(rules=rules, inlines=inline_assigns.items())
      return CommitOutcome(**outcome, status='pending')

    if self.runs_job():
      job_id = self.begin_job(assigns, op_state)
      return CommitOutcome(**outcome, status='pending', job_id=job_id)

    return CommitOutcome(**outcome, status='positive')

  def status_bundle(self, op_state: OperationState):
    bundle = dict(status=self.compute_status(op_state))
    if self.runs_job:
      job_id = self.own_state(op_state).job_id
      bundle['job_status'] = step_job_client.read_job_meta_status(job_id)
    return bundle

  def compute_status(self, op_state: OperationState):
    root = self.config.get('exit', {})
    own_state = self.own_state(op_state)

    defaults = self.default_exit_conditions()
    parse = lambda k, d: self.load_child(ExitCondition, root.get(k, d))
    success_conds: List[ExitCondition] = parse('positive', defaults[0])
    failure_conds: List[ExitCondition] = parse('negative', defaults[1])

    for success_cond in success_conds:
      if success_cond.evaluate(own_state):
        return dict(status='positive')

    for failure_cond in failure_conds:
      if failure_cond.evaluate(own_state):
        return dict(
          status='negative',
          error=failure_cond.title,
          reason=failure_cond.reason
        )

    return dict(status='pending')

  def default_exit_conditions(self) -> Tuple[List, List]:
    if self.applies_manifest():
      return default_res_exit_conds
    elif self.runs_job():
      return default_job_exit_conds
    else:
      print("DANGER no default exit conditions for step " + self.key)
      return [], []

  def own_state(self, op_state: OperationState) -> Optional[StepState]:
    matcher = (ss for ss in op_state.step_states if ss.step_id == self.key)
    return next(matcher, None)

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
      field = next(f for f in self.fields() if f.key == key)
      buckets[field.target][key] = value

    for target_type in TARGET_TYPES:
      worker = target_type_to_finalizer_mapping[target_type]
      # noinspection PyArgumentList
      buckets[target_type] = worker(self, buckets[target_type], op_state)

    return tuple(buckets[target_type] for target_type in TARGET_TYPES)



target_type_to_finalizer_mapping = {
  TARGET_CHART: Step.finalize_chart_values,
  TARGET_INLINE: Step.finalize_inline_values,
  TARGET_STATE: Step.finalize_state_values
}


default_res_exit_conds = (
  ['nectar.exit_conditions.all_resources_positive'],
  ['nectar.exit_conditions.any_resource_negative']
)


default_job_exit_conds = (
  ['nectar.exit_conditions.job_in_succeeded_phase'],
  ['nectar.exit_conditions.job_in_failed_phase']
 )
