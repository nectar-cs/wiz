from k8_kat.res.quotas.kat_quota import KatQuota
from k8_kat.utils.main import units

from wiz.core.wiz_globals import wiz_app
from wiz.model.adapters.adapter import Adapter


class BaseQuotasAdapter(Adapter):

  def __init__(self):
    super().__init__()
    self.kat_quota = self.find_kat_quota_resource()

  def find_kat_quota_resource(self) -> KatQuota:
    matches = KatQuota.list(wiz_app.ns)
    return matches[0] if len(matches) > 0 else None

  def cpu_limit(self):
    value = self.kat_quota.cpu_limit()
    return units.humanize_cpu_quant(value, True) if value else None

  def cpu_used(self):
    value = self.kat_quota.cpu_used()
    return units.humanize_cpu_quant(value, True) if value else None

  def mem_limit(self):
    value = self.kat_quota.mem_limit()
    return units.humanize_mem_quant(value) if value else None

  def mem_used(self):
    value = self.kat_quota.mem_used()
    return units.humanize_mem_quant(value) if value else None

  def serialize(self, **kwargs):
    if self.kat_quota:
      return dict(
        cpu_limit=self.cpu_limit(),
        cpu_used=self.cpu_used(),
        mem_limit=self.mem_limit(),
        mem_used=self.mem_used()
      )
    else:
      return None
