import unittest

from wiz.model.step import expr


class TestConcern(unittest.TestCase):

  def test_eval_next_expr_when_str(self):
    result = expr.eval_next_expr('simple', {})
    self.assertEqual(result, 'simple')

  def test_eval_next_expr_when_cond_positive(self):
    values = dict(f1='against-foo')
    result = expr.eval_next_expr(ift_expression(), values)
    self.assertEqual(result, 'then-foo')

  def test_eval_next_expr_when_cond_negative(self):
    values = dict(f1='eval-to-false')
    result = expr.eval_next_expr(ift_expression(), values)
    self.assertEqual(result, 'else-bar')

def ift_expression():
  return {
    'if': [
      dict(
        field='f1',
        type='equality',
        check_against='against-foo'
      )
    ],
    'then': 'then-foo',
    'else': 'else-bar'
  }
