from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.stage.stage import Stage
from nectwiz.tests.models.test_wiz_model import Base


class TestStage(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Stage

  def test_first_step_key(self):
    stage = Stage({'id': 'k', 'steps': ['s2', 's1']})
    actual = stage.first_step_key()
    self.assertEqual(actual, 's2')

  def test_next_step_key_implied(self):
    stage = Stage({'id': 'k', 'steps': [
      {'id': 's1'}, {'id': 's2'}
    ]})

    s1 = stage.step('s1')
    self.assertEqual('s2', stage.next_step_id(s1, {}))

  def test_next_step_key_explicit(self):
    stage = Stage({'id': 'k', 'steps': [
      {'id': 's1', 'next': 's3'}, {'id': 's2'}, {'id': 's3'}
    ]})

    s1 = stage.step('s1')
    self.assertEqual('s3', stage.next_step_id(s1, {}))

