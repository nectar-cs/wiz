from typing import Type

from wiz.model.base.wiz_model import WizModel
from wiz.model.operations.operation import Operation
from wiz.tests.models.test_wiz_model import Base


class TestOperation(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Operation



  # def test_first_step_key(self):
  #   wg.add_configs(operations=[g_con_conf(k='k', s=['s2', 's1'])])
  #   actual = Operation.inflate('k').first_step_key()
  #   self.assertEqual(actual, 's2')
  #
  # def test_step(self):
  #   wg.add_configs(
  #     operations=[g_con_conf(k='c1', s=['s1', 's2'])],
  #     steps=[g_conf(k='s1', t='foo')]
  #   )
  #
  #   c1 = Operation.inflate('c1')
  #   s1 = c1.step('s1')
  #   self.assertEqual(s1.key, 's1')
  #   self.assertEqual(s1.title, 'foo')

