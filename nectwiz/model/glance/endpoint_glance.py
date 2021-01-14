from werkzeug.utils import cached_property

from nectwiz.core.core.types import EndpointDict
from nectwiz.model.glance.glance import Glance


class EndpointGlance(Glance):
  ENDPOINT_DATA_KEY = 'endpoint'

  @cached_property
  def title(self):
    return self.get_prop(self.TITLE_KEY, 'App Endpoint')

  @cached_property
  def image(self):
    return

  @cached_property
  def view_type(self):
    return 'graphic_and_text'

  @cached_property
  def legend_icon(self) -> str:
    return 'open_in_new'

  @cached_property
  def url_intent(self) -> str:
    return self.endpoint_data.get('url')

  @cached_property
  def endpoint_data(self) -> EndpointDict:
    return self.get_prop(self.ENDPOINT_DATA_KEY)

  @cached_property
  def info(self) -> str:
    if self.endpoint_data and self.endpoint_data.get('url'):
      return self.endpoint_data['url']
    else:
      return 'Endpoint not working'

  def content_spec(self):
    result = self.endpoint_data
    if result and result['online']:
      is_external = result['type'] == 'external'
      return {
        'icon': 'public' if is_external else 'vpn_lock',
        'value': result['name'] or self.title,
        'icon_emotion': 'pleasant'
      }
    else:
      return {
        'icon': 'public_off',
        'value': (result or {}).get('name') or self.title,
        'icon_emotion': 'warning2'
      }
