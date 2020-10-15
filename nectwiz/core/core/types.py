from typing import Optional, Dict, List, Union

from typing_extensions import TypedDict


class ProgressItem(TypedDict, total=False):
  id: Optional[str]
  title: str
  info: Optional[str]
  status: str
  sub_items: List['ProgressItem']
  data: Dict
  error: Dict
  error_id: str
  logs: List[str]


class UpdateDict(TypedDict):
  id: str
  type: str
  version: str
  tam_type: Optional[str]
  tam_uri: Optional[str]
  note: str
  injections: Dict[str, str]
  manual: bool


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
  tone: str


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


class TamDict(TypedDict, total=False):
  type: str
  uri: str
  args: Optional[List[str]]
  version: str


class ActionOutcome(TypedDict):
  cls_name: str
  id: str
  charge: str
  data: Dict


class StepActionKwargs(TypedDict):
  inline_assigns: Dict
  chart_assigns: Dict
  state_assigns: Dict


class KAO(TypedDict):
  api_group: Optional[str]
  kind: str
  name: str
  verb: Optional[str]
  error: Optional[str]


class ErrDict(TypedDict, total=False):
  uuid: str
  event_type: str
  resource: Dict


KAOs = List[KAO]
KoD = Union[str, dict]
