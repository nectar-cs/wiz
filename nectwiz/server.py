import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from k8kat.auth.kube_broker import BrokerConnException

from nectwiz.controllers import operations_controller, status_controller, \
  app_controller, chart_variables_controller, resources_controller
from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man

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
def read_dev_ns():
  if request.headers.get('Wizns'):
    if utils.is_dev():
      config_man._ns = request.headers.get('Wizns')
    else:
      print("[nectwiz::server] danger client tried setting Wizns!")


def start():
  app.config["cmd"] = ["bash"]
  app.run(host='0.0.0.0', port=5000)
