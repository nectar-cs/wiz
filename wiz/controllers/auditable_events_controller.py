from flask import Blueprint, jsonify


REST_PATH = '/api/audit_items'

controller = Blueprint('auditable_events_controller', __name__)


@controller.route(REST_PATH)
def index():
  query_params = None


@controller.route(f'{REST_PATH}/upload-all', methods=['POST'])
def upload_all():
  # todo start background job
  return jsonify(status='pending')
