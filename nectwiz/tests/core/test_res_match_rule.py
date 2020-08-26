from k8_kat.utils.testing import ns_factory
from nectwiz.model.base.res_match_rule import ResMatchRule, component_matches
from nectwiz.core.wiz_app import wiz_app
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


def gen_res(kind, name, ns='ns'):
  return dict(kind=kind, metadata=dict(name=name, namespace=ns))

class TestResMatchRules(ClusterTest):

  def test_init_with_str(self):
    subject = ResMatchRule("kind:name")
    self.assertEqual(subject.kind, "kind")
    self.assertEqual(subject.name, "name")

  def test_init_with_dict(self):
    rule_dict = dict(
      kind='A',
      name='B',
      label_selectors=dict(a='b'),
      field_selectors=dict(b='c')
    )
    subject = ResMatchRule(rule_dict)
    for key, value in rule_dict.items():
      self.assertEqual(getattr(subject, key), rule_dict[key])

  def test_component_matches(self):
    self.assertTrue(component_matches("x", "x"))
    self.assertTrue(component_matches("*", "x"))
    self.assertFalse(component_matches("ab", "ba"))

  def test_evaluate(self):
    subject = ResMatchRule("x:x")
    self.assertTrue(subject.evaluate(gen_res('x', 'x')))
    self.assertFalse(subject.evaluate(gen_res('x', 'y')))

    subject = ResMatchRule("x:*")
    self.assertTrue(subject.evaluate(gen_res('x', 'z')))

  def test_query(self):
    from k8_kat.tests.res.common.test_kat_svc import TestKatSvc
    from k8_kat.tests.res.common.test_kat_pod import TestKatPod

    ns, = ns_factory.request(1)
    wiz_app.ns = ns
    TestKatSvc.create_res('s1', ns)
    TestKatSvc.create_res('s2', ns)

    TestKatPod.create_res('p1', ns)
    TestKatPod.create_res('p2', ns)

    actual = ResMatchRule("Service:s0").query()
    self.assertEqual(names(actual), [])

    actual = ResMatchRule("Role:").query()
    self.assertEqual(names(actual), [])

    actual = ResMatchRule("Service:s1").query()
    self.assertEqual(names(actual), ['s1'])

    actual = ResMatchRule("Service:").query()
    self.assertEqual(names(actual), ['s1', 's2'])

    actual = ResMatchRule(dict(
      kind='Service',
      label_selectors=dict(app='s2')
    )).query()
    self.assertEqual(names(actual), ['s2'])

    actual = ResMatchRule(dict(kind='Pod', name='p1')).query()
    self.assertEqual(names(actual), ['p1'])

def names(res_list):
  return [r.name for r in res_list]