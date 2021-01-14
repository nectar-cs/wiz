from flask import Blueprint, jsonify

from nectwiz.core.core import job_client
from nectwiz.core.telem import telem_man
from nectwiz.model.adapters.app_status_computer import AppStatusComputer
from nectwiz.model.adapters.deletion_spec import DeletionSpec
from nectwiz.model.glance.glance import Glance
from nectwiz.model.hook import hook_serial
from nectwiz.model.hook.hook import Hook
from nectwiz.model.predicate.system_check import SystemCheck

controller = Blueprint('app_controller', __name__)

BASE_PATH = '/api/app'


@controller.route(f'{BASE_PATH}/start-system-check', methods=['POST'])
def run_system_check():
  sys_check: SystemCheck = SystemCheck.inflate_singleton()
  if sys_check and sys_check.is_non_empty():
    action_config = sys_check.multi_predicate_action_config()
    job_id = job_client.enqueue_action(action_config)
    return jsonify(status='running', job_id=job_id)
  else:
    return jsonify(status='positive')


@controller.route(f'{BASE_PATH}/compute-status', methods=['GET', 'POST'])
def run_status_compute():
  computer = AppStatusComputer.inflate_singleton()
  application_status = computer.compute_and_commit_status()
  return jsonify(app_status=application_status)


@controller.route(f'{BASE_PATH}/sync-hub', methods=['POST'])
def sync_hub():
  job_id = job_client.enqueue_func(telem_man.upload_all_meta)
  return jsonify(job_id=job_id)


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
  result = None
  if status == 'positive':
    result = job_client.job_result(job_id)
  return jsonify(
    data=dict(
      status=status,
      progress=progress,
      result=result
    )
  )


@controller.route(f'{BASE_PATH}/glance-ids', methods=["GET"])
def glance_ids():
  """
  Returns a list of application endpoint adapters.
  :return: list of serialized adapters.
  """
  glances = Glance.inflate_all()
  serialized = list(map(Glance.fast_serialize, glances))
  return jsonify(data=serialized)


@controller.route(f'{BASE_PATH}/glances/<glance_id>', methods=["GET"])
def get_glance(glance_id: str):
  glance = Glance.inflate(glance_id)
  return jsonify(data=glance.compute_and_serialize())
