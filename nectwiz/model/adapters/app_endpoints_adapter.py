from typing import List

from typing_extensions import TypedDict

from nectwiz.model.base.wiz_model import WizModel


class EndpointDict(TypedDict):
  name: str
  url: str


class AppEndpointsAdapter(WizModel):
  def endpoints(self) -> List[EndpointDict]:
    return []
