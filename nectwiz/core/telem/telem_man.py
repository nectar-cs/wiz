from typing import Optional, Dict

from k8kat.auth.kube_broker import broker
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.results import InsertOneResult

from nectwiz.core.core import hub_client
from nectwiz.core.core.config_man import config_man

key_conn_obj_db = 'db'
key_events = 'events'
key_config_backups = 'config_backups'
key_errors = 'errors'
key_synced = 'synced'

key_telem_strategy = 'telem_storage.strategy'
strategy_disabled = 'disabled'
strategy_internal = 'managed_pvc'
connection_obj = {key_conn_obj_db: None}


def _database() -> Optional[Database]:
  return connection_obj[key_conn_obj_db]


def get_db() -> Optional[Database]:
  if not _database():
    is_local_dev = not broker.is_in_cluster_auth()
    strategy = config_man.manifest_var(key_telem_strategy)
    if is_local_dev or not strategy == strategy_disabled:
      connection_obj[key_conn_obj_db] = connect()
  return _database()


def is_storage_ready() -> bool:
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


def store_error(error: Dict) -> InsertOneResult:
  return store_list_element(key_errors, error)


def store_event(event: Dict) -> InsertOneResult:
  return store_list_element(key_events, event)


def store_config_backup(outcome: Dict):
  return store_list_element(key_config_backups, outcome)


def list_errors():
  return list_records(key_errors)


def list_outcomes():
  return list_records(key_events)


def list_config_backups():
  return list_records(key_config_backups)


@connected_and_enabled(backup=None)
def store_list_element(list_key: str, item: Dict) -> InsertOneResult:
  item = {**item, key_synced: False}
  return _database()[list_key].insert_one(item)


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


def upload_all_meta():
  upload_status()
  if is_storage_ready():
    upload_events_and_errors()
  else:
    print("[nectwiz::telem_man] db unavailable, skip upload events/errors")


def upload_status() -> bool:
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

  print(f"[nectwiz::telem_man] stat -> {hub_client.backend_host()} {payload}")
  endpoint = f'/installs/sync'
  response = hub_client.post(endpoint, dict(data=payload))
  print(f"[nectwiz::telem_man] upload status resp {response}")
  return response.status_code < 205


def upload_events_and_errors():
  for collection_name in [key_errors, key_events]:
    items = get_db()[collection_name].find({key_synced: False})
    for item in items:
      raw_id = item['_id']
      del item['_id']
      item['original_id'] = str(raw_id)
      hub_key = f'wiz_{collection_name}'[0:-1]
      payload = {hub_key: item}
      resp = hub_client.post(f'/{hub_key}s', payload)
      if resp.ok:
        query = {'_id': raw_id}
        patch = {'$set': {key_synced: True}}
        get_db()[collection_name].update_one(query, patch)
      else:
        print(f"[nectwiz::telem_man] failed ${collection_name} ${item}: ")
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

  try:
    client = MongoClient(
      host=host,
      port=port or 27017,
      connectTimeoutMS=1_000,
      serverSelectionTimeoutMS=1_000
    )
    client.server_info()
    return client['database']
  except ServerSelectionTimeoutError:
    print(f"[nectwiz::telem_man] MongoDB conn({host}, {port}) failed")
    return None


def in_cluster_conn_defaults() -> Dict:
  # strategy = config_man.manifest_var(key_telem_strategy)
  # if strategy == strategy_internal:
  return dict(host='telem-db', port=27017)
  # else:
  #   return dict(host=None, port=None)
