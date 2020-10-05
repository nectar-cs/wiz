from flask import Blueprint, jsonify

from nectwiz.core.core import job_client
from nectwiz.model.adapters.app_endpoints_adapter import AccessPointsAdapter
from nectwiz.model.adapters.deletion_spec import DeletionSpec
from nectwiz.model.error.errors_man import errors_man
from nectwiz.model.hook import hook_serial
from nectwiz.model.hook.hook import Hook

controller = Blueprint('app_controller', __name__)

BASE_PATH = '/api/app'


@controller.route(f'{BASE_PATH}/install-hooks')
def app_list_install_hooks():
  install_hooks = Hook.by_trigger(event='install')
  serialized_list = list(map(hook_serial.standard, install_hooks))
  return jsonify(data=serialized_list)


@controller.route(f'{BASE_PATH}/uninstall-hooks')
def app_list_uninstall_hooks():
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
  id_or_kind = action.id() or action.kind()
  job_id = job_client.enqueue_action(id_or_kind)
  return jsonify(data=dict(job_id=job_id))


@controller.route(f'{BASE_PATH}/jobs/<job_id>/status')
def job_progress(job_id):
  progress = job_client.job_progress(job_id)
  status = job_client.ternary_job_status(job_id)
  error = job_client.job_error(job_id)
  if error:
    errors_man.push_error(error)
  return jsonify(
    data=dict(
      status=status,
      progress=progress
    )
  )


@controller.route(f'{BASE_PATH}/errors/<error_id>/diagnose')
def diagnose_error(error_id):
  errdict = errors_man.find_error(error_id)


@controller.route(f'{BASE_PATH}/resource-stats', methods=["GET"])
def app_resource_usage():
  """
  Returns the Base Consumption adapter.
  :return: serialized adapter object.
  """
  # adapter = wiz_app.find_adapter_subclass(BaseConsumptionAdapter, True)
  # output = adapter().serialize()
  # return jsonify(data=output)
  pass


@controller.route(f'{BASE_PATH}/access-points', methods=["GET"])
def application_endpoints():
  """
  Returns a list of application endpoint adapters.
  :return: list of serialized adapters.
  """
  adapter = AccessPointsAdapter.descendent_or_self()
  aps = [ap for ap in adapter.access_points() if ap is not None]
  return jsonify(data=aps)
