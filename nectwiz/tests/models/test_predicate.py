from typing import Type

from k8kat.auth.kube_broker import broker
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from nectwiz.core.core import config_man
from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.tests.models.test_wiz_model import Base


class TestPredicate(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Predicate

  def test_perform_comparison(self):
    self.assertTrue(comp('=', 1, 1))
    self.assertTrue(comp('=', 1, '1'))
    self.assertTrue(comp('=', '1', 1))
    self.assertFalse(comp('=', '1', '2'))
    self.assertTrue(comp('>', 2, 1))
    self.assertTrue(comp('<', 1, 2))
    self.assertTrue(comp('>=', 2, 2))
    self.assertTrue(comp('>=', 3, 2))
    self.assertTrue(comp('<=', 2, 2))
    self.assertTrue(comp('<=', 2, 3))
    self.assertTrue(comp('in', 1, [1, 2]))
    self.assertTrue(comp('in', 'fo', 'foo'))
    self.assertTrue(comp('contains', [1, 2], 1))
    self.assertTrue(comp('only', [1, 1], 1))
    self.assertFalse(comp('only', [1, 2], 1))
    self.assertFalse(comp('defined', '', None))
    self.assertFalse(comp('defined', None, None))
    self.assertTrue(comp('defined', 'x', None))
    self.assertTrue(comp('undefined', '', None))

  def test_evaluate(self):
    config_man._ns = 'mock'
    predicate = Predicate(dict(challenge='{app/ns}'))
    self.assertEqual('mock', predicate.challenge)
    self.assertEqual('==', predicate.operator)


def comp(name, challenge, check_against) -> bool:
  return Predicate.perform_comparison(name, challenge, check_against)

def mk_pred0(challenge, against, op='eq'):
  return dict(
    operator=op,
    challenge=challenge,
    check_against=against
  )


def create_cmap(name, ns=None, data=None):
  data = data if data else dict(foo='bar')
  return broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(name=name),
      data=data
    )
  )
