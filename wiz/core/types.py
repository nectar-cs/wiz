from typing_extensions import TypedDict


class K8sResMeta(TypedDict):
  namespace: str
  name: str

class K8sRes(TypedDict):
  kind: str
  metadata: K8sResMeta
