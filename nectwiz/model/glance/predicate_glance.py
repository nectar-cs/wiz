from werkzeug.utils import cached_property

from nectwiz.model.glance.glance import Glance
from nectwiz.model.predicate.predicate import Predicate


class PredicateGlance(Glance):
  PREDICATE_KEY = 'predicate'
  PASS_TEXT_KEY = 'pass_text'
  FAIL_TEXT_KEY = 'fail_text'
  PASS_ICON_KEY = 'pass_icon'
  FAIL_ICON_KEY = 'fail_icon'

  @cached_property
  def view_type(self) -> str:
    return "graphic_and_text"

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

  @cached_property
  def pass_icon(self) -> str:
    return self.get_prop(self.PASS_ICON_KEY, 'done_all')

  @cached_property
  def fail_icon(self) -> str:
    return self.get_prop(self.FAIL_ICON_KEY, 'help_outline')

  def eval_result(self) -> bool:
    return self.predicate.evaluate()

  def content_spec(self):
    success = self.eval_result()
    return {
      'icon': self.pass_icon if success else self.fail_icon,
      'icon_emotion': 'milGreen' if success else 'warning2',
      'value': self.pass_text if success else self.fail_text
    }
