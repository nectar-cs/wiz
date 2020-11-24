from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.model.action.action_parts.run_hooks_action_part import RunHookGroupActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.error.controller_error import ActionHalt
from nectwiz.model.hook.hook import Hook
from nectwiz.tests.t_helpers.cluster_test import ClusterTest
from nectwiz.tests.t_helpers.helper import create_base_master_map


class TestRunHookGroupActionPart(ClusterTest):
  def test_hooks(self):
    models_man.clear(restore_defaults=True)
    models_man.add_descriptors([
      dict(
        id='h1',
        kind='Hook',
        title='Hook 1',
        trigger_selector=dict(
          prop1='foo'
        )
      ),
      dict(
        id='h2',
        kind='Hook',
        title='Hook 2',
        trigger_selector=dict(
          prop1='bar'
        )
      ),
      dict(
        id='h3',
        kind='Hook',
        title='Hook 3',
        trigger_selector=dict(
          prop1='foo',
          prop2='bar'
        )
      )
    ])

    ids = lambda **labs: list(map(Hook.id, Hook.by_trigger(**labs)))
    self.assertEqual(['h1'], ids(prop1='foo'))
    self.assertEqual(['h1', 'h3'], ids(prop1='foo', prop2='bar'))
    # self.assertEqual(['h1'], ids(Hook.by_trigger(prop1='foo')))
