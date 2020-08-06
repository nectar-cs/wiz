import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from k8_kat.auth.kube_broker import BrokerConnException, broker
from wiz.controllers import operations_controller, status_controller, \
  app_controller, chart_variables_controller, resources_controller
from wiz.core.wiz_app import wiz_app

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

controllers = [
  status_controller,
  operations_controller,
  app_controller,
  resources_controller,
  chart_variables_controller
]

for controller in controllers:
  app.register_blueprint(controller.controller)


CORS(app)


@app.errorhandler(BrokerConnException)
def all_exception_handler(error):
  return jsonify(dict(
    error='could not connect to Kubernetes API',
    reason=str(error)
  )), 500


@app.before_request
def ensure_broker_connected():
  if "/api/status" not in request.path:
    # broker.check_connected_or_raise()
    pass


@app.before_request
def apply_globals_from_headers():
  if request.headers.get('Wizns'):
    wiz_app.ns = request.headers.get('Wizns')
    wiz_app.reload_install_uuid()

  if request.headers.get('Tami-image'):
    wiz_app.tami_name = request.headers.get('Tami-Image')

  if request.headers.get('Tami-args'):
    wiz_app.tami_args = request.headers.get('Tami-Args')


def start():
  broker.connect()
  app.config["cmd"] = ["bash"]
  port = 5000 if broker.is_in_cluster_auth() else 5001
  app.run(host='0.0.0.0', port=port)
