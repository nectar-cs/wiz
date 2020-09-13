from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.tami_client import TamiClient, image_name
from nectwiz.core.core.config_man import config_man
from nectwiz.tests.core.tam.test_tam_super import Base
from nectwiz.tests.t_helpers.helper import ci_tami_name


class TestTamiClient(Base.TestTamSuper):

  def client_instance(self) -> TamClient:
    return TamiClient()

  def setUp(self) -> None:
    super().setUp()
    config_man._tam = dict(
      type='image',
      uri=ci_tami_name(),
      args=None,
      ver='latest'
    )

  def test_image_name(self):
    actual = image_name(dict(uri='foo/bar', ver=None))
    self.assertEqual('foo/bar:latest', actual)

    actual = image_name(dict(uri='foo/bar'))
    self.assertEqual('foo/bar:latest', actual)

    actual = image_name(dict(uri='foo/bar', ver='1.0'))
    self.assertEqual('foo/bar:1.0', actual)

    actual = image_name(dict(uri='foo/bar:1.0', ver='2.0'))
    self.assertEqual('foo/bar:2.0', actual)

    actual = image_name(dict(uri='foo/bar:3.0', ver=None))
    self.assertEqual('foo/bar:3.0', actual)

    actual = image_name(dict(uri='foo/bar:3.0'))
    self.assertEqual('foo/bar:3.0', actual)
