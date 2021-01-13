from typing import Dict, Optional

from werkzeug.utils import cached_property

from nectwiz.model.base.wiz_model import WizModel


# - website endpoint
# - any predicate
# - left battery, right pct
# - short text with line underneath
# - pie chart in the middle


class Glance(WizModel):

  VIEW_TYPE_KEY = 'view_key'
  CONTENT_SPEC_KEY = 'content'
  LEGEND_ICON_KEY = 'legend_icon'
  URL_INTENT_KEY = 'url'

  @cached_property
  def view_type(self) -> str:
    return self.resolve_prop(self.VIEW_TYPE_KEY, warn=True)

  @cached_property
  def legend_icon(self) -> Optional[str]:
    return self.get_prop(self.LEGEND_ICON_KEY)

  @cached_property
  def url_intent(self) -> Optional[str]:
    return self.get_prop(self.URL_INTENT_KEY)

  def fast_serialize(self) -> Dict:
    return {'id': self.id(), 'title': self.title}

  def compute_and_serialize(self):
    return {
      'title': self.title,
      'legend': self.info,
      'content_spec': self.content_spec(),
      'view_type': self.view_type,
      'url': self.url_intent,
      'legend_icon': self.legend_icon
    }

  def content_spec(self):
    raise NotImplementedError
