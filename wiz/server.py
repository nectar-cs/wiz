import os

from flask import Flask, jsonify, request
from flask_cors import CORS

# from utils.bay_map import BayMap
from k8_kat.auth.kube_broker import BrokerConnException, broker
from wiz.controllers import setup_controller
from wiz.model.wizard import Wizard

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

controllers = [
  setup_controller
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
    broker.check_connected_or_raise()

def model_class() -> Wizard:
  return app.config['model_class']

def start(_model_class):
  broker.connect()
  app.config['model_class'] = _model_class
  app.config["cmd"] = ["bash"]
  app.run(host='0.0.0.0', port=5001)
