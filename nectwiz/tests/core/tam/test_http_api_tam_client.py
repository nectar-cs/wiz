from nectwiz.core.tam.http_api_tam_client import HttpApiTamClient
from nectwiz.tests.core.tam.test_tam_super import Base
from nectwiz.tests.t_helpers.helper import ci_tams_name


class TestHttpApiTamClient(Base.TestTamSuper):

  def client_instance(self) -> HttpApiTamClient:
    return HttpApiTamClient(tam=dict(
      type='server',
      uri=ci_tams_name(),
      version='1.0.0'
    ))
