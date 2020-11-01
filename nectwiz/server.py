import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from k8kat.auth.kube_broker import BrokerConnException, broker

from nectwiz.controllers import operations_controller, status_controller, \
  app_controller, manifest_variables_controller, resources_controller, updates_controller, errors_controller, \
  telem_controller
from nectwiz.core.core import utils
from nectwiz.core.core.config_man import coerce_ns

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

controllers = [
  status_controller,
  operations_controller,
  app_controller,
  resources_controller,
  telem_controller,
  updates_controller,
  manifest_variables_controller,
  errors_controller
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
def read_dev_ns():
  coerced_ns = request.headers.get('Wizns')
  if coerced_ns:
    if utils.is_local_dev_server():
      coerce_ns(coerced_ns)
    else:
      print(f"[nectwiz::server] set-ns from header env={utils.run_env()}!")


def start():
  app.config["cmd"] = ["bash"]
  app.run(host='0.0.0.0', port=5000)
