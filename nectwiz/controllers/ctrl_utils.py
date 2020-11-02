import json

from flask import request

from nectwiz.core.core import utils


def jparse():
  if utils.is_in_cluster():
    payload_str = request.data.decode('unicode-escape')
    truncated = payload_str[1:len(payload_str) - 1]
    as_dict = json.loads(truncated)
    return utils.unmuck_primitives(as_dict)
  else:
    return utils.unmuck_primitives(request.json)
