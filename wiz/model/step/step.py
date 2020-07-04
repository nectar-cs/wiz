from typing import List, Dict, Union, Tuple, Optional

from wiz.core import tedi_client
from wiz.core.res_match_rule import ResMatchRule
from wiz.model.base.wiz_model import WizModel
from wiz.model.field.field import Field
from wiz.model.step import expr


class Step(WizModel):

  def __init__(self, config):
    super().__init__(config)

  @property
  def field_keys(self):
    return self.config.get('fields', [])

  @property
  def res_selector_descs(self) -> List[Union[str, Dict]]:
    return self.config.get('res', [])

  @property
  def applies(self) -> bool:
    selectors = self.res_selector_descs
    override = self.config.get('apply', None)
    return override if override is not None else len(selectors) > 0

  @property
  def next_step_descriptor(self):
    return self.config.get('next')

  def next_step_id(self, values: Dict[str, str]) -> str:
    root = self.next_step_descriptor
    return expr.eval_next_expr(root, values)

  def has_explicit_next(self):
    return not expr.is_default_next(self.next_step_descriptor)

  def fields(self) -> List[Field]:
    return self.load_children('fields', Field)

  def field(self, key) -> Field:
    return self.load_child('fields', Field, key)

  def sanitize_field_values(self, values: Dict[str, any]):
    transform = lambda k: self.field(k).sanitize_value(values[k])
    return {key: transform(key) for key, value in values.items()}

  def stage(self, values):
    mapped_values = self.sanitize_field_values(values)
    normal_values, _ = partition_values(self.fields(), mapped_values)
    return normal_values

  def commit(self, values) -> Tuple[str, Optional[str]]:
    mapped_values = self.sanitize_field_values(values)
    normal_values, inline_values = partition_values(self.fields(), mapped_values)

    if normal_values:
      tedi_client.commit_values(normal_values.items())

    if self.applies:
      rule_exprs = self.res_selector_descs
      rules = [ResMatchRule(rule_expr) for rule_expr in rule_exprs]
      tedi_client.apply(rules, inline_values.items())
      return 'pending', None

    return 'positive', None

  def res_selectors(self) -> List[ResMatchRule]:
    return [ResMatchRule(obj) for obj in self.res_selector_descs]

  def affected_resources(self):
    affected_res = []
    for rule in self.res_selectors():
      resources = rule.query()
      affected_res += resources
    return affected_res

  def status(self):
    if not self.applies:
      return 'positive'

    resources = self.affected_resources()
    res_statuses = set([r.ternary_status() for r in resources])
    if len(res_statuses) == 1:
      return list(res_statuses)[0]
    elif "negative" in res_statuses:
      return "negative"
    else:
      return "pending"

  @property
  def flags(self):
    _flags: List[str] = self.config.get('flags', [])
    if self.applies:
      _flags.append('manifest_applying')
    return list(set(_flags))

def partition_values(fields: List[Field], values: Dict[str, str]) -> List[Dict]:
  normal_values, inline_values = {}, {}

  def get_field(k):
    matches = [f for f in fields if f.key == k]
    return matches[0] if len(matches) else None

  for key, value in values.items():
    field = get_field(key)
    is_normal = field is None or not field.is_inline
    bucket = normal_values if is_normal else inline_values
    bucket[key] = value
  return [normal_values, inline_values]
