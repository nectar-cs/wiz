from flask import Blueprint, jsonify

from k8_kat.auth.kube_broker import broker

controller = Blueprint('status_controller', __name__)


@controller.route('/api/ping')
def ping():
  return jsonify(ping='pong')


@controller.route('/api/status')
def status():
  return jsonify(
    is_k8_kat_connected=broker.is_connected,
    last_k8_kat_conn_error=broker.last_error,
    connect_config=broker.connect_config
  )
