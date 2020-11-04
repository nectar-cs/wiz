from typing import Optional, Dict

from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.results import InsertOneResult

from nectwiz.core.core import hub_client, utils
from nectwiz.core.core.config_man import config_man

key_conn_obj_db = 'db'
key_synced = 'synced'

key_events = 'events'
key_config_backups = 'config_backups'
key_errors = 'errors'

key_telem_strategy = 'telem_storage.strategy'
strategy_disabled = 'disabled'
strategy_internal = 'managed_pvc'
connection_obj = {key_conn_obj_db: None}


def _database() -> Optional[Database]:
  return connection_obj[key_conn_obj_db]


def get_db() -> Optional[Database]:
  if not _database():
    strategy = config_man.manifest_var(key_telem_strategy)
    if utils.is_out_of_cluster() or not strategy == strategy_disabled:
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


def store_config_backup(outcome: Dict) -> InsertOneResult:
  return store_list_element(key_config_backups, outcome)


def list_errors():
  return list_records(key_errors)


def list_events():
  return list_records(key_events)


def list_config_backups():
  return list_records(key_config_backups)


def get_config_backup(record_id) -> Optional[Dict]:
  return find_record_by_id(key_config_backups, record_id)


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
def find_record_by_id(list_key,  record_id):
  collection = _database()[list_key]
  return collection.find_one({'_id': ObjectId(record_id)})


def upload_all_meta():
  upload_status()
  if is_storage_ready():
    upload_events_and_errors()
  else:
    print("[nectwiz:telem_man] db unavailable, skip upload events/errors")


def upload_status() -> bool:
  if config_man.is_training_mode():
    return False

  from nectwiz.model.adapters.status_adapter import StatusAdapter
  status_computer: StatusAdapter = StatusAdapter.descendent_or_self()
  status_computer.compute_and_commit_status()

  tam = config_man.tam()
  wiz = config_man.wiz()

  payload = {
    'status': config_man.application_status(),
    'tam_type': tam.get('type'),
    'tam_uri': tam.get('uri'),
    'tam_version': tam.get('version'),
    'wiz_version': wiz.get('version'),
    'synced_at': str(config_man.last_updated())
  }

  print(f"[nectwiz:telem_man] stat -> {hub_client.backend_host()} {payload}")
  endpoint = f'/installs/sync'
  response = hub_client.post(endpoint, dict(data=payload))
  print(f"[nectwiz:telem_man] upload status resp {response}")
  return response.status_code < 205


def upload_events_and_errors():
  if config_man.is_training_mode():
    return False

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
        print(f"[nectwiz:telem_man] failed ${collection_name} ${item}: ")
        print(resp)


def connect() -> Optional[Database]:
  host = 'localhost'
  port = 27017
  if utils.is_in_cluster():
    manifest_vars = config_man.flat_manifest_vars()
    host = manifest_vars.get('telem_db.host', 'telem-db')
    port = manifest_vars.get('telem_db.port', 27017)
  try:
    client = MongoClient(
      host=host,
      port=int(port),
      connectTimeoutMS=1_000,
      serverSelectionTimeoutMS=1_000
    )
    client.server_info()
    return client['database']
  except ServerSelectionTimeoutError:
    print(f"[nectwiz:telem_man] MongoDB[{host}, {port}] conn failed")
    if utils.is_out_of_cluster():
      print("For local dev server, run MongoDB on localhost:27017")
    return None
