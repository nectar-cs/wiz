from typing import Union, Dict, Optional, List

from k8kat.res.base.kat_res import KatRes
from typing_extensions import TypedDict

from nectwiz.core.types import K8sResDict
from nectwiz.core.wiz_app import wiz_app


class RuleDict(TypedDict, total=False):
  kind: str
  name: Optional[str]
  label_selectors: Optional[Dict[str, str]]
  field_selectors: Optional[Dict[str, str]]


class ResMatchRule:
  """Class that holds Resource Match Rules used to filter resources.
  Such rules include:
    1. Resource kind, eg Operation
    2. Resource name
    3. Resource label selectors (as per k8s)
    4. Resource field selectors (as per k8s)
  """

  def __init__(self, obj: Union[str, RuleDict]):
    rule_dict: RuleDict = obj
    if type(obj) == str:
      rule_dict = coerce_rule_expr_to_dict(obj)

    self.kind = rule_dict['kind']
    self.name = rule_dict.get('name')
    self.label_selectors = rule_dict.get('label_selectors')
    self.field_selectors = rule_dict.get('field_selectors')

  def evaluate(self, res: K8sResDict) -> bool:
    """
    Compares own kind and name with that of the passed k8s resource's.
    :param res: k8s resource to be used for comparison.
    :return: returns True if both match, False otherwise.
    """
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
    """
    Uses the rules defined at instantiation (kind, name, label selectors, field
    selectors) to locate all matching k8s resources.
    :return: list of k8s resources, instantiated as k8-kat classes.
    """
    kat_class = KatRes.find_res_class(self.kind)
    if kat_class:
      field_selectors = self.field_selectors

      if self.name and self.name != '*':
        field_selectors = {
          **(field_selectors or {}),
          'metadata.name': self.name
        }

      return kat_class.list(
        ns=wiz_app.ns(),
        labels=self.label_selectors,
        fields=field_selectors
      )
    else:
      print(f"Warn: {self.kind} unsupported by K8Kat, returning []!")
      return []


def coerce_rule_expr_to_dict(expr: str) -> RuleDict:
  """
  Coerces a rule expression from string to dict.
  :param expr: rule expression in string form.
  :return: rule expression in dict form.
  """
  parts = expr.split(':')
  return RuleDict(
    kind=parts[len(parts) - 2],
    name=parts[len(parts) - 1],
  )


def component_matches(rule_exp: str, challenge: str) -> bool:
  """
  Checks if rule expression matches the challenge. Accounts for rule expressions
  being passed as "*".
  :param rule_exp: rule expression to be matched.
  :param challenge: challenged to be matched.
  :return: True if matches, False otherwise.
  """
  if rule_exp:
    if rule_exp == '*' or rule_exp == challenge:
      return True
    else:
      return False
  else:
    return True
