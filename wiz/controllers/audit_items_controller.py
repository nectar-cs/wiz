from flask import Blueprint

REST_PATH = '/api/audit_items'

controller = Blueprint('audit_items_controller', __name__)

@controller.route(REST_PATH)
def index():
  query_params = None
