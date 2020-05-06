from typing import Dict

import dotenv
import yaml

from wiz.core.wiz_globals import wiz_globals
from wiz import server



def load_yaml_array(fname) -> [Dict]:
  file_contents = open(fname, 'r').read()
  return yaml.load(file_contents, Loader=yaml.FullLoader)

wiz_globals.set_configs(
  concerns=load_yaml_array('example/concerns.yaml'),
  steps=load_yaml_array('example/steps.yaml'),
  fields=load_yaml_array('example/fields.yaml'),
)

dotenv.load_dotenv()

server.start()
