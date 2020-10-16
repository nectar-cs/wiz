import json
from typing import Optional, Dict

from k8kat.auth.kube_broker import broker
from redis import Redis

from nectwiz.core.core import hub_client
from nectwiz.core.core.config_man import config_man

STRATEGY_DISABLED = 'disabled'
key_outcomes_list = 'update_outcomes'
key_config_backups_list = 'config_backups'

connection_obj = dict(
  redis=None
)


def redis() -> Optional[Redis]:
  return connection_obj['redis']


def get_redis():
  if not redis():
    connection_obj['redis'] = connect()
  return redis()


def parametrized(dec):
  def layer(*args, **kwargs):
    def repl(f):
      return dec(f, *args, **kwargs)
    return repl
  return layer


@parametrized
def connected_and_enabled(func, backup=None):
  def aux(*xs, **kws):
    is_local_dev = not broker.is_in_cluster_auth()
    manifest_vars = config_man.flat_manifest_vars()
    strategy = manifest_vars.get('telem_storage.strategy')
    if is_local_dev or (not strategy == STRATEGY_DISABLED):
      if get_redis():
        return func(*xs, **kws)
      else:
        return backup
    else:
      return backup
  return aux


def store_outcome(outcome: Dict):
  store_list_element(key_outcomes_list, outcome)


def store_config_backup(outcome: Dict):
  store_list_element(key_config_backups_list, outcome)


def list_outcomes():
  return list_records(key_outcomes_list)


def list_config_backups():
  return list_records(key_config_backups_list)


@connected_and_enabled(backup=None)
def store_list_element(list_key: str, item: Dict):
  stored_records = list_records(list_key)
  stored_records.append(item)
  redis().set(list_key, json.dumps(stored_records))


@connected_and_enabled(backup=[])
def list_records(key: str):
  return json.loads(redis().get(key) or '[]')


@connected_and_enabled(backup=[])
def clear_update_outcomes():
  redis().delete(key_outcomes_list)


@connected_and_enabled(backup=None)
def get_update_outcome(_id: str) -> Optional[Dict]:
  stored_outcomes = list_outcomes()
  finder = lambda o: o.get('update_id') == _id
  return next(filter(finder, stored_outcomes), None)


@connected_and_enabled
def store_mfst_var_assign():
  pass

def upload_meta():
  tam = config_man.tam(force_reload=True)
  last_updated = config_man.last_updated(force_reload=True)
  install_uuid = config_man.install_uuid(force_reload=True)

  payload = {
    'tam_type': tam.get('type'),
    'tam_uri': tam.get('uri'),
    'tam_ver': tam.get('version'),
    'last_updated': str(last_updated)
  }

  endpoint = f'/installs/{install_uuid}'
  response = hub_client.patch(endpoint, payload)
  return response.status_code < 205

def connect() -> Optional[Redis]:
  if broker.is_in_cluster_auth():
    manifest_vars = config_man.flat_manifest_vars()
    host = manifest_vars.get('telem_storage.host')
    port = manifest_vars.get('telem_storage.port')
  else:
    host = 'localhost'
    port = 6379
  if host:
    return Redis(host=host, port=int(port or 6379))
  else:
    return None
