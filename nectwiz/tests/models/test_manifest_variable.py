from typing import Type

from k8kat.utils.testing import ns_factory

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.variable.manifest_variable import ManifestVariable
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers import helper


class TestManifestVariable(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ManifestVariable

  def setUp(self) -> None:
    super().setUp()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)

  def test_read_crt_value(self):
    helper.foo_bar_setup(self.ns)
    cv1 = ManifestVariable(dict(id='foo'))
    self.assertEqual('bar', cv1.current_value(True))

    cv2 = ManifestVariable(dict(id='bar.foo'))
    self.assertEqual('baz', cv2.current_value(True))

    cv3 = ManifestVariable(dict(id='missing'))
    self.assertIsNone(cv3.current_value(True))
