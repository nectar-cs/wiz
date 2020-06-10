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

  def default_value(self):
    return utils.rand_str(string_len=32)

