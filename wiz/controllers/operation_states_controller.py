from flask import Blueprint, jsonify

from wiz.core.audit_sink import AuditSink, audit_sink
from wiz.core.osr import operation_states
from wiz.model.operations import serial as operation_serial

REST_PATH = '/api/operation_states'

controller = Blueprint('operation_states_controller', __name__)

@controller.route(REST_PATH)
def index():
  serialized = list(map(operation_serial.state, operation_states))
  return jsonify(data=serialized)


@controller.route(REST_PATH, methods=['POST'])
def create():
  serialized = list(map(operation_serial.state, operation_states))
  return jsonify(data=serialized)


@controller.route(f'{REST_PATH}/<op_state_id>', methods=['POST'])
def delete(op_state_id: str):
  serialized = list(map(operation_serial.state, operation_states))
  return jsonify(data=serialized)


@controller.route(f'{REST_PATH}/<op_state_id>/mark_finished', methods=['POST'])
def mark_finished(op_state_id: str):
  audit_sink.save_operation_outcome()
