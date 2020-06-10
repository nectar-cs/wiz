from typing import List, TypeVar

from k8_kat.res.ingress.kat_ingress import KatIngress
from k8_kat.res.svc.kat_svc import KatSvc

from wiz.core.wiz_globals import wiz_app
from wiz.model.adapters.app_endpoint_adapter import AppEndpointAdapter
from wiz.model.adapters.provider import Provider



class HomepageAdapter(AppEndpointAdapter):
  def name(self):
    return "Homepage"

  def url(self):
    return "wosy.asdas"
    # ingress = KatIngress.find('hub-ingress', wiz_app.ns)
    # host, host_info = list(ingress.basic_rules().items())[0]
    # info = [b for b in host_info if b['service'] == 'hub-front'][0]
    # path = '' if info['path'] == '/' else info['path']
    # return f"{host}{path}"


class HomepageInternalAdapter(AppEndpointAdapter):
  def name(self):
    return "Homepage internal"

  def url(self):
    svc = KatSvc.find('hub-front', wiz_app.ns)
    return f"{svc.internal_ip}:{svc.from_port}"


class AdminPageAdapter(HomepageAdapter):
  def name(self):
    return "Admin Panel"

  def url(self):
    return f"{super().url()}/admin"


class AppEndpointsProvider(Provider[AppEndpointAdapter]):

  @classmethod
  def kind(cls):
    return AppEndpointAdapter

  def produce_adapters(self) -> List[AppEndpointAdapter]:
    return [
      AppEndpointAdapter(),
      HomepageInternalAdapter(),
      AdminPageAdapter()
    ]
