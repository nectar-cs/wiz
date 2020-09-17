from typing import Dict, Optional, List

from k8kat.res.base.kat_res import KatRes
from typing_extensions import TypedDict

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import K8sResDict
from nectwiz.model.base.wiz_model import WizModel


class RuleDict(TypedDict, total=False):
  k8s_kind: str
  name: Optional[str]
  label_selectors: Optional[Dict[str, str]]
  field_selectors: Optional[Dict[str, str]]


class ResourceSelector(WizModel):
  def __init__(self, config: RuleDict):
    super().__init__(config)
    self.k8s_kind = config['k8s_kind']
    self.name = config.get('name')
    self.label_selectors = config.get('label_selectors')
    self.field_selectors = config.get('field_selectors')

  @classmethod
  def from_expr(cls, expr: str):
    parts = expr.split(':')
    return cls(config=RuleDict(
      k8s_kind=parts[len(parts) - 2],
      name=parts[len(parts) - 1],
    ))

  def evaluate(self, res: K8sResDict) -> bool:
    res_kind = res['kind']
    res_name = res['metadata']['name']

    tuples = [(self.kind, res_kind), (self.name, res_name)]

    for rule, challenge in tuples:
      if not component_matches(rule, challenge):
        return False
    return True

  def query(self) -> List[KatRes]:
    kat_class = KatRes.find_res_class(self.k8s_kind)
    if kat_class:
      field_selectors = self.field_selectors

      if self.name and self.name != '*':
        field_selectors = {
          **(field_selectors or {}),
          'metadata.name': self.name
        }

      return kat_class.list(
        ns=config_man.ns(),
        labels=self.label_selectors,
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
