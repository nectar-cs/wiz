import json
from typing import Dict, Any

from flask import request
from k8kat.auth.kube_broker import broker

from nectwiz.core.core import utils


def jparse():
  if broker.is_in_cluster_auth():
    payload_str = request.data.decode('unicode-escape')
    truncated = payload_str[1:len(payload_str) - 1]
    as_dict = json.loads(truncated)
    return utils.unmuck_primitives(as_dict)
  else:
    return utils.unmuck_primitives(request.json)
