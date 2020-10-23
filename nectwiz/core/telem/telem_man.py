from typing import Optional, Dict

from k8kat.auth.kube_broker import broker
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

from nectwiz.core.core import hub_client
from nectwiz.core.core.config_man import config_man

key_events = 'events'
key_config_backups = 'config_backups'
key_errors = 'errors'
key_synced = 'synced'

key_telem_strategy = 'telem_storage.strategy'
strategy_disabled = 'disabled'
strategy_internal = 'managed_pvc'
connection_obj = dict(database=None)


def _database() -> Optional[Database]:
  return connection_obj['db']


def get_db() -> Optional[Database]:
  if not _database():
    is_local_dev = not broker.is_in_cluster_auth()
    strategy = config_man.manifest_var(key_telem_strategy)
    if is_local_dev or not strategy == strategy_disabled:
      connection_obj['db'] = connect()
  return _database()


def is_on() -> bool:
  return True if get_db() else False


def parametrized(dec):
  def layer(*args, **kwargs):
    def repl(f):
      return dec(f, *args, **kwargs)
    return repl
  return layer


@parametrized
def connected_and_enabled(func, backup=None):
  def aux(*xs, **kws):
    return func(*xs, **kws) if get_db() else backup
  return aux


def store_error(error: Dict) -> Dict:
  return store_list_element(key_errors, error)


def store_event(outcome: Dict) -> Dict:
  return store_list_element(key_events, outcome)


def store_config_backup(outcome: Dict):
  return store_list_element(key_config_backups, outcome)


def list_errors():
  return list_records(key_errors)


def list_outcomes():
  return list_records(key_events)


def list_config_backups():
  return list_records(key_config_backups)


@connected_and_enabled(backup=None)
def store_list_element(list_key: str, item: Dict) -> Dict:
  item = {**item, key_synced: False}
  return _database()[list_key].insert_one(list_key, item)


@connected_and_enabled(backup=[])
def list_records(key: str):
  return list(_database()[key].find())


@connected_and_enabled(backup=[])
def clear_update_outcomes():
  _database().delete(key_events)


@connected_and_enabled(backup=None)
def get_update_outcome(_id: str) -> Optional[Dict]:
  stored_outcomes = list_outcomes()
  finder = lambda o: o.get('update_id') == _id
  return next(filter(finder, stored_outcomes), None)


@connected_and_enabled
def store_mfst_var_assign():
  pass


def upload_meta() -> bool:
  tam = config_man.tam(force_reload=True)
  wiz = config_man.wiz(force_reload=True)
  last_updated = config_man.last_updated(force_reload=True)

  payload = {
    'tam_type': tam.get('type'),
    'tam_uri': tam.get('uri'),
    'tam_version': tam.get('version'),
    'wiz_version': wiz.get('version'),
    'synced_at': str(last_updated)
  }

  print("SEND")
  print(payload)
  endpoint = f'/installs/sync'
  response = hub_client.post(endpoint, dict(data=payload))
  try:
    print("GET")
    print(response.json())
  except:
    print('telem sync non-json response')
  return response.status_code < 205


def upload_events_and_errors():
  events = _database()[key_events].find({key_synced: False})
  errors = _database()[key_errors].find({key_synced: False})
  item_sets = [('events', events), ('errors', errors)]

  for _set in item_sets:
    for set_name, item in _set:
      resp = hub_client.post(f'/telem/{set_name}', item)
      if resp.ok:
        _database()[set_name].update_one({'$set': {key_synced: True}})
      else:
        print(f"[nectwiz::telem_man] failed ${set_name} ${item}: ")
        print(resp)


def connect() -> Optional[Database]:
  if broker.is_in_cluster_auth():
    manifest_vars = config_man.flat_manifest_vars()
    defaults = in_cluster_conn_defaults()
    host = manifest_vars.get('telem_db.host', defaults['host'])
    port = manifest_vars.get('telem_db.port', defaults['port'])
  else:
    host = 'localhost'
    port = 27017
  if host:
    try:
      client = MongoClient(
        host=host,
        port=port or 27017,
        serverSelectionTimeoutMS=5_000
      )
      return client['database']
    except ServerSelectionTimeoutError:
      print(f"[nectwiz::telem_man] MongoDB conn({host}, {port}) failed")
      return None
  else:
    return None


def in_cluster_conn_defaults() -> Dict:
  strategy = config_man.manifest_var(key_telem_strategy)
  if strategy == strategy_internal:
    return dict(host='telem-db', port=6379)
  else:
    return dict(host=None, port=None)
