from typing import List, Dict

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

  def next_step_id(self, values: Dict[str, str]) -> str:
    root = self.config.get('next')
    return expr.eval_next_expr(root, values)

  def field(self, key) -> Field:
    field_configs = self.config.get('fields', [])
    step_key = [s for s in field_configs if s == key][0]
    return Field.inflate(step_key)

  def fields(self) -> List[Field]:
    return [self.field(key) for key in self.field_keys]

  def commit(self, values):
    normal_values, inline_values = partition_values(self.fields(), values)

    if normal_values:
      tedi_client.commit_values(normal_values.items())

    if self.should_apply():
      rule_exprs = self.config.get('res', [])
      rules = [ResMatchRule(rule_expr) for rule_expr in rule_exprs]
      tedi_client.apply(rules, inline_values.items())

  def status(self):
    if not self.should_apply():
      return 'done'
    return 'done'

  def should_apply(self) -> bool:
    raw = self.config.get('apply', 'False')
    return str(raw).lower() == 'true'

  def watch_res_kinds(self):
    field_kinds = [f.watch_res_kinds for f in self.fields()]
    field_kinds = [item for sublist in field_kinds for item in sublist]
    return list(set(field_kinds))


def partition_values(fields: List[Field], values: Dict[str, str]) -> List[Dict]:
  normal_values, inline_values = {}, {}
  get_field = lambda k: [f for f in fields if f.key == k][0]
  for key, value in values.items():
    is_inline = get_field(key).is_inline
    bucket = inline_values if is_inline else normal_values
    bucket[key] = value
  return [normal_values, inline_values]
