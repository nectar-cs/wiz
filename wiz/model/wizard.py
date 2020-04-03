import abc
from typing import Dict

from wiz.model.concern import Concern


class Wizard:
  __metaclass__ = abc.ABCMeta
  pass

  @classmethod
  def concerns(cls) -> [Concern]:
    return []

  @classmethod
  def concern(cls, key):
    return [c for c in cls.concerns() if c.key() == key][0]

  @classmethod
  def concerns_meta(cls) -> [Dict[str, str]]:
    maker = lambda concern: dict(
      key=1,
      friendly_name=2,
      description=3
    )

    return [maker(concern) for concern in cls.concerns()]