from k8_kat.res.pod.kat_pod import KatPod

from k8_kat.res.dep.kat_dep import KatDep

from k8_kat.res.base.kat_res import KatRes


def basic(res: KatRes):
  return dict(
    kind=res.kind,
    name=res.name,
    status=res.ternary_status()
  )


def _embedded_pod(pod: KatPod):
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


def deployment(dep: KatDep):
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



