from typing import List

from nectwiz.core.core import hub_client, config_man
from nectwiz.core.core.config_man import config_man
from nectwiz.model.operations.operation_state import OperationState, operation_states
from nectwiz.serializers import operation_state_ser


def upload_meta():
  tam = config_man.read_tam()
  last_updated_checked = config_man.read_last_update_checked()
  payload = {
    'tam_type': tam['type'],
    'tam_uri': tam['uri'],
    'tam_ver': tam['version'],
    'last_update_check': last_updated_checked
  }

  endpoint = f'/installs/{config_man.install_uuid()}'
  hub_client.patch(endpoint, payload)


def upload_operation_outcomes() -> int:
  victim_osts: List[str] = []
  OperationState.prune()
  for op_state in operation_states:
    upload_operation_outcome(op_state)
    victim_osts.append(op_state.ost_id)

  for victim_ost in victim_osts:
    OperationState.delete_if_exists(victim_ost)

  return len(victim_osts)


def upload_operation_outcome(op_state: OperationState) -> bool:
  install_uuid = config_man.install_uuid(True)
  if install_uuid:
    serialized_outcome = operation_state_ser.serialize(op_state)
    ep = f'/installs/{install_uuid}/operation_outcomes'
    resp = hub_client.post(ep, dict(data=serialized_outcome))
    return resp.status_code < 300
  else:
    return False
