from wiz.core import tedi_client
from wiz.model.base.res_match_rule import ResMatchRule
from wiz.model.base.wiz_model import WizModel


class Prerequisite(WizModel):

  def decide(self):
    prereq_satisfied: bool = self.eval_predicate()
    if prereq_satisfied:
      return None, None
    else:
      return self.tone, self.message()

  def eval_predicate(self) -> bool:
    if self.type == 'resource-exists':
      predicate_config = self.config.get('predicate')
      resources = ResMatchRule(predicate_config).query()
      return len(resources) == 1
    elif self.type == 'config-value-eq':
      config = self.config.get('predicate')
      key, expected = config.get('key'), config.get('value')
      actual = tedi_client.chart_value(key)
      return actual == expected

    else:
      print(f"[CRITICAL] No default predicate for type {self.type}")
      return True

  @property
  def type(self):
    return self.config.get('type')

  @property
  def kind(self):
    return self.config.get('kind')

  @property
  def k8kat_selectors(self):
    return self.config.get('k8kat_selectors', {})

  @property
  def tone(self):
    return self.config.get('tone', 'error')

  def message(self):
    return self.config.get('message', 'Condition not met')
