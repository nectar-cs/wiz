from nectwiz.core.tam.tams_client import TamsClient
from nectwiz.tests.core.tam.test_tam_super import Base
from nectwiz.tests.t_helpers.helper import ci_tams_name


class TestTamsClient(Base.TestTamSuper):

  def client_instance(self) -> TamsClient:
    return TamsClient(tam=dict(
      type='server',
      uri=ci_tams_name(),
      version='1.0.0'
    ))
