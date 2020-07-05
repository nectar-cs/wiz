from typing import Optional, Dict

from typing_extensions import TypedDict


class CommitOutcome(TypedDict, total=False):
  status: str
  reason: Optional[str]
  assignments: Dict
  job_id: Optional[str]


class K8sResMeta(TypedDict):
  namespace: str
  name: str


class K8sResDict(TypedDict):
  kind: str
  metadata: K8sResMeta
