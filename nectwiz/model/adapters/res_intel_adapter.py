from typing import Dict, List, TypeVar

from k8kat.res.base.kat_res import KatRes
from k8kat.res.pod.kat_pod import KatPod
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import IntelDict
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel


T = TypeVar('T', bound='ResIntelAdapter')

class ResIntelAdapter(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_kod = config.get('resource_selector')

  def covers_res(self, res: KatRes) -> bool:
    selector = self.inflate_child(ResourceSelector, self.selector_kod)
    if selector:
      context = dict(resolvers=config_man.resolvers())
      return selector.selects_res(res_dict, context)
    else:
      print("[nectwiz:res_intel_adapter] no selector found")

  def generate_intel_items(self, res: KatRes) -> List[IntelDict]:
    return []

  @classmethod
  def covering_res(cls: T, res_dict: Dict) -> List[T]:
    decide = lambda adapter: adapter.covers_res(res_dict)
    return list(filter(decide, cls.inflate_all()))


class PodIntelAdapter(ResIntelAdapter):
  def covers_res(self, kat_res: KatRes) -> bool:
    return kat_res.kind == 'Pod'

  def generate_intel_items(self, res: KatPod) -> List[IntelDict]:
    if res.ternary_status() == 'negative':
      pass
    else:
      return []
