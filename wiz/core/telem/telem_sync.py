import requests

from wiz.core import utils, hub_client
from wiz.core.telem.ost import OperationState, operation_states
from wiz.core.wiz_app import wiz_app
from wiz.serializers import operation_state_ser


def upload_operation_outcomes():
  for op_state in operation_states:
    upload_operation_outcome(op_state)


def upload_operation_outcome(op_state: OperationState, delete=False):
  if wiz_app.install_uuid:
    serialized_outcome = operation_state_ser.serialize(op_state)
    ep = f'/installs/{wiz_app.install_uuid}/operation_outcomes'
    print(f"TO {ep} ----> {serialized_outcome}")
    resp = hub_client.post(ep, dict(data=serialized_outcome))
    print(resp)
    return True
