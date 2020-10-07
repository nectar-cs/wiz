from nectwiz.model.action.action_parts.run_hooks_action_part import RunHookGroupActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.error.controller_error import ActionHalt
from nectwiz.model.hook.hook import Hook
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestRunHookGroupActionPart(ClusterTest):
  def test_hooks(self):
    h1 = Hook(dict(
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
        cmd='echo this-wont-crash'
      )
    ))

    h2 = Hook(dict(
      id='h2',
      kind='Hook',
      title='After Only',
      abort_on_fail=False,
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
    ))

    h3 = Hook(dict(
      id='h3',
      kind='Hook',
      title='Both',
      abort_on_fail=True,
      trigger_selector=dict(
        event='software-update',
        update_type='release',
      ),
      action=dict(
        kind='CmdExecAction',
        cmd='this-will-crash',
      )
    ))

    observer = Observer()
    subject = RunHookGroupActionPart
    self.assertEqual(0, len(observer.errdicts))
    subject.perform(observer, 'before', [h1, h2])
    self.assertEqual(1, len(observer.errdicts))

    with self.assertRaises(ActionHalt):
      subject.perform(observer, 'before', [h1, h2, h3])
