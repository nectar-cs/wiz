from wiz.core import utils
from wiz.model.field.field import Field


class DbPasswordField(Field):
  @classmethod
  def key(cls):
    return 'hub.storage.secrets.password'

  def default_value(self):
    return utils.rand_str(string_len=20)


class SecKeyBaseField(Field):
  @classmethod
  def key(cls):
    return 'hub.backend.secrets.key_base'

  def default_value(self):
    return utils.rand_str(string_len=24)


class AttrEncField(Field):
  @classmethod
  def key(cls):
    return 'hub.backend.secrets.attr_enc_key'

  def default_value(self):
    return utils.rand_str(string_len=32)


class CPUQuotaField(Field):
  @classmethod
  def key(cls):
    return 'hub.quotas.cpu'

  def decorate_value(self, value):
    people = int(value) * 75
    return f"{value}", f"Team of ~{people}"


class MemQuotaField(Field):
  @classmethod
  def key(cls):
    return 'hub.quotas.memory'

  def decorate_value(self, value):
    people = int(value) * 65
    return f"{value} Gb", f"Team of ~{people}"

  def clean_value(self, value):
    return value / 1_000_000
