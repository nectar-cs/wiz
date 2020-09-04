from typing import Type

from k8kat.utils.testing import ns_factory

from nectwiz.core.wiz_app import wiz_app
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.chart_variable.chart_variable import ChartVariable
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers import helper


class TestChartVariables(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ChartVariable

  def setUp(self) -> None:
    super().setUp()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)

  def test_read_crt_value(self):
    helper.foo_bar_setup(self.ns)
    cv1 = ChartVariable(dict(key='foo'))
    self.assertEqual('bar', cv1.read_crt_value(True))

    cv2 = ChartVariable(dict(key='bar.foo'))
    self.assertEqual('baz', cv2.read_crt_value(True))

    cv3 = ChartVariable(dict(key='missing'))
    self.assertIsNone(cv3.read_crt_value(True))

  def test_commit(self):
    helper.foo_bar_setup(self.ns)
    cv1 = ChartVariable(dict(key='foo'))
    self.assertEqual('bar', cv1.read_crt_value(True))

    cv1.commit('baz')
    self.assertEqual('baz', cv1.read_crt_value(True))
