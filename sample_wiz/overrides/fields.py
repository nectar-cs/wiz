from typing import Dict

from wiz.core import utils
from wiz.model.field.field import Field


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

  @classmethod
  def type_key(cls):
    return Field.type_key()

  def default_value(self):
    return utils.rand_str(string_len=32)


class CpuQuotaField(Field):
  @classmethod
  def type_key(cls):
    return Field.type_key()

  def decorate_value(self, value: str) -> Dict:
    people = int(float(value) * 75)
    return dict(
      value=f"{value} Cores",
      hint=f"Team of ~{people}"
    )


class MemQuotaField(Field):
  @classmethod
  def type_key(cls):
    return Field.type_key()

  def decorate_value(self, value: str) -> Dict:
    people = int(float(value) * 65)
    return dict(
      value=f"{value} Gb",
      hint=f"Team of ~{people}"
    )

  def sanitize_value(self, value):
    return f"{value}G"


class CPURequestsQuotaField(CpuQuotaField):
  @classmethod
  def key(cls):
    return 'hub.quotas.requests.cpu'


class CPULimitsQuotaField(CpuQuotaField):
  @classmethod
  def key(cls):
    return 'hub.quotas.limits.cpu'


class MemRequestsQuotaField(MemQuotaField):
  @classmethod
  def key(cls):
    return 'hub.quotas.requests.memory'


class MemLimitsQuotaField(MemQuotaField):
  @classmethod
  def key(cls):
    return 'hub.quotas.limits.memory'

