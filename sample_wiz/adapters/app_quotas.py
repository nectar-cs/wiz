from k8_kat.res.quotas.kat_quota import KatQuota

from wiz.core.wiz_app import wiz_app
from wiz.model.adapters.base_quotas_adapter import BaseQuotasAdapter


class AppQuotasAdapter(BaseQuotasAdapter):

  def find_kat_quota_resource(self) -> KatQuota:
    return KatQuota.find('application-quotas', wiz_app.ns)
