import traceback
from typing import List, Optional

from k8kat.res.svc.kat_svc import KatSvc
from typing_extensions import TypedDict
from werkzeug.utils import cached_property

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel


class AccessPointDict(TypedDict):
  name: str
  url: Optional[str]
  type: str


class AccessPointAdapter(WizModel):

  RESOURCE_KEY = 'selector'
  TYPE_KEY = 'type'
  URL_KEY = 'url'
  PORT_KEY = 'port'

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
      print(f"MATCHES {matches}")
      res = next(iter(matches), None)
      if res:
        print("WINNER")
        print(res.kind)
        print(res.name)
      if res and isinstance(res, KatSvc):
        return res
    return None

  @cached_property
  def access_point_type(self) -> Optional[str]:
    return self.get_prop(self.TYPE_KEY) or self.infer_type()

  @cached_property
  def url(self) -> Optional[str]:
    explicit = self.get_prop(self.URL_KEY)
    print(f"{self.title} EXPLICIT URL {explicit}")
    print(f"INDERRED {self.infer_url()}")
    return explicit or self.infer_url()

  @cached_property
  def port(self) -> Optional[str]:
    return self.get_prop(self.PORT_KEY) or self.infer_port()

  def _resolve(self) -> Optional[AccessPointDict]:
    port_part = f":{self.port}" if self.port else ''
    return AccessPointDict(
      name=self.title,
      url=f"{self.url}{port_part}",
      type=self.access_point_type
    )

  def resolve(self) -> Optional[AccessPointDict]:
    # noinspection PyBroadException
    try:
      return self._resolve()
    except:
      print(traceback.format_exc())
      print(f"[nectwiz:endpoints_adapter] AP resolve failed ^^")
      return None

  def infer_type(self) -> Optional[str]:
    if self.underlying_svc:
      is_external = bool(self.underlying_svc.external_ip)
      prefix = "external" if is_external else "internal"
      return f"{prefix}-url"
    return None

  def infer_url(self):
    print("INFER TIME")
    print(self.underlying_svc)
    if self.underlying_svc:
      val = self.underlying_svc.external_ip or \
             self.underlying_svc.internal_ip
      print(f"INFERRED {val}")
      return val
    return None

  def infer_port(self) -> str:
    if self.underlying_svc:
      value = str(self.underlying_svc.first_tcp_port_num())
      return value if not value == '80' else ''


class AccessPointsProvider(WizModel):

  ADAPTERS_KEY = 'adapters'

  @classmethod
  def singleton_id(cls):
    return 'nectar.access-points-provider'

  @cached_property
  def adapters(self):
    return self.inflate_children(
      AccessPointAdapter,
      prop=self.ADAPTERS_KEY
    )

  def serialize_access_points(self) -> List[AccessPointDict]:
    results = list(map(AccessPointAdapter.resolve, self.adapters))
    judge = lambda s: s and None not in s.values()
    return list(filter(judge, results))
