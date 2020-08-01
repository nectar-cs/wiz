import requests

from wiz.core import utils
from wiz.core.telem.ost import OperationState
from wiz.core.wiz_globals import wiz_app
from wiz.serializers import operation_state_ser


def backend_host():
  if utils.is_dev():
    return 'http://localhost:3000'
  else:
    return 'https://api.codenectar.com'


def upload_operation_outcome(op_state: OperationState):
  install_uuid = wiz_app.install_uuid
  payload = operation_state_ser.serialize(op_state)
  ep = f'/api/cli/installs/{install_uuid}/operation_outcomes'
  resp = requests.post(f'{backend_host()}{ep}', payload)
  print(resp)
  print(resp.text)
  return True
