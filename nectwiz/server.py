import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from k8_kat.auth.kube_broker import BrokerConnException, broker

from nectwiz.controllers import operations_controller, status_controller, \
  app_controller, chart_variables_controller, resources_controller

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

def start():
  broker.connect()
  app.config["cmd"] = ["bash"]
  port = 5000
  app.run(host='0.0.0.0', port=port)
