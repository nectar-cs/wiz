from typing import List

from nectwiz.core import hub_client
from nectwiz.core.telem.ost import OperationState, operation_states
from nectwiz.core.wiz_app import wiz_app
from nectwiz.serializers import operation_state_ser


def upload_operation_outcomes():
  victim_osts: List[str] = []
  OperationState.prune()
  for op_state in operation_states:
    if upload_operation_outcome(op_state):
      victim_osts.append(op_state.ost_id)

  for victim_ost in victim_osts:
    OperationState.delete_if_exists(victim_ost)


def upload_operation_outcome(op_state: OperationState) -> bool:
  install_uuid = wiz_app.install_uuid(force=True)
  if install_uuid:
    serialized_outcome = operation_state_ser.serialize(op_state)
    ep = f'/installs/{install_uuid}/operation_outcomes'
    resp = hub_client.post(ep, dict(data=serialized_outcome))
    return resp.status_code < 300
  else:
    return False
