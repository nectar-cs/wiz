from k8kat.res.quotas.kat_quota import KatQuota

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel


class ResQuotasAdapter(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.kat_quota = self.find_kat_quota_resource()

  def find_kat_quota_resource(self) -> KatQuota:
    matches = KatQuota.list(config_man.ns())
    return matches[len(matches) - 1] if len(matches) > 0 else None

  def cpu_limit(self):
    # return self.kat_quota.mem_limit_cap()
    pass

  def cpu_used(self):
    return self.kat_quota.cpu_used()

  def mem_limit(self):
    # value = self.kat_quota.mem_limit()
    # return value / 10**9 if value is not None else None
    pass

  def mem_used(self):
    value = self.kat_quota.mem_used()
    return value / 10**9 if value is not None else None

  def serialize(self):
    if self.kat_quota:
      return dict(
        cpu_limit=self.cpu_limit(),
        cpu_used=self.cpu_used(),
        cpu_unit='Cores',
        mem_limit=self.mem_limit(),
        mem_used=self.mem_used(),
        mem_unit='Gb'
      )
    else:
      return None
