from typing import List, Dict, TypeVar

from k8kat.res.base.kat_res import KatRes

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.subs import interp
from nectwiz.core.core.types import K8sResDict
from nectwiz.model.base.wiz_model import WizModel

T = TypeVar('T', bound='ResourceSelector')

class ResourceSelector(WizModel):
  def __init__(self, config):
    super().__init__(config)
    self.k8s_kind = config['k8s_kind']
    self.name = config.get('name')
    self.label_selector = config.get('label_selector')
    self.field_selector = config.get('field_selector')

  @classmethod
  def from_expr(cls, expr: str, context) -> T:
    if ":" in expr:
      parts = interp(expr, context).split(':')
      return cls(config=dict(
        k8s_kind=parts[len(parts) - 2],
        name=parts[len(parts) - 1],
      ))
    else:
      return cls.inflate(expr)

  def evaluate(self, res: K8sResDict) -> bool:
    res_kind = res['kind']
    res_name = res['metadata']['name']

    tuples = [(self.kind, res_kind), (self.name, res_name)]

    for rule, challenge in tuples:
      if not component_matches(rule, challenge):
        return False
    return True

  def query(self, context: Dict) -> List[KatRes]:
    kat_class = KatRes.find_res_class(self.k8s_kind)
    if kat_class:
      field_selectors = self.field_selector

      if self.name and self.name != '*':
        field_selectors = {
          **(field_selectors or {}),
          'metadata.name': self.name
        }

      return kat_class.list(
        ns=config_man.ns(),
        labels=self.label_selector,
        fields=field_selectors
      )
    else:
      print(f"[nextwiz::res_match_rule] No kat for {self.kind}; kubectl fallback")
      return []


def component_matches(rule_exp: str, challenge: str) -> bool:
  if rule_exp:
    if rule_exp == '*' or rule_exp == challenge:
      return True
    else:
      return False
  else:
    return True
