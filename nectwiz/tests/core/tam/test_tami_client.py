from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.tami_client import TamiClient
from nectwiz.core.wiz_app import wiz_app
from nectwiz.tests.core.tam.test_tam_super import Base


class TestTamiClient(Base.TestTamSuper):

  def setUp(self) -> None:
    super().setUp()
    wiz_app._tam = dict(
      type='image',
      uri='gcr.io/nectar-bazaar/wiz-ci-tami:latest',
      args=None
    )

  def client_instance(self) -> TamClient:
    return TamiClient()
