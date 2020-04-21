from wiz.core.wiz_globals import wiz_globals


class WizModel:

  def __init__(self, config):
    self.config = config

  @classmethod
  def inflate(cls, key, config=None):
    if not config:
      config = wiz_globals.find_config(cls.type_key(), key)

    subclass = wiz_globals.find_subclass(cls.type_key(), key)
    host_class = subclass or cls
    return host_class(config)

  @classmethod
  def inflate_all(cls):
    keys = [c['key'] for c in wiz_globals.configs['concerns']]
    return [cls.inflate(key) for key in keys]

  @classmethod
  def type_key(cls):
    return f'{cls.__name__.lower()}s'
