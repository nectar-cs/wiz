from typing import List

from k8_kat.res.pod.kat_pod import KatPod
from wiz.core import tec_client
from wiz.core.res_match_rule import ResMatchRule
from wiz.core.wiz_globals import wiz_globals
from wiz.model.field.field import Field
from wiz.model.base.wiz_model import WizModel
from wiz.model.step import expr


class Step(WizModel):

  def __init__(self, config):
    super().__init__(config)

  def next_step_key(self, state) -> str:
    root = self.config.get('next')
    return expr.eval_next_expr(root, state)

  def field(self, key) -> Field:
    field_configs = self.config.get('fields', [])
    step_key = [s for s in field_configs if s == key][0]
    return Field.inflate(step_key)

  def fields(self) -> List[Field]:
    return [self.field(key) for key in self.config['fields']]

  def commit(self, state):
    tec_client.commit_values(state)
    rule_exprs = self.config.get('res', [])
    rules = [ResMatchRule(rule_expr) for rule_expr in rule_exprs]
    if self.should_apply():
      tec_client.apply(rules)

  def should_apply(self) -> bool:
    return self.config.get('apply', 'False').lower() == 'true'
