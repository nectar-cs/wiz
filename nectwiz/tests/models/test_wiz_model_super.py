import unittest

from nectwiz.model.base.wiz_model import configs_for_kinds, find_class_by_name


class TestWizModelSuper(unittest.TestCase):

  class K1:
    pass

  class K3:
    pass

  def test_configs_of_kind(self):
    configs = [{'kind': 'K1'}, {'kind': 'K2'}, {'kind': 'K3'}]
    classes = [TestWizModelSuper.K1, TestWizModelSuper.K3]

    actual = configs_for_kinds(configs, classes)
    self.assertEqual([{'kind': 'K1'}, {'kind': 'K3'}], actual)

  def test_find_class_by_name(self):
    classes = [TestWizModelSuper.K1, TestWizModelSuper.K3]
    actual = find_class_by_name('K1', classes)
    self.assertEqual(TestWizModelSuper.K1, actual)
