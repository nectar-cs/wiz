from typing import Union, Dict, Optional, List

from k8_kat.res.base.kat_res import KatRes
from typing_extensions import TypedDict

from wiz.core.types import K8sResDict
from wiz.core.wiz_globals import wiz_globals


class RuleDict(TypedDict):
  kind: str
  name: Optional[str]
  label_selectors: Optional[Dict[str, str]]
  field_selectors: Optional[Dict[str, str]]

class ResMatchRule:

  def __init__(self, obj: Union[str, RuleDict]):
    rule_dict: RuleDict = obj
    if type(obj) == str:
      rule_dict = expr_to_rule_dict(obj)

    self.kind = rule_dict['kind']
    self.name = rule_dict.get('name')
    self.label_selectors = rule_dict.get('label_selectors')
    self.field_selectors = rule_dict.get('field_selectors')

  def evaluate(self, res: K8sResDict) -> bool:
    res_kind = res['kind']
    res_name = res['metadata']['name']

    tuples = [
      (self.kind, res_kind),
      (self.name, res_name)
    ]

    for rule, challenge in tuples:
      if not component_matches(rule, challenge):
        return False

    return True


  def query(self) -> List[KatRes]:
    kat_class = KatRes.find_res_class(self.kind)
    if kat_class:
      field_selectors = self.field_selectors

      if self.name and self.name != '*':
        field_selectors = {
          **(field_selectors or {}),
          'metadata.name': self.name
        }

      return kat_class.list(
        ns=wiz_globals.ns,
        labels=self.label_selectors,
        fields=field_selectors
      )
    else:
      print(f"{self.kind} unsupported by K8Kat, kubectl fallback")
      print("Except kubectl fallback not implemented either :/, returning []")
      return []

def expr_to_rule_dict(expr: str) -> RuleDict:
  parts = expr.split(':')
  return RuleDict(
    kind=parts[len(parts) - 2],
    name=parts[len(parts) - 1],
  )


def component_matches(rule_exp: str, challenge: str) -> bool:
  if rule_exp:
    if rule_exp == '*' or rule_exp == challenge:
      return True
    else:
      return False
  else:
    return True

