import requests

from wiz.core import utils
from wiz.core.telem.ost import OperationState
from wiz.core.wiz_app import wiz_app
from wiz.serializers import operation_state_ser


def upload_operation_outcomes():
  for op_state in operation_states:
    upload_operation_outcome(op_state)


def upload_operation_outcome(op_state: OperationState, delete=False):
  install_uuid = wiz_app.install_uuid
  serialized_outcome = operation_state_ser.serialize(op_state)
  ep = f'/api/cli/installs/{install_uuid}/operation_outcomes'
  resp = hub_client.post(ep, json=dict(data=serialized_outcome))
  print(resp)
  return True
