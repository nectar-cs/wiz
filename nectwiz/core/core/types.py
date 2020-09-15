from typing import Optional, Dict, List

from typing_extensions import TypedDict


class UpdateDict(TypedDict):
  id: str
  type: str
  version: str
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
  data: Dict


class StepActionKwargs(TypedDict):
  inline_assigns: Dict
  chart_assigns: Dict
  state_assigns: Dict


class KtlApplyOutcome(TypedDict):
  kind: str
  name: str
  verb: str


class UpdateOutcome(TypedDict):
  update_id: str
  type: str
  version: str
  pre_man_vars: Dict
  post_man_vars: Dict
  apply_logs: List[str]
  hook_outcomes: List[ActionOutcome]
