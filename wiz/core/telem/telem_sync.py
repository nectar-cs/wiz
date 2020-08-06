import requests

from wiz.core import utils
from wiz.core.telem.ost import OperationState
from wiz.core.wiz_app import wiz_app
from wiz.serializers import operation_state_ser


def backend_host():
  if utils.is_dev():
    return 'http://localhost:3000'
  else:
    return 'https://api.codenectar.com'


def upload_operation_outcome(op_state: OperationState):
  install_uuid = wiz_app.install_uuid
  serialized_outcome = operation_state_ser.serialize(op_state)
  payload = dict(data=serialized_outcome)
  ep = f'/api/cli/installs/{install_uuid}/operation_outcomes'
  resp = requests.post(f'{backend_host()}{ep}', json=payload)
  return True
