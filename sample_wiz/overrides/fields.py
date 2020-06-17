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


class CPUQuotaField(Field):
  @classmethod
  def key(cls):
    return 'hub.quotas.cpu'

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
  def key(cls):
    return 'hub.quotas.memory'

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
