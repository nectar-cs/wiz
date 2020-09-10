from typing import Dict

from flask import Blueprint, jsonify, request

from k8kat.auth.kube_broker import broker

from nectwiz.core.core import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.telem.telem_perms import TelemPerms
from nectwiz.core.core.wiz_app import wiz_app
from nectwiz.model.hook.hook import Hook

controller = Blueprint('status_controller', __name__)


@controller.route('/api/status/on-uninstall', methods=['POST'])
def trigger_uninstall():
  uninstall_hooks = Hook.list_for_trigger("before", "uninstall")
  for hook in uninstall_hooks:
    pass



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

  if not is_healthy():
    broker.connect()

  return jsonify(
    sanity='1',
    is_healthy=is_healthy(),
    cluster_connection=dict(
      is_k8kat_connected=broker.is_connected,
      connect_config=broker.connect_config
    ),
    ns=wiz_app.ns(),
    tam_config=wiz_app.tam(),
    tam_defaults=wiz_app.tam_defaults(),
    tam_variables=config_man.read_man_vars()
  )


@controller.route('/api/status/templated_manifest')
def templated_manifest():
  return jsonify(
    data=tam_client().load_tpd_manifest()
  )


def is_healthy() -> bool:
  if broker.is_connected:
    return config_man.master_cmap() is not None
  else:
    return False


