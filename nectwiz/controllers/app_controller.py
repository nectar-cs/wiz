from flask import Blueprint, jsonify

from nectwiz.core.job.job_client import enqueue_action, find_job, ternary_job_status
from nectwiz.model.adapters.app_endpoint_adapter import AppEndpointAdapter
from nectwiz.model.adapters.base_consumption_adapter import BaseConsumptionAdapter
from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.deletion_spec.deletion_spec import DeletionSpec
from nectwiz.model.hook import hook_serial
from nectwiz.model.hook.hook import Hook

controller = Blueprint('app_controller', __name__)

BASE_PATH = '/api/app'


@controller.route(f'{BASE_PATH}/uninstall-hooks')
def trigger_uninstall():
  uninstall_hooks = Hook.by_trigger(event='uninstall')
  serialized_list = list(map(hook_serial.standard, uninstall_hooks))
  return jsonify(data=serialized_list)


@controller.route(f'{BASE_PATH}/uninstall-spec')
def uninstall_victims():
  del_spec: DeletionSpec = DeletionSpec.inflate('nectar.deletion-spec')
  return jsonify(data=del_spec.config)


@controller.route(f'{BASE_PATH}/deletion_selectors')
def deletion_selectors():
  deletion_map = 3
  return jsonify(data=deletion_map)


@controller.route(f'{BASE_PATH}/hooks/<hook_id>/run', methods=['POST'])
def run_hook(hook_id):
  hook = Hook.inflate(hook_id)
  action = hook.action()
  job_id = enqueue_action(action.id() or action.kind())
  return jsonify(data=dict(job_id=job_id))


@controller.route(f'{BASE_PATH}/jobs/<job_id>/status')
def job_status(job_id):
  return jsonify(data=dict(status=ternary_job_status(job_id)))


@controller.route(f'{BASE_PATH}/apply-updates')
def app_apply_updates():
  pass

@controller.route(f'{BASE_PATH}/resource-stats', methods=["GET"])
def app_resource_usage():
  """
  Returns the Base Consumption adapter.
  :return: serialized adapter object.
  """
  adapter = wiz_app.find_adapter_subclass(BaseConsumptionAdapter, True)
  output = adapter().serialize()
  return jsonify(data=output)


@controller.route(f'{BASE_PATH}/application_endpoints', methods=["GET"])
def application_endpoints():
  """
  Returns a list of application endpoint adapters.
  :return: list of serialized adapters.
  """
  provider = wiz_app.find_provider(AppEndpointAdapter)()
  if provider:
    adapters = provider.produce_adapters()
    ser_endpoints = [a.serialize() for a in adapters]
    return jsonify(data=ser_endpoints)
  else:
    return jsonify(data=[])

