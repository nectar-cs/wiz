from k8_kat.res.quotas.kat_quota import KatQuota

from k8_kat.res.ns.kat_ns import KatNs
from werkzeug.utils import cached_property


from k8_kat.res.cluster.kat_cluster import KatCluster
from wiz.core.wiz_globals import wiz_app
from wiz.model.adapters.adapter import Adapter


class BaseConsumptionAdapter(Adapter):

  @cached_property
  def kat_ns(self) -> KatNs:
    return KatNs.find(wiz_app.ns)

  @cached_property
  def resources_capacity(self):
    return KatCluster.resources_available()

  @cached_property
  def kat_quota(self) -> KatQuota:
    matches = KatQuota.list(ns=wiz_app.ns)
    return matches[len(matches) - 1] if len(matches) > 0 else None

  def cpu_request_sum_allowed(self):
    return self.kat_quota.cpu_request_sum_allowed()

  def cpu_request_sum_deployed(self):
    return self.kat_quota.cpu_request_sum_deployed()

  def mem_request_sum_allowed(self):
    return self.kat_quota.mem_request_sum_allowed()

  def mem_request_sum_deployed(self):
    return self.kat_quota.mem_request_sum_deployed()

  def cpu_limit_sum_allowed(self):
    return self.kat_quota.cpu_limit_sum_allowed()

  def mem_limit_sum_allowed(self):
    return self.kat_quota.mem_limit_sum_allowed()

  def cpu_used(self):
    return self.kat_ns.cpu_used()

  def mem_used(self):
    return self.kat_ns.mem_used()

  def serialize(self, **kwargs):
    return dict(
      cpu=dict(
        request_sum_allowed=self.cpu_request_sum_allowed(),
        request_sum_deployed=self.cpu_request_sum_deployed(),
        limit_sum_allowed=self.cpu_limit_sum_allowed(),
        used=self.cpu_used(),
      ),
      mem=dict(
        request_sum_allowed=self.mem_request_sum_allowed(),
        request_sum_deployed=self.mem_request_sum_deployed(),
        limit_sum_allowed=self.mem_limit_sum_allowed(),
        used=self.mem_used(),
      ),
    )
