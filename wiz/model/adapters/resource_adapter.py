from typing import List

from wiz.model.adapters.adapter import Adapter


class ResourceAdapter(Adapter):

  @classmethod
  def covers_resource(cls, kind):
    return True

  def delete(self):
    pass

  def chart_variable_ids(self) -> List[str]:
    return []
