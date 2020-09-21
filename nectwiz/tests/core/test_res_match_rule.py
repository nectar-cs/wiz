from k8kat.utils.testing import ns_factory, simple_pod, simple_svc
from nectwiz.model.base.resource_selector import ResourceSelector, component_matches
from nectwiz.core.core.config_man import config_man
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


def gen_res(kind, name, ns='ns'):
  return dict(kind=kind, metadata=dict(name=name, namespace=ns))

class TestResMatchRules(ClusterTest):

  def test_init_with_str(self):
    subject = ResourceSelector("kind:name")
    self.assertEqual(subject.kind, "kind")
    self.assertEqual(subject.name, "name")

  def test_init_with_dict(self):
    rule_dict = dict(
      kind='A',
      name='B',
      label_selectors=dict(a='b'),
      field_selectors=dict(b='c')
    )
    subject = ResourceSelector(rule_dict)
    for key, value in rule_dict.items():
      self.assertEqual(getattr(subject, key), rule_dict[key])

  def test_component_matches(self):
    self.assertTrue(component_matches("x", "x"))
    self.assertTrue(component_matches("*", "x"))
    self.assertFalse(component_matches("ab", "ba"))

  def test_evaluate(self):
    subject = ResourceSelector("x:x")
    self.assertTrue(subject.evaluate(gen_res('x', 'x')))
    self.assertFalse(subject.evaluate(gen_res('x', 'y')))

    subject = ResourceSelector("x:*")
    self.assertTrue(subject.evaluate(gen_res('x', 'z')))

  def test_query(self):
    ns, = ns_factory.request(1)
    config_man._ns = ns
    simple_svc.create(name='s1', ns=ns)
    simple_svc.create(name='s2', ns=ns)

    simple_pod.create(name='p1', ns=ns)
    simple_pod.create(name='p2', ns=ns)

    actual = ResourceSelector("Service:s0").query_cluster()
    self.assertEqual(names(actual), [])

    actual = ResourceSelector("Role:").query_cluster()
    self.assertEqual(names(actual), [])

    actual = ResourceSelector("Service:s1").query_cluster()
    self.assertEqual(names(actual), ['s1'])

    actual = ResourceSelector("Service:").query_cluster()
    self.assertEqual(names(actual), ['s1', 's2'])

    actual = ResourceSelector(dict(
      kind='Service',
      label_selectors=dict(app='s2')
    )).query_cluster()
    self.assertEqual(names(actual), ['s2'])

    actual = ResourceSelector(dict(kind='Pod', name='p1')).query_cluster()
    self.assertEqual(names(actual), ['p1'])

def names(res_list):
  return [r.name for r in res_list]
