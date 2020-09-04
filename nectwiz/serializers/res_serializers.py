from typing import Dict

from k8kat.res.rbac.rbac import KatRole

from k8kat.res.quotas.kat_quota import KatQuota

from k8kat.res.pod.kat_pod import KatPod

from k8kat.res.dep.kat_dep import KatDep

from k8kat.res.base.kat_res import KatRes


def basic(res: KatRes) -> Dict:
  return dict(
    kind=res.kind,
    name=res.name,
    status=res.ternary_status()
  )


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


def deployment(dep: KatDep) -> Dict:
  return dict(
    **basic(dep),
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
    features=quota.dump()
  )


def role(k_role: KatRole):
  return dict(
    **basic(k_role),
    matrix=k_role.matrix_form()
  )
