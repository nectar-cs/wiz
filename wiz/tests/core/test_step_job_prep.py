import time

from k8_kat.utils.testing import ns_factory
from wiz.core import step_job_prep, step_job_client
from wiz.core.wiz_globals import wiz_app
from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestStepJobPrep(ClusterTest):

  def test_status(self):
    wiz_app.ns_overwrite, = ns_factory.request(1)
    job_id = step_job_prep.create_and_run(
      image='ruby:2.6.6-alpine3.12',
      command=["ruby", "-e"],
      args=[inline_ruby_program()],
      values=dict(x='y')
    )

    pod = step_job_client.find_worker_pod(job_id)
    pod.wait_until(pod.is_running_normally)
    time.sleep(2)

    status_dict = step_job_client.extract_status(pod)
    bundle = step_job_client.compute_job_status(job_id)
    expected = dict(name='foo', status='bar', pct=50)
    self.assertEqual(expected, status_dict)

    pod.wait_until(pod.has_run)
    self.assertEqual('done', pod.clean_logs())

    self.assertEqual(1, len(bundle.parts))
    self.assertEqual('foo', bundle.parts[0].name)
    self.assertEqual('bar', bundle.parts[0].status)
    self.assertEqual(50, bundle.parts[0].pct)

  def test_create_and_run_completed(self):
    wiz_app.ns_overwrite, = ns_factory.request(1)
    job_id = step_job_prep.create_and_run(
      image='ruby:2.6.6-alpine3.12',
      command=["ruby", "-e"],
      args=["puts 'hello wiz'"],
      values=dict(x='y')
    )

    pod = step_job_client.find_worker_pod(job_id)
    pod.wait_until(pod.has_run)
    job = step_job_client.find_job(job_id)

    self.assertEqual('positive', job.ternary_status())
    self.assertEqual('Succeeded', pod.phase)
    self.assertEqual('positive', pod.ternary_status())
    self.assertEqual(True, pod.has_succeeded())
    self.assertEqual("hello wiz", pod.clean_logs())

  def test_create_and_run_failed(self):
    wiz_app.ns_overwrite, = ns_factory.request(1)
    job_id = step_job_prep.create_and_run(
      image='ruby:2.6.6-alpine3.12',
      command=["ruby", "-e", "fail!"],
      args=[],
      values=dict(x='y')
    )

    pod = step_job_client.find_worker_pod(job_id)
    pod.wait_until(pod.has_run)

    self.assertEqual('Failed', pod.phase)
    self.assertEqual('negative', pod.ternary_status())
    self.assertEqual(False, pod.has_succeeded())


def inline_ruby_program():
  j_status = "JSON.dump({name: :foo, status: :bar, pct: 50})"
  status_stmt = f"File.write('{step_job_prep.status_fname}', {j_status})"
  end_stmt = f"sleep(12); p 'done'"
  return f"require 'json'; {status_stmt}; {end_stmt}"
