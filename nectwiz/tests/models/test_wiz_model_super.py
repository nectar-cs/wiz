import unittest

from nectwiz.model.base.wiz_model import configs_for_kinds, find_class_by_name, WizModel


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

  def test_truncate_kod_prefix(self):
    result = WizModel.truncate_kod_prefix("foo", "")
    self.assertEqual("foo", result)

    result = WizModel.truncate_kod_prefix("foo", "id::")
    self.assertEqual("foo", result)

    result = WizModel.truncate_kod_prefix("id::bar", "id::")
    self.assertEqual("bar", result)
