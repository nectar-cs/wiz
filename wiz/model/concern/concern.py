from wiz.core.wiz_globals import wiz_globals
from wiz.model.step.step import Step


class Concern:

  def __init__(self, config):
    self.config = config
    self.key = config['key']
    self.title = config['title']
    self.description = config['description']

  def meta(self):
    keys = ['key', 'name', 'description']
    return {k: self.__dict__[k] for k in keys}

  def first_step_key(self) -> str:
    return self.config['steps'][0]

  def step(self, key) -> Step:
    step_key = [s for s in self.config['steps'] if s == key][0]
    step_config = wiz_globals.step_config(step_key)
    return Step.inflate(step_config)

  @classmethod
  def inflate(cls, key):
    custom_subclass = wiz_globals.concern_class(key)
    host_class = custom_subclass or cls
    config = [c for c in wiz_globals.tree if c['key']][0]
    return host_class(config)

  @classmethod
  def all(cls):
    keys = [c['key'] for c in wiz_globals.concern_configs]
    return [cls.inflate(key) for key in keys]