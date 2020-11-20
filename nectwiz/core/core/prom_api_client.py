import json
import time
import traceback
from datetime import datetime, timedelta
from json import JSONDecodeError
from typing import Optional, Dict, Tuple
from urllib.parse import quote

import requests
from k8kat.res.svc.kat_svc import KatSvc

from nectwiz.core.core.config_man import config_man

_cache_obj = dict(
  prom_config={},
  svc=None
)


def compute_instant(*args):
  path, args = instant_path_and_args(*args)
  return do_invoke(path, args)


def compute_series(*args):
  path, args = gen_series_args(*args)
  return do_invoke(path, args)


def do_invoke(path: str, args: Dict) -> Optional[Dict]:
  _conn_type = conn_type()
  if _conn_type == 'proxy':
    svc = find_prom_svc()
    return invoke_svc(svc, path, args) if svc else None
  elif _conn_type == 'url':
    return invoke_url(path, args)
  else:
    return None


def invoke_url(path, args: Dict) -> Optional[Dict]:
  base_url = prom_config().get('url')
  full_url = f"{base_url}{path}?{dict_args2str(args)}"
  resp = requests.get(full_url)
  if resp.ok:
    try:
      return resp.json()
    except JSONDecodeError:
      print(traceback.format_exc())
      print(resp)
      print(f"[nectwiz:prom_client] svc resp decode ^^ fail")
      return None


def dict_args2str(args: Dict) -> str:
  as_list = [f"{k}={quote(v)}" for k, v in list(args.items())]
  return "&".join(as_list)


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
  return base, args


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
  return base, args


def fmt_time(timestamp: datetime):
  return int(time.mktime(timestamp.timetuple()))


def find_prom_svc() -> Optional[KatSvc]:
  if not _cache_obj['svc']:
    prefs = prom_config()
    prom_ns = prefs.get('ns', def_svc_ns)
    prom_name = prefs.get('name', def_svc_name)
    _cache_obj['svc'] = KatSvc.find(prom_name, prom_ns)
    if not _cache_obj['svc']:
      print(f"[nectwiz:prom_client] svc [{prefs}] not found")
  return _cache_obj['svc']


def prom_config() -> Dict:
  if not _cache_obj['prom_config']:
    root = config_man.prefs().get('prom_config') or {}
    _cache_obj['prom_config'] = root
  return _cache_obj['prom_config'] or {}


def conn_type() -> str:
  return prom_config().get('type')


def_svc_ns = "monitoring"
def_svc_name = "prometheus-prometheus-oper-prometheus"
