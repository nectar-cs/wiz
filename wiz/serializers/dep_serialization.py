from typing import Optional

from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.utils.main import units


def pct(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
  divisible = numerator is not None and denominator
  return (numerator / denominator) * 100.0 if divisible else None


def for_homepage(dep: KatDep):
  replica_status = f"{dep.ready_replicas}/{dep.desired_replicas}"


  x = units.humanize_mem_quant(dep.memory_usage())

  return dict(
    name=dep.name,
    replica_status=replica_status,
    cpu_pct=pct(dep.cpu_usage(), dep.cpu_limits()),
    mem_pct=pct(dep.memory_usage(), dep.memory_limits()),

  )
