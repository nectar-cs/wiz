from functools import lru_cache

from k8kat.res.quotas.kat_quota import KatQuota

from k8kat.res.ns.kat_ns import KatNs
from k8kat.res.cluster.kat_cluster import KatCluster

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel


class ResourceConsumptionAdapter(WizModel):

  @lru_cache(maxsize=1)
  def kat_ns(self) -> KatNs:
    return KatNs.find(config_man.ns())

  @lru_cache(maxsize=1)
  def resources_capacity(self):
    return KatCluster.resources_available()

  @lru_cache(maxsize=1)
  def kat_quota(self) -> KatQuota:
    matches = KatQuota.list(ns=config_man.ns())
    return matches[len(matches) - 1] if len(matches) > 0 else None

  def permitted_cpu_request_sum(self):
    return self.kat_quota().cpu_request_sum_allowed()

  def cpu_requested_sum(self):
    return self.kat_quota().cpu_request_sum_deployed()

  def permitted_mem_request_sum(self):
    return self.kat_quota().mem_request_sum_allowed()

  def mem_requested_sum(self):
    return self.kat_quota().mem_request_sum_deployed()

  def permitted_cpu_limit_sum(self):
    return self.kat_quota().cpu_limit_sum_allowed()

  def permitted_mem_limit_sum(self):
    return self.kat_quota().mem_limit_sum_allowed()

  def cpu_used(self):
    return self.kat_ns().cpu_used()

  def mem_used(self):
    return self.kat_ns().mem_used()

  def serialize(self):
    return dict(
      cpu=dict(
        request_sum_allowed=self.permitted_cpu_request_sum(),
        request_sum_deployed=self.cpu_requested_sum(),
        limit_sum_allowed=self.permitted_cpu_limit_sum(),
        used=self.cpu_used(),
      ),
      mem=dict(
        request_sum_allowed=self.permitted_mem_request_sum(),
        request_sum_deployed=self.mem_requested_sum(),
        limit_sum_allowed=self.permitted_mem_limit_sum(),
        used=self.mem_used(),
      )
    )
