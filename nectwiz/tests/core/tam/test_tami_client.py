from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.tami_client import TamiClient, image_name
from nectwiz.tests.core.tam.test_tam_super import Base
from nectwiz.tests.t_helpers.helper import ci_tami_name


class TestTamiClient(Base.TestTamSuper):

  def client_instance(self) -> TamClient:
    return TamiClient(tam=dict(
      type='image',
      uri=ci_tami_name(),
      version='1.0.0'
    ))

  def test_load_manifest_defaults(self):
    pass

  # def test_load_tpd_manifest(self):
  #   pass

  def test_image_name(self):
    actual = image_name(dict(uri='foo/bar', version=None))
    self.assertEqual('foo/bar:latest', actual)

    actual = image_name(dict(uri='foo/bar'))
    self.assertEqual('foo/bar:latest', actual)

    actual = image_name(dict(uri='foo/bar', version='1.0'))
    self.assertEqual('foo/bar:1.0', actual)

    actual = image_name(dict(uri='foo/bar:1.0', version='2.0'))
    self.assertEqual('foo/bar:2.0', actual)

    actual = image_name(dict(uri='foo/bar:3.0', version=None))
    self.assertEqual('foo/bar:3.0', actual)

    actual = image_name(dict(uri='foo/bar:3.0'))
    self.assertEqual('foo/bar:3.0', actual)
