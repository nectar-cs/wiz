from typing import Dict

from flask import Blueprint, jsonify, request

from k8_kat.auth.kube_broker import broker
from wiz.core.telem.telem_perms import TelemPerms


controller = Blueprint('status_controller', __name__)


@controller.route('/api/ping')
def ping():
  return jsonify(ping='pong')


@controller.route('/api/status/telem-perms')
def status_telem_perms():
  raw_perms: Dict = TelemPerms().user_perms()
  return jsonify(data=raw_perms)


@controller.route('/api/status/telem-perms', methods=['POST'])
def status_patch_telem_perms():
  patch_values: Dict = request.json['data']
  TelemPerms().patch(patch_values)
  return jsonify(data=TelemPerms().user_perms())


@controller.route('/api/status')
def status():
  return jsonify(
    is_k8_kat_connected=broker.is_connected,
    last_k8_kat_conn_error=broker.last_error,
    connect_config=broker.connect_config
  )
