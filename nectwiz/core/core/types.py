from typing import Optional, Dict, List, Union

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
  tam_version: str
  injections: Dict[str, str]


class JobStatusPart(TypedDict):
  name: str
  status: str
  pct: Optional[int]


class JobStatus(TypedDict):
  parts: List[JobStatusPart]
  logs: List[str]


class PredEval(TypedDict, total=False):
  predicate_id: str
  name: str
  met: bool
  reason: Optional[str]


class ExitStatuses(TypedDict, total=False):
  positive: List[PredEval]
  negative: List[PredEval]


class CommitOutcome(TypedDict, total=False):
  status: str
  reason: Optional[str]
  logs: List[str]


class K8sResMeta(TypedDict):
  namespace: str
  name: str


class K8sResDict(TypedDict):
  kind: str
  metadata: K8sResMeta


class TamDict(TypedDict):
  type: str
  uri: str
  args: Optional[List[str]]
  ver: str


class ActionOutcome(TypedDict):
  cls_name: str
  id: str
  charge: str
  summary: str
  data: Dict


class StepActionKwargs(TypedDict):
  inline_assigns: Dict
  chart_assigns: Dict
  state_assigns: Dict


class KtlApplyOutcome(TypedDict):
  kind: str
  name: str
  verb: str
