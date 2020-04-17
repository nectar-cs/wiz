import abc
from typing import Dict

import functools

from wiz.core.resolve import find_concern_class
from wiz.core.wiz_globals import wiz_globals
from wiz.model.concern import Concern


class Wizard:
  __metaclass__ = abc.ABCMeta

  def __init__(self):
    self._concerns = []

  @property
  @functools.lru_cache()
  def concerns(self) -> [Concern]:
    dicts = wiz_globals.concerns_base
    trans = lambda d: find_concern_class(d.key, Concern)(d)
    return [trans(sub_tree) for sub_tree in dicts]

  def concern(self, key):
    found = [c for c in self.concerns if c.key == key]
    if len(found) == 1:
      return found[0]
    else:
      return f"Found {len(found)} concerns for {key} instead of 1!"

