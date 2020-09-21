import unittest

from nectwiz.core.core.subs import SubsGetter, interp


class TestSubs(unittest.TestCase):
  def test__getitem__direct(self):
    simple_getter = SubsGetter(dict(foo='bar'))
    self.assertEqual('bar', simple_getter['foo'])

  def test__getitem__resolving(self):
    resolving_getter = SubsGetter(dict(
      resolvers=dict(
        foo=lambda k: f"new_{k}"
      )
    ))
    self.assertEqual('new_bar', resolving_getter['foo/bar'])

  def test_interp(self):
    context = dict(
      foo='bar',
      resolvers=dict(
        foo=lambda k: f"new_{k}"
      )
    )

    string = "easy {foo} hard {foo/bar}"
    expect = "easy bar hard new_bar"
    self.assertEqual(expect, interp(string, context))
