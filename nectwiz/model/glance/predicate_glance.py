from werkzeug.utils import cached_property

from nectwiz.model.glance.glance import Glance
from nectwiz.model.predicate.predicate import Predicate


class PredicateGlance(Glance):
  PREDICATE_KEY = 'predicate'
  PASS_TEXT_KEY = 'pass_text'
  FAIL_TEXT_KEY = 'fail_text'

  @cached_property
  def predicate(self):
    return self.inflate_child(
      Predicate,
      prop=self.PREDICATE_KEY
    )

  @cached_property
  def pass_text(self):
    return self.get_prop(self.PASS_TEXT_KEY, 'Passing')

  @cached_property
  def fail_text(self):
    return self.get_prop(self.FAIL_TEXT_KEY, 'Failing')

  def eval_result(self):
    return self.predicate.evaluate()

  def content_spec(self):
    success = self.eval_result()
    return {
      'icon': 'done_all' if success else 'help_outline',
      'value': self.pass_text if success else self.fail_text
    }
