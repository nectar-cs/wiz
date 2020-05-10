import unittest
from wiz.core.res_match_rule import ResMatchRule, component_matches

def gen_res(kind, name, ns='ns'):
  return dict(kind=kind, metadata=dict(name=name, namespace=ns))

class TestResMatchRules(unittest.TestCase):

  def test_init_with_ns(self):
    subject = ResMatchRule("ns:kind:name")
    self.assertEqual(subject.ns_expr, "ns")
    self.assertEqual(subject.kind_expr, "kind")
    self.assertEqual(subject.name_expr, "name")

  def test_init_without_ns(self):
    subject = ResMatchRule("kind:name")
    self.assertEqual(subject.kind_expr, "kind")
    self.assertEqual(subject.name_expr, "name")

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
