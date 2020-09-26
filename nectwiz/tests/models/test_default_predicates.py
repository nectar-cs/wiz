from nectwiz.model.predicate import default_predicates
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestDefaultPredicates(ClusterTest):
  def test_from_apply_outcome(self):
    logs = [
      "pods/pod created",
      "namespaces/ns configured",
      "apps.deployments/dep unchanged"
    ]

    result = default_predicates.from_apply_outcome(logs)
    self.assertEqual(2, len(result['positive']))
    self.assertEqual(2, len(result['negative']))

    self.assertEqual('positive', result['positive'][0].config['check_against'])
    self.assertEqual(dict(
      k8s_kind='pods',
      name='pod',
      api_group='',
    ), result['positive'][0].config['selector'])

    self.assertEqual('negative', result['negative'][0].config['check_against'])
    self.assertEqual(dict(
      k8s_kind='pods',
      name='pod',
      api_group='',
    ), result['negative'][0].config['selector'])

