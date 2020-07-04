from datetime import datetime
from typing import TypedDict, List

from wiz.model.adapters.adapter import Adapter


class IncidentsAdapter(Adapter):

  class DailyIncidentBundle(TypedDict):
    date: datetime
    application: int
    kubernetes: int

  def day_incident_bundle(self, date) -> DailyIncidentBundle:
    raise NotImplementedError

  def week_incident_bundles(self) -> List[DailyIncidentBundle]:
    return []

  def serialize(self, **kwargs):

    return[

    ]
