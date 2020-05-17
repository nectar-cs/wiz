import unittest
from unittest.mock import MagicMock

from wiz.model.field.validator import EqValidator, Validator, NeqValidator


def g_conf(c='Check', m='Message', t='warning'):
  return dict(
    check_against=c,
    message=m,
    tone=t
  )

class TestValidator(unittest.TestCase):

  def test_validate_when_nothing(self):
    v = Validator(g_conf())
    v.perform = MagicMock(return_value=False)
    self.assertEqual(v.validate(None), [None, None])

  def test_validate_when_warn(self):
    v = Validator(g_conf(t='warning', m='foo'))
    v.perform = MagicMock(return_value=True)
    self.assertEqual(v.validate(None), ['warning', 'foo'])

  def test_validate_when_error(self):
    v = Validator(g_conf(t='error', m='bar'))
    v.perform = MagicMock(return_value=True)
    self.assertEqual(v.validate(None), ['error', 'bar'])

  def test_inflate(self):
    config = dict(**g_conf(), type='equality')
    self.assertEqual(type(Validator.inflate(config)), EqValidator)

    config = dict(**g_conf(), type='inequality')
    self.assertEqual(type(Validator.inflate(config)), NeqValidator)

    with self.assertRaises(RuntimeError):
      config = dict(**g_conf(), type='obviously-non-existing-type')
      Validator.inflate(config)

class TestEqValidator(unittest.TestCase):

  def test_perform_with_easy_values(self):
    v = EqValidator(g_conf(c='foo'))
    self.assertTrue(v.perform('foo'))
    self.assertFalse(v.perform('bar'))

  def test_perform_with_fringe_values(self):
    v = EqValidator(g_conf(c='none'))
    self.assertTrue(v.perform('None'))
    self.assertTrue(v.perform(None))
    self.assertFalse(v.perform(False))
    self.assertFalse(v.perform(0))

    v = EqValidator(g_conf(c='true'))
    self.assertTrue(v.perform('true'))
    self.assertTrue(v.perform(True))
