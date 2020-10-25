from typing import Dict

from flask import Blueprint, jsonify
from k8kat.auth.kube_broker import broker

from nectwiz.core.telem import telem_man
from nectwiz.model.base.wiz_model import models_man, default_descriptors, configs_for_kinds, WizModel

from nectwiz.controllers.ctrl_utils import jparse
from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.telem.telem_perms import TelemPerms

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
  patch_values: Dict = jparse()['data']
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
    sanity='2',
    is_healthy=is_healthy(),
    telem_connected=telem_man.is_storage_ready(),
    install_uuid=config_man.install_uuid(),
    cluster_connection=dict(
      is_k8kat_connected=broker.is_connected,
      connect_config=broker.connect_config
    ),
    ns=config_man.ns(),
    tam_config=config_man.tam(),
    wiz_config=config_man.wiz(),
    tam_defaults=config_man.tam_defaults(),
    tam_variables=config_man.read_manifest_vars()
  )


@controller.route('/api/status/templated_manifest')
def templated_manifest():
  return jsonify(
    data=tam_client().load_templated_manifest()
  )


@controller.route('/api/status/descriptors')
def dump_descriptors():
  descriptors = models_man.descriptors()
  return jsonify(data=descriptors)


@controller.route('/api/status/descriptors/<kind>')
def dump_descriptors_by_kind(kind):
  master = WizModel.inflate(kind)
  cls_pool = master.lteq_classes(models_man.classes())
  descriptors = configs_for_kinds(models_man.descriptors(), cls_pool)
  return jsonify(data=descriptors)


@controller.route('/api/status/descriptors/<kind>/<res_id>')
def dump_descriptor(kind, res_id):
  model_class: WizModel = WizModel.kind2cls(kind)
  instance = model_class.inflate(res_id)
  return jsonify(data=instance.to_dict())


@controller.route('/api/status/default-descriptors')
def dump_default_descriptors():
  descriptors = default_descriptors()
  return jsonify(data=descriptors)


def is_healthy() -> bool:
  if broker.is_connected:
    return config_man.master_config_map() is not None
  else:
    return False


