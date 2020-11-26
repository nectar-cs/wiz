from functools import lru_cache
from typing import List, Dict

from k8kat.res.base.kat_res import KatRes
from werkzeug.utils import cached_property

from nectwiz.core.core.types import KoD
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.supply.value_supplier import ValueSupplier


class ResourcesSupplier(ValueSupplier):

  RESOURCE_SELECTOR_KEY = 'selector'

  @cached_property
  def resource_selector(self) -> ResourceSelector:
    return self.inflate_child(
      ResourceSelector,
      prop=self.RESOURCE_SELECTOR_KEY
    )

  def _compute(self) -> List[KatRes]:
    return self.resource_selector.query_cluster()

  def serialize_prop(self):
    pass

  @lru_cache(maxsize=1)
  def output_format(self):
    if self.desired_output_format == 'options_format':
      return dict(id='name', title='name')
    else:
      return super(ResourcesSupplier, self).output_format()
