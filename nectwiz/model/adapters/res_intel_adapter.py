import traceback
from typing import Dict, List, TypeVar

from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main.types import IntelDict

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel

T = TypeVar('T', bound='ResIntelProvider')

class ResIntelProvider(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_kod = config.get('resource_selector')

  def covers_res(self, res: KatRes) -> bool:
    selector = self.inflate_child(ResourceSelector, self.selector_kod)
    if selector and res and res.raw:
      context = dict(resolvers=[])
      return selector.selects_res(res.raw.to_dict(), context)
    else:
      print("[nectwiz:res_intel_adapter] no selector or res")

  # noinspection PyMethodMayBeStatic,PyBroadException
  def generate_intel(self, res: KatRes) -> List[IntelDict]:
    try:
      if res.ternary_status() == 'negative':
        return res.intel()
      else:
        return []
    except:
      print(traceback.format_exc())
      print("[nectwiz:res_intel_adapter] exception generating intel ^^")
      return []

  @classmethod
  def weight(cls):
    return 0

  @classmethod
  def covering_res(cls: T, res: KatRes) -> List[T]:
    decide = lambda adapter: adapter.covers_res(res)
    return list(filter(decide, cls.inflate_all()))
