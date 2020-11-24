from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.tamle_client import TamleClient
from nectwiz.core.tam.tams_client import TamsClient
from nectwiz.tests.core.tam.test_tam_super import Base
from nectwiz.tests.t_helpers.helper import ci_tams_name, ci_tamle_name


class TestTamleClient(Base.TestTamSuper):

  def client_instance(self) -> TamClient:
    return TamleClient(tam=dict(
      type='local_executable',
      uri=ci_tamle_name(),
      version='1.0.0'
    ))
