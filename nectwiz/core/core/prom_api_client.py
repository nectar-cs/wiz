import json
import time
import traceback
from datetime import datetime, timedelta
from json import JSONDecodeError
from typing import Optional, Dict, Tuple

import requests
from k8kat.res.svc.kat_svc import KatSvc

from nectwiz.core.core.config_man import config_man

_cache_obj = dict(
  svc=None
)


def compute_instant(*args):
  path, args = instant_path_and_args(*args)
  return do_invoke(path, args)


def compute_series(*args):
  path, args = gen_series_args(*args)
  return do_invoke(path, args)


def do_invoke(path: str, args: Dict) -> Optional[Dict]:
  svc = find_prom_svc()
  if svc:
    return invoke_svc(svc, path, args)
  else:
    return None


def invoke_svc(svc, path, args) -> Optional[Dict]:
  resp = svc.proxy_get(path, args) or {}
  print(args)
  if resp.get('status', 500) < 300:
    try:
      return json.loads(resp.get('body'))
    except JSONDecodeError:
      print(traceback.format_exc())
      print(resp.get('body'))
      print(f"[nectwiz:prom_client] svc resp decode ^^ fail")
      return None


def invoke_pure_http(path, args) -> Optional[Dict]:
  arg2s = lambda arg: f"{arg[0]}={arg[1]}"
  url = f"{path}?{'&'.join(list(map(arg2s, args.items())))}"
  # noinspection PyBroadException
  try:
    return requests.get(url).json()
  except:
    print(traceback.format_exc())
    print(f"[nectwiz:prom_client] pure http invoke ^^ fail")
    return None


def instant_path_and_args(query: str, ts: datetime = None) -> Tuple:
  base = '/api/v1/query'
  ts = ts or datetime.now()
  args = {
    'query': query,
    'time': fmt_time(ts)
  }
  return base, sanitize_params(args)


def gen_series_args(query: str, step=None, t0=None, tn=None) -> Tuple:
  base = '/api/v1/query_range'
  t_start = t0 or datetime.now() - timedelta(days=7)
  t_end = tn or datetime.now()
  args = {
    'query': query,
    'start': fmt_time(t_start),
    'end': fmt_time(t_end),
    'step': step or '1h'
  }
  return base, sanitize_params(args)


def fmt_time(timestamp: datetime):
  return int(time.mktime(timestamp.timetuple()))


def sanitize_params(args: Dict) -> Dict:
  # return {k: urllib.parse.quote(v) for k, v in args.items()}
  return args


def find_prom_svc() -> Optional[KatSvc]:
  if not _cache_obj['svc']:
    prefs = config_man.prefs().get('prom') or {}
    prom_ns = prefs.get('ns', def_svc_ns)
    prom_name = prefs.get('name', def_svc_name)
    _cache_obj['svc'] = KatSvc.find(prom_name, prom_ns)
    if not _cache_obj['svc']:
      print(f"[nectwiz:prom_client] svc [{prefs}] not found")

  return _cache_obj['svc']


def conn_type():
  if not _cache_obj['type']:
    prefs = config_man.prefs().get('prom') or {}
    if prefs.get('type'):
      _cache_obj['type'] = prefs.get('type')
  return _cache_obj['type'] or 'svc'


def_svc_ns = "monitoring"
def_svc_name = "prometheus-prometheus-oper-prometheus"
