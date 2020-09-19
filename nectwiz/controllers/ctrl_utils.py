import json

from flask import request
from k8kat.auth.kube_broker import broker


def jparse():
  if broker.is_in_cluster_auth():
    payload_str = request.data.decode('unicode-escape')
    truncated = payload_str[1:len(payload_str) - 1]
    return json.loads(truncated)
  else:
    return request.json
