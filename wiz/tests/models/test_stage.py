from typing import Type

from wiz.core.wiz_app import wiz_app
from wiz.model.base.wiz_model import WizModel
from wiz.model.stage.stage import Stage
from wiz.model.step.step import Step
from wiz.tests.models.helpers import g_conf
from wiz.tests.models.test_wiz_model import Base


class TestStage(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Stage

  def test_first_step_key(self):
    stage = Stage(g_conf(k='k', steps=['s2', 's1']))
    actual = stage.first_step_key()
    self.assertEqual(actual, 's2')

  def test_step(self):
    wiz_app.add_configs([
      g_conf(k='c1', steps=['s1', 's2'], i=Stage.type_key()),
      g_conf(k='s1', t='foo', i=Step.type_key())
    ])

    c1 = Stage.inflate('c1')
    s1 = c1.step('s1')
    self.assertEqual(s1.key, 's1')
    self.assertEqual(s1.title, 'foo')
