from typing import List, Dict, TypeVar

from k8kat.res.base.kat_res import KatRes
from nectwiz.core.core.utils import keyed2dict, deep_get, deep_get2

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

  def query_cluster(self, context: Dict) -> List[KatRes]:
    kat_class = KatRes.find_res_class(self.k8s_kind)
    if kat_class:
      query_params = self.build_k8kat_query(context)
      return kat_class.list(**query_params)
    else:
      print(f"[nextwiz::res_match_rule] No kat for {self.kind}; kubectl fallback")
      return []

  def selects_res(self, res: K8sResDict, context: Dict) -> bool:
    if self.k8s_kind in [res['kind'], '*']:
      query_dict = self.build_k8kat_query(context)
      res_labels = (res.get('metadata') or {}).get('labels') or {}

      labels_match = query_dict['labels'].items() <= res_labels.items()
      fields_match = keyed_compare(query_dict['fields'], res)

      return labels_match and fields_match
      pass
    else:
      return False

  def build_k8kat_query(self, context: Dict) -> Dict:
    field_selector = self.field_selector

    if self.name and self.name != '*':
      field_selector = {
        'metadata.name': self.name,
        **(field_selector or {}),
      }

    field_selector = interp_dict_vals(field_selector, context)
    label_selector = interp_dict_vals(self.label_selector, context)

    return dict(
      ns=config_man.ns(),
      labels=label_selector,
      fields=field_selector
    )


def keyed_compare(keyed_q_dict: Dict, against_dict: Dict):
  for deep_key, check_val in keyed_q_dict.items():
    actual = deep_get2(against_dict, deep_key)
    if not actual == check_val:
      return False
  return True
