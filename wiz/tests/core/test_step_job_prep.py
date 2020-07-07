from k8_kat.utils.testing import ns_factory
from wiz.core import step_job_prep, step_job_client
from wiz.core.wiz_globals import wiz_app
from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestStepJobPrep(ClusterTest):

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


  @classmethod
  def tearDownClass(cls) -> None:
    pass
