from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.stage.stage import Stage
from nectwiz.tests.models.test_wiz_model import Base


class TestStage(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Stage

  def test_first_step_key(self):
    stage = Stage(dict(
      id='k',
      steps=['s2', 's1']
    ))
    actual = stage.first_step_key()
    self.assertEqual(actual, 's2')

  def test_next_step_key_implied(self):
    stage = Stage(dict(
      steps=[
        dict(id='s1'),
        dict(id='s2')
      ]
    ))

    op_state = OperationState('', '')
    s1 = stage.step('s1')
    self.assertEqual('s2', stage.next_step_id(s1, op_state))

  def test_next_step_key_explicit(self):
    stage = Stage(dict(
      id='k',
      steps=[
        dict(id='s1', next='s3'),
        dict(id='s2'),
        dict(id='s3')
      ]
    ))

    op_state = OperationState('', '')
    s1 = stage.step('s1')
    self.assertEqual('s3', stage.next_step_id(s1, op_state))
