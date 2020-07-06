from typing import List, Dict, Union, Tuple, Optional

from wiz.core import tedi_client, step_job_client, step_job_prep
from wiz.core.osr import OperationState, StepState
from wiz.model.base.res_match_rule import ResMatchRule
from wiz.core.types import CommitOutcome
from wiz.model.base.wiz_model import WizModel
from wiz.model.field.field import Field
from wiz.model.step import next_expr
from wiz.model.step.exit_condition import ExitCondition


class Step(WizModel):

  @property
  def updates_chart(self) -> bool:
    return self.config.get('updates_chart', True)

  @property
  def applies_manifest(self) -> bool:
    return self.config.get('applies_manifest', True)

  @property
  def runs_job(self) -> bool:
    return bool(self.job_descriptor)

  @property
  def is_long_running(self):
    return self.runs_job or self.applies_manifest

  @property
  def field_keys(self):
    return self.config.get('fields', [])

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
    return next_expr.eval_next_expr(root, values)

  def has_explicit_next(self):
    return not next_expr.is_default_next(self.next_step_descriptor)

  def fields(self) -> List[Field]:
    return self.load_children('fields', Field)

  def field(self, key) -> Field:
    return self.load_list_child('fields', Field, key)

  def sanitize_field_values(self, values: Dict[str, any]):
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

  # noinspection PyUnusedLocal
  def compute_values(self, values, op_state) -> Tuple[Dict, Dict]:
    mapped_values = self.sanitize_field_values(values)
    return partition_values(self.fields(), mapped_values)

  def commit(self, values, op_state) -> CommitOutcome:
    normal_values, inline_values = self.compute_values(values, op_state)

    if self.updates_chart and normal_values:
      # noinspection PyTypeChecker
      tedi_client.commit_values(normal_values.items())

    if self.applies_manifest:
      rule_exprs = self.res_selector_descs
      rules = [ResMatchRule(rule_expr) for rule_expr in rule_exprs]
      tedi_client.apply(rules, inline_values.items())
      return CommitOutcome(status='pending', assignments=normal_values)

    if self.runs_job:
      job_id = self.begin_job(values, op_state)
      return CommitOutcome(
        status='positive',
        assignments=normal_values,
        job_id=job_id
      )

    return CommitOutcome(status='positive', assignments=normal_values)

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
    if self.applies_manifest:
      return default_res_exit_conds
    elif self.runs_job:
      return default_job_exit_conds
    else:
      print("DANGER no default exit conditions for step " + self.key)
      return [], []

  def own_state(self, op_state: OperationState) -> Optional[StepState]:
    matcher = (ss for ss in op_state.step_states if ss.step_id == self.key)
    return next(matcher, None)

  @property
  def flags(self):
    _flags: List[str] = self.config.get('flags', [])
    if self.applies_manifest:
      _flags.append('manifest_applying')
    if self.runs_job:
      _flags.append('job_running')
    return list(set(_flags))


def partition_values(fields: List[Field], values: Dict[str, str]) -> Tuple[Dict, Dict]:
  internal_values, chart_values, inline_values = {}, {}, {}

  for key, value in values.items():
    field = next(f for f in fields if f.key == key)
    is_normal = field is None or not field.is_inline
    bucket = chart_values if is_normal else inline_values
    bucket[key] = value

  return chart_values, inline_values


default_res_exit_conds = (
  ['nectar.exit_conditions.all_resources_positive'],
  ['nectar.exit_conditions.any_resource_negative']
)


default_job_exit_conds = (
  ['nectar.exit_conditions.job_in_succeeded_phase'],
  ['nectar.exit_conditions.job_in_failed_phase']
 )
