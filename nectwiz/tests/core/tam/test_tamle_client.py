from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.local_exec_tam_client import LocalExecTamClient
from nectwiz.core.tam.http_api_tam_client import HttpApiTamClient
from nectwiz.tests.core.tam.test_tam_super import Base
from nectwiz.tests.t_helpers.helper import ci_tams_name, ci_tamle_name


class TestTamleClient(Base.TestTamSuper):

  def client_instance(self) -> TamClient:
    return LocalExecTamClient(tam=dict(
      type='local_executable',
      uri=ci_tamle_name(),
      version='1.0.0'
    ))
