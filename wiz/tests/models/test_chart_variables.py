from typing import Type

from k8_kat.utils.testing import ns_factory

from wiz.core.wiz_globals import wiz_app
from wiz.model.base.wiz_model import WizModel
from wiz.model.chart_variable.chart_variable import ChartVariable
from wiz.tests.models.test_wiz_model import Base
from wiz.tests.t_helpers import helper


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
    self.assertEqual('bar', cv1.read_crt_value())

    cv2 = ChartVariable(dict(key='bar.foo'))
    self.assertEqual('baz', cv2.read_crt_value())

    cv3 = ChartVariable(dict(key='missing'))
    self.assertIsNone(cv3.read_crt_value())

  def test_read_crt_value_cache(self):
    cv1 = ChartVariable(dict(key='foo'))
    self.assertEqual('rab', cv1.read_crt_value(cache={'foo': 'rab'}))

  def test_commit(self):
    helper.foo_bar_setup(self.ns)
    cv1 = ChartVariable(dict(key='foo'))
    self.assertEqual('bar', cv1.read_crt_value())

    cv1.commit('baz')
    self.assertEqual('baz', cv1.read_crt_value())
