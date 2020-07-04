from typing import List

from wiz.model.adapters.adapter import Adapter
from wiz.model.adapters.resource_adapter import ResourceAdapter


class PodManagerAdapter(ResourceAdapter):

  @classmethod
  def covers_resource(cls, kind):
    return kind in ['Deployment', 'Job', 'ReplicaSet']

  def delete(self):
    pass

  def chart_variable_ids(self) -> List[str]:
    return []



