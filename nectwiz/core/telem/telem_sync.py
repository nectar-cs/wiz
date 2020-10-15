from nectwiz.core.core import hub_client, config_man
from nectwiz.core.core.config_man import config_man


def upload_meta():
  tam = config_man.read_tam()
  last_updated_checked = config_man.read_last_update_checked()
  payload = {
    'tam_type': tam['type'],
    'tam_uri': tam['uri'],
    'tam_ver': tam['version'],
    'last_update_check': last_updated_checked
  }

  endpoint = f'/installs/{config_man.install_uuid()}'
  hub_client.patch(endpoint, payload)
