from typing import Dict

from flask import Blueprint, jsonify, request

from k8kat.auth.kube_broker import broker

from nectwiz.core import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.telem.telem_perms import TelemPerms
from nectwiz.core.wiz_app import wiz_app

controller = Blueprint('status_controller', __name__)


@controller.route('/api/ping')
def ping():
  return jsonify(ping='pong')


@controller.route('/api/status/telem-perms')
def status_telem_perms():
  """
  Returns the default user perms.
  :return: serialized user perms.
  """
  raw_perms: Dict = TelemPerms().user_perms()
  return jsonify(data=raw_perms)


@controller.route('/api/status/telem-perms', methods=['POST'])
def status_patch_telem_perms():
  """
  Patches the user perms.
  :return: patched user perms.
  """
  patch_values: Dict = request.json['data']
  TelemPerms().patch(patch_values)
  return jsonify(data=TelemPerms().user_perms())


@controller.route('/api/status')
def status():
  """
  Checks Wiz's status.
  :return: dict containing status details.
  """
  return jsonify(
    is_healthy=broker.is_connected,
    cluster_connection=dict(
      is_k8kat_connected=broker.is_connected,
      connect_config=broker.connect_config
    ),
    ns=wiz_app.ns(),
    master_cmap_present=config_man.master_cmap() is not None,
    tam_config=wiz_app.tam(),
    tam_defaults=wiz_app.tam_defaults(),
    tam_variables=config_man.read_tam_vars()
  )


@controller.route('/api/status/templated_manifest')
def templated_manifest():
  return jsonify(
    data=tam_client().load_tpd_manifest()
  )
