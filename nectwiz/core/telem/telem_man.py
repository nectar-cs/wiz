import json
from typing import Optional

from k8kat.auth.kube_broker import broker
from redis import Redis

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateOutcome

STRATEGY_DISABLED = 'disabled'
key_var_assign = 'variable_assignment'
key_update_outcomes = 'update_outcomes'

connection_obj = dict(
  redis=None
)


def redis() -> Optional[Redis]:
  return connection_obj['redis']


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
      if not redis():
        connection_obj['redis'] = connect()
      if redis():
        return func(*xs, **kws)
      else:
        return backup
    else:
      return backup
  return aux


@connected_and_enabled(backup=None)
def store_update_outcome(outcome: UpdateOutcome):
  stored_outcomes = list_update_outcomes()
  stored_outcomes.append(outcome)
  redis().set(key_update_outcomes, json.dumps(stored_outcomes))


@connected_and_enabled(backup=[])
def list_update_outcomes():
  return json.loads(redis().get(key_update_outcomes) or '[]')


@connected_and_enabled(backup=[])
def clear_update_outcomes():
  redis().delete(key_update_outcomes)


@connected_and_enabled(backup=None)
def get_update_outcome(_id: str) -> Optional[UpdateOutcome]:
  stored_outcomes = list_update_outcomes()
  finder = lambda o: o.get('update_id') == _id
  return next(filter(finder, stored_outcomes), None)


@connected_and_enabled
def store_mfst_var_assign():
  pass


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
