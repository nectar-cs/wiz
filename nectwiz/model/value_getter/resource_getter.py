from typing import Dict, Any, Optional

from nectwiz.core.core.utils import getattr_deep
from nectwiz.model.value_getter.value_getter import ValueGetter


class ResourceGetter(ValueGetter):
  def __init__(self, config: Dict):
    super().__init__(config)
    from nectwiz.model.base.resource_selector import ResourceSelector
    self.resource_selector: ResourceSelector = config.get('selector')
    self.return_property = config.get('property', 'ternary_status')
    self.tolerate_multiple = config.get('tolerate_multiple', False)

  def produce(self) -> Optional[Any]:
    resources = self.resource_selector.query_cluster({})
    if len(resources) > 0:
      if len(resources) > 1 and not self.tolerate_multiple:
        return None
      return getattr_deep(resources[0], self.return_property)
    return None
