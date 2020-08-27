from nectwiz.core.tam_config import TamConfig
from nectwiz.core.wiz_app import wiz_app

wiz_app._ns = 3

class DevelopmentTamConfig(TamConfig):
  def type(self):
    return 'local_executable'

  def uri(self) -> str:
    return ''