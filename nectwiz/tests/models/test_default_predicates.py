from nectwiz.core.core import utils
from nectwiz.model.predicate.resource_property_predicate import ResourcePropertyPredicate
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestDefaultPredicates(ClusterTest):
  def test_from_apply_outcome(self):
    outcomes = utils.logs2outkomes([
      "pods/pod created",
      "namespaces/ns configured",
      "apps.deployments/dep unchanged"
    ])

    result = ResourcePropertyPredicate.from_apply_outcome(outcomes)
    self.assertEqual(2, len(result['positive']))
    self.assertEqual(2, len(result['negative']))

    self.assertEqual('positive', result['positive'][0].config['check_against'])
    self.assertEqual(dict(
      res_kind='pods',
      name='pod',
      api_group='',
    ), result['positive'][0].config['selector'])

    self.assertEqual('negative', result['negative'][0].config['check_against'])
    self.assertEqual(dict(
      res_kind='pods',
      name='pod',
      api_group='',
    ), result['negative'][0].config['selector'])

