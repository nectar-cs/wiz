from flask import Blueprint, jsonify, request

from nectwiz.core.telem.audit_sink import audit_sink
from nectwiz.core.telem.ost import OperationState

REST_PATH = '/api/audit_items'

controller = Blueprint('auditable_events_controller', __name__)


@controller.route(f"{REST_PATH}/persist-operation-outcome")
def persist_operation_outcome():
  ost_id = request.json['ost_id']
  op_state = OperationState.find(ost_id)

  if op_state:
    audit_sink.save_op_outcome(op_state, True)



@controller.route(REST_PATH)
def index():
  query_params = None


@controller.route(f'{REST_PATH}/upload-all', methods=['POST'])
def upload_all():
  # todo start background job
  return jsonify(status='pending')
