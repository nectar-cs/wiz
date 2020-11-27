from typing import List

from k8kat.res.base.kat_res import KatRes
from werkzeug.utils import cached_property

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.supply.value_supplier import ValueSupplier


class ResourcesSupplier(ValueSupplier):

  RESOURCE_SELECTOR_KEY = 'selector'

  @cached_property
  def output_format(self):
    super_value = super(ResourcesSupplier, self).output_format
    if super_value == 'options_format':
      return dict(id='name', title='name')
    return super_value

  @cached_property
  def resource_selector(self) -> ResourceSelector:
    return self.inflate_child(
      ResourceSelector,
      prop=self.RESOURCE_SELECTOR_KEY
    )

  def _compute(self) -> List[KatRes]:
    result = self.resource_selector.query_cluster()
    return result

  def serialize_prop(self):
    pass
