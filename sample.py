from random import random
from typing import Dict

import dotenv
import yaml

from wiz.core import utils
from wiz.core.wiz_globals import wiz_globals
from wiz import server
from wiz.model.field.field import Field
from wiz.model.step.step import Step


class DbPasswordField(Field):
  @classmethod
  def key(cls):
    return 'hub.storage.db_password'

  def default_value(self):
    return utils.rand_str(string_len=20)


class LocateExternalDatabaseStep(Step):

  @classmethod
  def key(cls):
    return "locate_external_db"

  # noinspection PyUnusedLocal
  @staticmethod
  def can_connect(**connection_props):
    return False

  def commit(self, values):
    if self.can_connect(**values):
      return super().commit(values)
    else:
      return "negative", "Connection to the database failed"


def load_yaml_array(fname) -> [Dict]:
  file_contents = open(fname, 'r').read()
  return yaml.load(file_contents, Loader=yaml.FullLoader)

wiz_globals.set_configs(
  concerns=load_yaml_array('example/concerns.yaml'),
  steps=load_yaml_array('example/steps.yaml'),
  fields=load_yaml_array('example/fields.yaml'),
)

wiz_globals.set_subclasses(
  concerns=[],
  steps=[
    LocateExternalDatabaseStep
  ],
  fields=[
    DbPasswordField
  ]
)

dotenv.load_dotenv()
server.start()
