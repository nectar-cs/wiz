from k8_kat.res.pod.kat_pod import KatPod

from k8_kat.utils.testing import simple_pod, ns_factory
from wiz.core import utils

from wiz.core.wiz_globals import wiz_app
from wiz.model.step.step import Step
from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestStatusComputer(ClusterTest):

  @classmethod
  def tearDownClass(cls) -> None:
    pass

  def test_compute_conditions_status_no_res(self):
    wiz_app.ns_overwrite = 'ns1'
    actual = mk_step(raf='Pod:wont-be-there').compute_status()
    actual_pos = actual['condition_statuses']['positive']
    expected_pos_key = 'nectar.exit_conditions.select_resources_positive'
    self.assertEqual('pending', actual['status'])
    self.assertFalse(actual_pos[0]['met'])
    self.assertEqual(expected_pos_key, actual_pos[0]['key'])

  def test_compute_conditions_status_with_res(self):
    wiz_app.ns_overwrite, = ns_factory.request(1)
    step = mk_step(raf='Pod:*')

    fast_pod, slow_pod = mk_sleeper(1), mk_sleeper(19)
    fast_pod.wait_until(fast_pod.has_run)
    print("FAST HAS RUN")
    slow_pod.wait_until(slow_pod.is_running_normally)
    print("SLOW RUNNING")

    actual = step.compute_status()
    actual_pos = actual['condition_statuses']['positive']
    self.assertFalse(actual_pos[0]['met'])
    self.assertEqual('pending', actual['status'])

    print("NOW WAIT SLOW RUN")
    slow_pod.wait_until(slow_pod.has_run)
    print("SLOWW HAS RUN")

    actual = step.compute_status()
    actual_pos = actual['condition_statuses']['positive']
    self.assertTrue(actual_pos[0]['met'])
    self.assertEqual('positive', actual['status'])


def mk_sleeper(seconds):
  return KatPod(simple_pod.create(
    name=utils.rand_str(),
    restart='Never',
    ns=wiz_app.ns,
    image='ruby:2.6.6-alpine3.12',
    command=["ruby", "-e"],
    args=[f"sleep({seconds}); puts :done; exit 0"],
  ))


def mk_step(**kwargs) -> Step:
  defaults = dict(
    key='s',
    resource_apply_filter=kwargs.get('raf'),
    applies_manifest=True
  )
  return Step({**defaults, **kwargs})
