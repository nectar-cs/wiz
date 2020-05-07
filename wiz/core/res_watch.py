from typing import Callable, Optional, List

from k8_kat.res.config_map.kat_map import KatMap
from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.res.ns.kat_ns import KatNs
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.res.pvc.kat_pvc import KatPvc
from k8_kat.res.sa.kat_service_account import KatServiceAccount
from k8_kat.res.secret.kat_secret import KatSecret
from k8_kat.res.svc.kat_svc import KatSvc

kat_classes = [
  KatNs, KatServiceAccount, KatPod, KatSvc,
  KatDep, KatPvc, KatSecret, KatMap
]

class Decorator:
  def __init__(self, res_instance):
    self.res_instance = res_instance

  @property
  def kat_inst(self):
    return


def target_res_kinds() -> List[str]:
  return ['Deployment', 'ConfigMap']


def ns_kat_res_adapter(res_name) -> Optional[Callable]:
  matches = [k for k in kat_classes if k.kind == res_name]
  return matches[0] if len(matches) else None


# def glob(kinds: List[str], decorators: List):


