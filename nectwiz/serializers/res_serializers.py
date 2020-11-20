from typing import Dict

from k8kat.res.config_map.kat_map import KatMap
from k8kat.res.rbac.rbac import KatRole

from k8kat.res.quotas.kat_quota import KatQuota

from k8kat.res.pod.kat_pod import KatPod

from k8kat.res.dep.kat_dep import KatDep

from k8kat.res.base.kat_res import KatRes

from nectwiz.model.adapters.res_intel_adapter import ResIntelProvider


def basic(res: KatRes) -> Dict:
  return dict(
    kind=res.res_name_plural,
    name=res.name,
    status=res.ternary_status()
  )

def intel(res: KatRes) -> Dict:
  provider_candidates = ResIntelProvider.covering_res(res)
  intel_items = []
  if len(provider_candidates) > 0:
    provider = provider_candidates[0]
    if len(provider_candidates) > 1:
      message = f"warn {len(provider_candidates)} providers for {res}"
      print(f"[nectwiz:res_serializers] {message}")
    intel_items = provider.generate_intel(res)
  return dict(intel=intel_items)


def _embedded_pod(pod: KatPod) -> Dict:
  return dict(
    **basic(pod),
    phase=pod.phase,
    cpu=dict(
      used=pod.cpu_used(),
      requested=pod.cpu_request(),
      limit=pod.cpu_limit()
    ),
    mem=dict(
      used=pod.mem_used(),
      requested=pod.mem_request(),
      limit=pod.mem_limit()
    )
  )


def config_map(cmap: KatMap) -> Dict:
  return dict(
    **basic(cmap),
    **intel(cmap),
    data=cmap.data
  )


def deployment(dep: KatDep) -> Dict:
  return dict(
    **basic(dep),
    **intel(dep),
    desc=dep.short_desc(),
    cpu=dict(
      requested=dep.pods_cpu_request(),
      limit=dep.pods_cpu_limit(),
      used=dep.cpu_used(),
    ),
    mem=dict(
      requested=dep.pods_mem_request(),
      limit=dep.pods_mem_limit(),
      used=dep.mem_used(),
    ),
    pods=[_embedded_pod(p) for p in dep.pods()]
  )


def resource_quota(quota: KatQuota) -> Dict:
  return dict(
    **basic(quota),
    **intel(quota),
    features=quota.dump()
  )


def role(k_role: KatRole):
  return dict(
    **basic(k_role),
    **intel(k_role),
    matrix=k_role.matrix_form()
  )
