from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.supply.value_supplier import ValueSupplier
from nectwiz.tests.models.test_wiz_model import Base


class TestValueSupplier(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ValueSupplier

  def test_serialize_item_prop_default(self):
    result = ValueSupplier.serialize_item_prop('foo', None)
    self.assertEqual('foo', result)

    result = ValueSupplier.serialize_item_prop('foo', 'bar')
    self.assertEqual(None, result)

    result = ValueSupplier.serialize_item_prop({'foo': 'bar'}, 'foo')
    self.assertEqual('bar', result)

    result = ValueSupplier.serialize_item_prop('foo', 'lower')
    self.assertEqual('foo', result)

  def test_serialize_item_default(self):
    instance = ValueSupplier(dict())
    result = instance.serialize_item('Letter')
    self.assertEqual('Letter', result)

  def test_serialize_item_blank(self):
    instance = ValueSupplier(dict(output=''))
    result = instance.serialize_item('Letter')
    self.assertEqual('Letter', result)

  def test_serialize_item_string(self):
    instance = ValueSupplier(dict(output='lower'))
    result = instance.serialize_item('Letter')
    self.assertEqual('letter', result)

  def test_serialize_item_dict(self):
    output = dict(lower_case='lower')
    instance = ValueSupplier(dict(output=output))
    result = instance.serialize_item('Letter')
    self.assertEqual({'lower_case': 'letter'}, result)

  def test_serialize_explicit_many(self):
    instance = ValueSupplier({'many': True})
    result = instance.serialize_computed_value('Letter')
    self.assertEqual(['Letter'], result)

    instance = ValueSupplier({'many': False, 'output': 'foo'})
    _input = [dict(foo='bar'), dict(foo='rab')]
    result = instance.serialize_computed_value(_input)
    self.assertEqual('bar', result)

  def test_serialize_explicit_auto(self):
    instance = ValueSupplier({})
    result = instance.serialize_computed_value([dict(foo='bar')])
    self.assertEqual([dict(foo='bar')], result)

    instance = ValueSupplier({'output': {'Bar': 'bar'}})
    result = instance.serialize_computed_value(dict(foo='bar', bar='baz'))
    self.assertEqual({'Bar': 'baz'}, result)
