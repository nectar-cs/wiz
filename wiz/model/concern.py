import os
from typing import Dict

import inflection
import yaml

from wiz.model.step import Step


class Concern:

  def next_step(self, crt_step):
    return None

  @classmethod
  def defaults_fname(cls):
    return ''

  @classmethod
  def step(cls, name) -> Step:
    raise NotImplementedError

  @classmethod
  def defaults(cls) -> Dict[str, str]:
    with open(cls.defaults_fname(), 'r') as stream:
      yaml_concerns = yaml.safe_load(stream)['concerns']
      return [d for d in yaml_concerns if d['key'] == cls.key()][0]

  @classmethod
  def key(cls) -> str:
    pre_concern = cls.__name__.split('Concern')[0]
    return inflection.underscore(pre_concern)

  @classmethod
  def friendly_name(cls):
    return cls.defaults()['friendly_name']

  @classmethod
  def description(cls):
    return cls.defaults()['description']

  @classmethod
  def meta(cls):
    return dict(
      key=cls.key(),
      name=cls.friendly_name(),
      description=cls.description()
    )

  pass
