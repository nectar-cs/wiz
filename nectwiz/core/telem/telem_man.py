import functools
from typing import Optional

from k8kat.auth.kube_broker import broker
from redis import Redis

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateOutcome

STRATEGY_DISABLED = 'disabled'

connection_obj = dict(
  redis=None
)


def redis() -> Optional[Redis]:
  return connection_obj['redis']


def connected_and_enabled(backup=None):
  def actual_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      manifest_vars = config_man.flat_manifest_vars()
      strategy = manifest_vars.get('telem_storage.strategy')
      if strategy not in [STRATEGY_DISABLED, None]:
        if not redis():
          connection_obj['redis'] = connect()
        if redis():
          return func(*args, **kwargs)
        else:
          return backup
      else:
        return backup
    return wrapper
  return actual_decorator


@connected_and_enabled
def store_update_outcome(outcome: UpdateOutcome):
  redis()


@connected_and_enabled(backup=[])
def list_update_outcomes():
  pass


@connected_and_enabled
def get_update_outcome(_id: str):
  pass


@connected_and_enabled
def store_mfst_var_assign():
  pass


def connect() -> Optional[Redis]:
  manifest_vars = config_man.flat_manifest_vars()
  host = manifest_vars.get('telem_storage.host')
  port = manifest_vars.get('telem_storage.port')
  if host:
    return Redis(host=host, port=int(port or 6379))
  else:
    return None
