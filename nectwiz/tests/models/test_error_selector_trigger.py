from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.model.error.error_context import ErrCtx
from nectwiz.model.error.error_trigger_selector import ErrorTriggerSelector
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestErrorTriggerSelector(ClusterTest):

  def test_prop_match_score(self):
    selector: ErrorTriggerSelector = ErrorTriggerSelector.inflate(dict(
      property_selector=dict(
        foo='bar',
        bar='baz'
      )
    ))

    actual = selector.prop_match_score(ErrCtx(dict()))
    self.assertEqual(0, actual)

    actual = selector.prop_match_score(ErrCtx(dict(foo='bar')))
    self.assertEqual(1, actual)

    actual = selector.prop_match_score(ErrCtx(dict(extras=dict(foo='bar'))))
    self.assertEqual(1, actual)

    actual = selector.prop_match_score(ErrCtx(dict(foo='bar', bar='baz')))
    self.assertEqual(2, actual)

    actual = selector.prop_match_score(
      ErrCtx(dict(foo='bar', extras=dict(bar='baz')))
    )
    self.assertEqual(2, actual)

    actual = selector.prop_match_score(ErrCtx(dict(foo='baz')))
    self.assertIsNone(actual)

  def test_res_match_score(self):
    config_man._ns, = ns_factory.request(1)
    selector: ErrorTriggerSelector = ErrorTriggerSelector.inflate(dict(
      resource_selector=dict(
        res_kind='ConfigMap',
        name='foo'
      )
    ))

    resdict = dict(kind='configmaps', name='foo')
    actual = selector.res_match_score(ErrCtx(dict(resource=resdict)))
    self.assertEqual(1, actual)

    resdict = dict(kind='configmap', name='foo')
    actual = selector.res_match_score(ErrCtx(dict(resource=resdict)))
    self.assertEqual(1, actual)

    resdict = dict(kind='ConfigMap', name='foo')
    actual = selector.res_match_score(ErrCtx(dict(resource=resdict)))
    self.assertEqual(1, actual)

    resdict = dict(kind='ConfigMap', name='bar')
    actual = selector.res_match_score(ErrCtx(dict(resource=resdict)))
    self.assertEqual(None, actual)

    # selector: ErrorTriggerSelector = ErrorTriggerSelector.inflate({})
    # resdict = dict(kind='ConfigMap', name='foo')
    # actual = selector.res_match_score(ErrCtx(dict(resource=resdict)))
    # self.assertEqual(0, actual)
