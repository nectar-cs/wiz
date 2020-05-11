from typing_extensions import TypedDict


class K8sResMeta(TypedDict):
  namespace: str
  name: str

class K8sResDict(TypedDict):
  kind: str
  metadata: K8sResMeta
