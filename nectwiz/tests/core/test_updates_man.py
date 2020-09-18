import time

from k8kat.res.pod.kat_pod import KatPod
from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import TamDict, UpdateDict
from nectwiz.core.telem import updates_man
from nectwiz.core.telem.update_observer import UpdateObserver
from nectwiz.core.telem.updates_man import HaltedError
from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.pre_built.cmd_exec_action import CmdExecAction
from nectwiz.tests.t_helpers.cluster_test import ClusterTest
from nectwiz.tests.t_helpers.helper import ci_tami_name, create_base_master_map


class TestUpdatesMan(ClusterTest):

  def setUp(self) -> None:
    models_man.clear(restore_defaults=True)

  def test_await_resource_settled(self):
    config_man._ns,  = ns_factory.request(1)
    action = CmdExecAction(config=dict(
      cmd=f"kubectl run nginx --image=nginx -n {config_man.ns()}"
    ))
    logs = action.run()['data']['logs']
    observer = UpdateObserver('release')
    observer.on_perform_finished('positive', logs)
    updates_man.await_resource_settled(observer)

  def test_hooks(self):
    models_man.add_descriptors([
      dict(
        id='h1',
        kind='Hook',
        title='Before Only',
        trigger_selector=dict(
          event='software-update',
          update_type='release',
          timing='before'
        ),
        action=dict(
          kind='CmdExecAction',
          cmd='echo before'
        )
      ),
      dict(
        id='h2',
        kind='Hook',
        title='After Only',
        abort_on_fail=True,
        trigger_selector=dict(
          event='software-update',
          update_type='release',
          timing='after'
        ),
        action=dict(
          kind='CmdExecAction',
          cmd='this-will-crash',
          timing='after'
        )
      ),
      dict(
        id='h3',
        kind='Hook',
        title='Both',
        trigger_selector=dict(
          event='software-update',
          update_type='release',
        ),
        action=dict(
          kind='CmdExecAction',
          cmd='this-will-crash',
        )
      ),
    ])

    boil = lambda p: (p['id'], p['status'])
    observer = UpdateObserver('release')

    r_before = updates_man.run_hooks('before', update_package, observer)
    self.assertTrue(r_before)
    exp = [('Before Only', 'positive'), ('Both', 'negative')]
    actual = list(map(boil, observer.item('before_hooks')['sub_items']))
    self.assertEqual(exp, actual)

    with self.assertRaises(HaltedError):
      r_after = updates_man.run_hooks('after', update_package, observer)
      self.assertFalse(r_after)
      exp = [('After Only', 'negative'), ('Both', 'negative')]
      actual = list(map(boil, observer.item('after_hooks')['sub_items']))
      self.assertEqual(exp, actual)



  def test_apply_release_update(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man.ns())

    config_man.write_tam(TamDict(
      version='1.0.0',
      type='image',
      uri=ci_tami_name(),
      args=None
    ))

    config_man.commit_keyed_mfst_vars([
      ('pod.name', 'legally-custom'),
    ])

    models_man.add_descriptors([
      dict(
        kind='ChartVariable',
        id='pod.image',
        release_overridable=True
      ),
      dict(
        kind='ChartVariable',
        id='pod.name',
        release_overridable=False
      )
    ])

    observer = UpdateObserver('release')
    updates_man.perform(update_package, observer)
    time.sleep(4)

    progress = observer.item('perform')
    ns, defs = config_man.ns(), config_man.tam_defaults(True)
    tam, mfst_vars = config_man.tam(True), config_man.mfst_vars(True)
    self.assertEqual("2.0.0", tam.get('version'))
    self.assertEqual(ci_tami_name(), tam.get('uri'))

    self.assertEqual('nginx:1.19.2', mfst_vars['pod']['image'])
    self.assertEqual('legally-custom', mfst_vars['pod']['name'])

    self.assertEqual('nginx:1.19.2', defs['pod']['image'])
    self.assertEqual('pod', defs['pod']['name'])

    self.assertIsNotNone(KatPod.find('legally-custom', ns))

    exp_logs = ['service/service created', 'pod/legally-custom created']
    self.assertEqual('positive', progress['status'])
    self.assertEqual(exp_logs, progress['logs'])

  # def test_run_hooks(self):


update_package = UpdateDict(
  id='foo',
  type='release',
  version='2.0.0',
  injections={},
  manual=False
)
