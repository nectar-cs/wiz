from typing import Optional, Dict, List

from typing_extensions import TypedDict


class UpdateOutcome(TypedDict, total=False):
  update_key: str
  pre_inject: Dict
  post_inject: Dict
  release_logs: Optional[List[str]]
  apply_logs: List[str]


class Update(TypedDict):
  id: str
  type: str
  tami_name: str
  injections: Dict[str, str]


class JobStatusPart(TypedDict):
  name: str
  status: str
  pct: Optional[int]


class JobStatus(TypedDict):
  parts: List[JobStatusPart]
  logs: List[str]


class ExitConditionStatus(TypedDict, total=False):
  key: str
  name: str
  met: bool
  reason: Optional[str]
  resources_considered: List[str]


class ExitConditionStatuses(TypedDict, total=False):
  positive: List[ExitConditionStatus]
  negative: List[ExitConditionStatus]


class StepRunningStatus(TypedDict, total=False):
  status: str
  condition_statuses: ExitConditionStatuses
  job_status: JobStatus


class CommitOutcome(TypedDict, total=False):
  status: str
  reason: Optional[str]
  chart_assigns: Dict
  state_assigns: Dict
  job_id: Optional[str]
  logs: List[str]


class K8sResMeta(TypedDict):
  namespace: str
  name: str


class K8sResDict(TypedDict):
  kind: str
  metadata: K8sResMeta
