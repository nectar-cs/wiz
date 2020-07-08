from typing import Optional, Dict, List

from typing_extensions import TypedDict

class ExitConditionStatus(TypedDict, total=False):
  key: str
  name: str
  met: bool
  reason: Optional[str]
  resources_considered: List[str]


class ExitConditionStatuses(TypedDict, total=False):
  positive: List[ExitConditionStatus]
  negative: List[ExitConditionStatus]


class StepExitStatus(TypedDict, total=False):
  status: str
  condition_statuses: ExitConditionStatuses


class CommitOutcome(TypedDict, total=False):
  status: str
  reason: Optional[str]
  chart_assigns: Dict
  state_assigns: Dict
  job_id: Optional[str]


class K8sResMeta(TypedDict):
  namespace: str
  name: str


class K8sResDict(TypedDict):
  kind: str
  metadata: K8sResMeta
