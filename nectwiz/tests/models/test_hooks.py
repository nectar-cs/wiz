from typing import List, Type

from nectwiz.model.base.wiz_model import models_man, WizModel
from nectwiz.model.hook.hook import Hook
from nectwiz.tests.models.test_wiz_model import Base


class TestHooks(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Hook

  def test_by_trigger(self):
    models_man.clear(restore_defaults=True)
    models_man.add_descriptors([
      dict(
        id='h1',
        kind='Hook',
        trigger_selector=dict(foo='bar')
      ),
      dict(
        id='h2',
        kind='Hook',
        trigger_selector=dict(foo='baz', bar='baz'),
      ),
      dict(
        id='h3',
        kind='Hook',
        trigger_selector=dict(foo='bar', bar='baz'),
      ),
      dict(
        id='h4',
        kind='Hook',
        trigger_selector=dict()
      ),
      dict(
        id='h5',
        kind='Hook',
        trigger_selector=None
      ),
      dict(
        id='h6',
        kind='Hook'
      )
    ])

    self.assertEqual(['h1'], ids(Hook.by_trigger(foo='bar')))
    self.assertEqual(['h1'], ids(Hook.by_trigger(foo='bar', x='y')))
    self.assertEqual(['h1', 'h3'], ids(Hook.by_trigger(foo='bar', bar='baz')))


def ids(models) -> List[str]:
  return [model.id() for model in models]
