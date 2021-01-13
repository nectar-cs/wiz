from typing import Optional, Any

from k8kat.res.svc.kat_svc import KatSvc
from werkzeug.utils import cached_property

from nectwiz.core.core.types import EndpointDict
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.supply.value_supplier import ValueSupplier


class EndpointSupplier(ValueSupplier):

  RESOURCE_KEY = 'selector'
  TYPE_KEY = 'type'
  URL_KEY = 'url'
  PORT_KEY = 'port'

  def _compute(self) -> Any:
    port_part = f":{self.port}" if self.port else ''
    return EndpointDict(
      name=self.title,
      url=f"{self.url}{port_part}",
      type=self.access_point_type,
      online=self.check_is_online()
    )

  def check_is_online(self):
    return self.underlying_svc is not None

  @cached_property
  def resource_selector(self):
    return self.inflate_child(
      ResourceSelector,
      prop=self.RESOURCE_KEY,
      safely=True
    )

  @cached_property
  def underlying_svc(self) -> Optional[KatSvc]:
    if self.resource_selector:
      matches = self.resource_selector.query_cluster()
      res = next(iter(matches), None)
      if res and isinstance(res, KatSvc):
        return res
    return None

  @cached_property
  def access_point_type(self) -> Optional[str]:
    return self.get_prop(self.TYPE_KEY) or self.infer_type()

  @cached_property
  def url(self) -> Optional[str]:
    explicit = self.get_prop(self.URL_KEY)
    return explicit or self.infer_url()

  @cached_property
  def port(self) -> Optional[str]:
    return self.get_prop(self.PORT_KEY) or self.infer_port()

  def infer_type(self) -> Optional[str]:
    if self.underlying_svc:
      is_external = bool(self.underlying_svc.external_ip)
      prefix = "external" if is_external else "internal"
      return f"{prefix}-url"
    return None

  def infer_url(self) -> Optional[str]:
    if self.underlying_svc:
      return self.underlying_svc.external_ip or \
             self.underlying_svc.internal_ip
    return None

  def infer_port(self) -> str:
    if self.underlying_svc:
      value = str(self.underlying_svc.first_tcp_port_num())
      return value if not value == '80' else ''
