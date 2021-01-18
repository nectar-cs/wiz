from flask import Blueprint, jsonify

from nectwiz.core.core import updates_man, job_client
from nectwiz.model.action.actions.run_update_hooks_action import RunUpdateHooksAction
from nectwiz.model.action.actions.sync_injections_action import SyncInjectionsAction

controller = Blueprint('injections_controller', __name__)

BASE_PATH = '/api/injections'

@controller.route(f'{BASE_PATH}/check_newer')
def check_newer():
  new_available = not updates_man.is_using_latest_injection()
  return jsonify(data=new_available)


@controller.route(f'{BASE_PATH}/latest/preview')
def preview():
  bundle = updates_man.latest_injection_bundle()
  preview_data = updates_man.preview_injection(bundle)
  return jsonify(data=preview_data)


@controller.route(f'{BASE_PATH}/latest/hooks/<timing>/run', methods=['POST'])
def run_injection_hooks(timing: str):
  job_id = job_client.enqueue_action({
    RunUpdateHooksAction.KIND_KEY: RunUpdateHooksAction.kind(),
    RunUpdateHooksAction.IS_INJECTION_KEY: True,
    RunUpdateHooksAction.TIMING_KEY: timing
  })
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/latest/apply', methods=['POST'])
def apply_latest_injection():
  action_kod = SyncInjectionsAction.__name__
  job_id = job_client.enqueue_action(action_kod)
  return jsonify(data=dict(job_id=job_id))
