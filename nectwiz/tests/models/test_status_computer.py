from k8_kat.res.pod.kat_pod import KatPod

from k8_kat.utils.testing import simple_pod, ns_factory
from nectwiz.core import utils

from nectwiz.core.wiz_app import wiz_app
from nectwiz.model.step.step import Step
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestStatusComputer(ClusterTest):

  def test_compute_conditions_status_no_res(self):
    wiz_app._ns, = ns_factory.request(1)
    actual = mk_step(raf='Pod:wont-be-there').compute_status()
    actual_pos = actual['condition_statuses']['positive']
    expected_pos_key = 'nectar.exit_conditions.select_resources_positive'

    self.assertEqual('pending', actual['status'])
    self.assertFalse(actual_pos[0]['met'])
    self.assertEqual(expected_pos_key, actual_pos[0]['key'])

  def test_compute_conditions_neg(self):
    wiz_app._ns, = ns_factory.request(1)
    step = mk_step(raf='Pod:*')

    crasher = mk_sleeper('not-an-int')
    crasher.wait_until(crasher.has_failed)

    actual = step.compute_status()
    actual_pos = actual['condition_statuses']['negative']
    self.assertTrue(actual_pos[0]['met'])
    self.assertEqual('negative', actual['status'])

  def test_compute_conditions_status_with_res(self):
    wiz_app._ns, = ns_factory.request(1)
    cond = mk_cond('Pod:*', 'all', 'has_succeeded', 'True')
    step = mk_step(raf='Pod:*', exit=dict(positive=[cond]))

    fast_pod, slow_pod = mk_sleeper(1), mk_sleeper(19)

    fast_pod.wait_until(fast_pod.has_run)
    slow_pod.wait_until(slow_pod.is_running_normally)

    actual = step.compute_status()
    actual_pos = actual['condition_statuses']['positive']
    self.assertFalse(actual_pos[0]['met'])
    self.assertEqual('pending', actual['status'])

    slow_pod.wait_until(slow_pod.has_run)

    actual = step.compute_status()
    actual_pos = actual['condition_statuses']['positive']
    self.assertTrue(actual_pos[0]['met'])
    self.assertEqual('positive', actual['status'])


def mk_sleeper(seconds):
  return KatPod(simple_pod.create(
    name=utils.rand_str(),
    restart='Never',
    ns=wiz_app.ns(),
    image='ruby:2.6.6-alpine3.12',
    command=["ruby", "-e"],
    args=[f"sleep({seconds}); puts :done; exit 0"],
  ))


def mk_cond(sel, match, prop, against):
  return dict(
    key=utils.rand_str(4),
    selector=sel,
    match=match,
    property=prop,
    check_against=against
  )


def mk_step(**kwargs) -> Step:
  defaults = dict(
    key='s',
    resource_apply_filter=kwargs.get('raf'),
    applies_manifest=True
  )
  return Step({**defaults, **kwargs})
