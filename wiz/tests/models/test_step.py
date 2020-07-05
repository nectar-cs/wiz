from typing import Type

from k8_kat.res.pod.kat_pod import KatPod


from k8_kat.utils.testing import ns_factory
from wiz.core.wiz_globals import wiz_app
from wiz.model.base.wiz_model import WizModel
from wiz.model.step.step import Step
from wiz.tests.models.test_wiz_model import Base


class TestStep(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Step

  def test_affected_resources(self):
    from k8_kat.tests.res.common.test_kat_pod import TestKatPod
    from k8_kat.tests.res.common.test_kat_svc import TestKatSvc

    ns, = ns_factory.request(1)
    wiz_app.ns_overwrite = ns
    step = Step(dict(
      key='foo',
      title='foo',
      res=["Pod:", "Service:s1"]
    ))
    TestKatSvc.create_res('s1', ns)
    TestKatSvc.create_res('s2', ns)
    TestKatPod.create_res('p1', ns)

    TestKatPod.create_res('p2', ns)
    actual = step.affected_resources()
    self.assertEqual(names(actual), ['p1', 'p2', 's1'])

  def test_status_simple(self):
    from k8_kat.tests.res.common.test_kat_svc import TestKatSvc
    ns, = ns_factory.request(1)
    wiz_app.ns_overwrite = ns
    step = Step(dict(key='foo', title='foo', res=["Service:"]))
    TestKatSvc.create_res('s1', ns)
    self.assertEqual('positive', step.compute_status())

  def test_status_pending(self):
    from k8_kat.tests.res.common.test_kat_pod import TestKatPod
    from k8_kat.tests.res.common.test_kat_svc import TestKatSvc

    ns, = ns_factory.request(1)
    wiz_app.ns_overwrite = ns
    step = Step(dict(key='foo', title='foo', res=["Pod:", "Service:"]))

    TestKatSvc.create_res('s1', ns)
    pod = KatPod(TestKatPod.create_res('p1', ns))

    self.assertEqual('pending', step.compute_status())
    pod.wait_until(pod.has_settled)
    self.assertEqual('positive', step.compute_status())

  def test_status_negative(self):
    from k8_kat.tests.res.common.test_kat_pod import TestKatPod
    from k8_kat.tests.res.common.test_kat_svc import TestKatSvc

    ns, = ns_factory.request(1)
    wiz_app.ns_overwrite = ns
    step = Step(dict(key='foo', title='foo', res=["Pod:", "Service:"]))

    TestKatSvc.create_res('s1', ns)
    pod = KatPod(TestKatPod.create_res('p1', ns, image='bro-ken'))

    self.assertEqual('pending', step.compute_status())
    pod.wait_until(pod.has_settled)
    self.assertEqual('negative', step.compute_status())

def names(res_list):
  return [r.name for r in res_list]