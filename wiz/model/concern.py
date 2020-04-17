import os
from typing import Dict

import inflection
import yaml

from wiz.core.resolve import find_step_class
from wiz.model.step import Step


class Concern:

  def __init__(self, config):
    self.config = config
    self.key = config.get('key')
    self.name = config.get('name')
    self.description = config.get('description')
    # self._step_keys = config.

  def meta(self):
    keys = ['key', 'name', 'description']
    return {k: self.__dict__[k] for k in keys}

  def steps(self):
    dicts = self.config.get('steps', [])
    trans = lambda d: find_step_class(d.key, Step)(d)
    return [trans(sub_tree) for sub_tree in dicts]



# def first_step(self):


