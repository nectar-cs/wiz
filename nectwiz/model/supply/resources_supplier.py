from functools import lru_cache
from typing import List, Dict

from k8kat.res.base.kat_res import KatRes

from nectwiz.core.core.types import KoD
from nectwiz.model.supply.value_supplier import ValueSupplier


class ResourcesSupplier(ValueSupplier):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_kod: KoD = config.get('selector')

  def _compute(self) -> List[KatRes]:
    from nectwiz.model.base.resource_selector import ResourceSelector
    selector = self.inflate_child(ResourceSelector, self.selector_kod)
    return selector.query_cluster()

  def serialize_prop(self):
    pass

  @lru_cache(maxsize=1)
  def output_format(self):
    if self.desired_output_format == 'options_format':
      return dict(id='name', title='name')
    else:
      return super(ResourcesSupplier, self).output_format()
