from typing import List, Dict, TypeVar

from k8kat.res.base.kat_res import KatRes

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.subs import interp_dict_vals
from nectwiz.core.core.types import K8sResDict
from nectwiz.model.base.wiz_model import WizModel

T = TypeVar('T', bound='ResourceSelector')

class ResourceSelector(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.k8s_kind = config.get('k8s_kind')
    self.name: str = config.get('name')
    self.label_selector: Dict = config.get('label_selector') or {}
    self.field_selector: Dict = config.get('field_selector') or {}

  @classmethod
  def inflate_with_key(cls, _id: str) -> T:
    if ":" in _id:
      parts = _id.split(':')
      return cls.inflate_with_config(dict(
        k8s_kind=parts[len(parts) - 2],
        name=parts[len(parts) - 1],
      ))
    else:
      return super().inflate_with_key(_id)

  def evaluate(self, res: K8sResDict) -> bool:
    res_kind = res['kind']
    res_name = res['metadata']['name']

    tuples = [(self.k8s_kind, res_kind), (self.name, res_name)]

    for rule, challenge in tuples:
      if not component_matches(rule, challenge):
        return False
    return True

  def query_cluster(self, context: Dict) -> List[KatRes]:
    kat_class = KatRes.find_res_class(self.k8s_kind)
    if kat_class:
      query_params = self.build_k8kat_query(context)
      return kat_class.list(**query_params)
    else:
      print(f"[nextwiz::res_match_rule] No kat for {self.kind}; kubectl fallback")
      return []

  def build_k8kat_query(self, context: Dict) -> Dict:
    field_selector = self.field_selector

    if self.name and self.name != '*':
      field_selector = {
        **(field_selector or {}),
        'metadata.name': self.name
      }

    field_selector = interp_dict_vals(field_selector, context)
    label_selector = interp_dict_vals(self.label_selector, context)

    return dict(
      ns=config_man.ns(),
      labels=label_selector,
      fields=field_selector
    )


def component_matches(rule_exp: str, challenge: str) -> bool:
  if rule_exp:
    if rule_exp == '*' or rule_exp == challenge:
      return True
    else:
      return False
  else:
    return True
