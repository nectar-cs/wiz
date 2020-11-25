from typing import Dict

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.predicate.predicate import Predicate


class ResourceCountPredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.selector_kod = config.get('selector')

  def evaluate(self) -> bool:
    res_list = self.selector().query_cluster(self.context)
    return self._common_compare(len(res_list))

  def selector(self) -> ResourceSelector:
    return ResourceSelector.inflate(self.selector_kod)
