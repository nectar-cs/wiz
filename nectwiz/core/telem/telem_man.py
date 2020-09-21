import functools
from typing import Optional

from redis import Redis

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateOutcome

connection_obj = dict(
  redis=None
)


def redis() -> Optional[Redis]:
  return connection_obj['redis']


def connected(backup=None):
  def actual_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      if not redis():
        connection_obj['redis'] = connect()
      if redis():
        return func(*args, **kwargs)
      else:
        return backup
    return wrapper
  return actual_decorator


@connected
def store_update_outcome(outcome: UpdateOutcome):
  redis()


@connected(backup=[])
def list_update_outcomes():
  pass


@connected
def get_update_outcome(_id: str):
  pass


@connected
def store_mfst_var_assign():
  pass


def connect() -> Optional[Redis]:
  prefs = config_man.prefs()
  host, port = prefs.get('telem_db_host'), prefs.get('telem_db_port')
  if host:
    port = int(port or 6379)
    return Redis(host=host, port=port)
  else:
    return None
