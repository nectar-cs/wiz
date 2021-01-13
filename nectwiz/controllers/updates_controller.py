from flask import Blueprint, jsonify

from nectwiz.core.core import job_client, updates_man
from nectwiz.core.telem import telem_man
from nectwiz.model.action.actions.apply_update_action import ApplyUpdateAction
from nectwiz.model.action.actions.run_update_hooks_action import RunUpdateHooksAction

controller = Blueprint('updates_controller', __name__)

BASE_PATH = '/api/updates'


@controller.route(f'{BASE_PATH}/next-available')
def fetch_next_available():
  telem_man.upload_status()
  update_or_none = updates_man.next_available()
  return jsonify(data=update_or_none)


@controller.route(f'{BASE_PATH}/<update_id>')
def show_update(update_id):
  update = updates_man.fetch_update(update_id)
  return jsonify(data=update)


@controller.route(f'{BASE_PATH}/<update_id>/preview')
def preview_update(update_id):
  update = updates_man.fetch_update(update_id)
  preview_bundle = updates_man.preview(update)
  return jsonify(preview_bundle)


@controller.route(f'{BASE_PATH}/<update_id>/apply', methods=['POST'])
def install_update(update_id):
  job_id = job_client.enqueue_action({
    ApplyUpdateAction.KIND_KEY: ApplyUpdateAction.kind(),
    ApplyUpdateAction.UPDATE_ID_KEY: update_id}
  )
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/<update_id>/hooks/<timing>/run', methods=['POST'])
def run_pre_wiz_update_hooks(update_id: str, timing: str):
  job_id = job_client.enqueue_action({
    RunUpdateHooksAction.KIND_KEY: RunUpdateHooksAction.kind(),
    RunUpdateHooksAction.UPDATE_ID_KEY: update_id,
    RunUpdateHooksAction.TIMING_KEY: timing
  })
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/outcomes')
def list_past_updates():
  outcomes = telem_man.list_events()
  return jsonify(data=outcomes)
