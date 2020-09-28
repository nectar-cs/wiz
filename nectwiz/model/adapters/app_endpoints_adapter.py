from typing import List, Optional, Dict

from typing_extensions import TypedDict

from nectwiz.model.base.wiz_model import WizModel


class AccessPointDict(TypedDict, total=False):
  name: str
  url: Optional[str]
  resource: Optional[Dict]
  command: Optional[str]
  type: str


class AccessPointsAdapter(WizModel):
  # noinspection PyMethodMayBeStatic
  def access_points(self) -> List[AccessPointDict]:
    return []

