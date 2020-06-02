from typing import List

from k8_kat.res.ingress.kat_ingress import KatIngress
from k8_kat.res.svc.kat_svc import KatSvc

from wiz.core import utils
from wiz.core.wiz_globals import wiz_app
from wiz.model.adapters.access_adapter import AppEndpointAdapter
from wiz.model.adapters.provider import Provider
from wiz.model.field.field import Field
from wiz.model.step.step import Step


class HomepageAdapter(AppEndpointAdapter):
  def name(self):
    return "Homepage"

  def url(self):
    ingress = KatIngress.find('hub-ingress', wiz_app.ns)
    host, host_info = list(ingress.basic_rules().items())[0]
    info = [b for b in host_info if b['service'] == 'hub-front'][0]
    path = '' if info['path'] == '/' else info['path']
    return f"{host}{path}"


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


class AppEndpointsProvider(Provider):
  def list(self) -> List[AppEndpointAdapter]:
    return [
      AppEndpointAdapter(),
      HomepageInternalAdapter(),
      AdminPageAdapter()
    ]


class DbPasswordField(Field):
  @classmethod
  def key(cls):
    return 'hub.storage.secrets.password'

  @classmethod
  def type_key(cls):
    return Field.type_key()

  def default_value(self):
    return utils.rand_str(string_len=20)


class SecKeyBaseField(Field):
  @classmethod
  def key(cls):
    return 'hub.backend.secrets.key_base'

  @classmethod
  def type_key(cls):
    return Field.type_key()

  def default_value(self):
    return utils.rand_str(string_len=24)


class AttrEncField(Field):
  @classmethod
  def key(cls):
    return 'hub.backend.secrets.attr_enc_key'

  def default_value(self):
    return utils.rand_str(string_len=32)


class AvailabilityStep(Step):

  @classmethod
  def key(cls):
    return "availability"

  @classmethod
  def type_key(cls):
    return Step.type_key()

  @staticmethod
  def str_num_to_i(str_rep):
    if str_rep == 'small':
      return 1
    return 3 if str_rep == 'high' else 2

  def field_to_manifest_values(self, values):
    exp_users_i = self.str_num_to_i(values['hub.backend.num_users'])
    req_downtime_i = self.str_num_to_i(values['hub.backend.response_time'])
    num_rep = exp_users_i + req_downtime_i
    return {
      "hub.backend.replicas": (num_rep - num_rep) + 1,
      "hub.frontend.replicas": (num_rep - num_rep) + 1
    }


class LocateExternalDatabaseStep(Step):

  @classmethod
  def key(cls):
    return "locate_external_db"

  @classmethod
  def type_key(cls):
    return Step.type_key()

  @staticmethod
  def can_connect(**connection_props):
    return False

  def commit(self, values):
    if self.can_connect(**values):
      return super().commit(values)
    else:
      return "negative", "Connection to the database failed"

