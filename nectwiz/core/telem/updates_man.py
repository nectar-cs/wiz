from datetime import datetime
from typing import Dict, List, Optional

from nectwiz.core.core import utils, hub_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateDict, ProgressItem
from nectwiz.model.action.base.action import Action
from nectwiz.model.action.action_parts.apply_manifest_action_part import ApplyManifestActionPart
from nectwiz.model.action.action_parts.await_settled_action_part import AwaitSettledActionPart
from nectwiz.model.action.action_parts.run_hooks_action_part import RunHookGroupActionPart
from nectwiz.model.action.action_parts.update_manifest_defaults_action_part import UpdateManifestDefaultsActionPart
from nectwiz.model.adapters.mock_update import MockUpdate, next_mock_update_id
from nectwiz.model.hook.hook import Hook

TYPE_RELEASE = 'release'
TYPE_UPDATE = 'update'


class UpdateAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer.progress = ProgressItem(
      id='software-update-action',
      status='running',
      info="Updates the variable manifest and waits for a settled state",
      sub_items=[
        *UpdateManifestDefaultsActionPart.progress_items(),
        *ApplyManifestActionPart.progress_items(),
        *AwaitSettledActionPart.progress_items(),
      ]
    )

  def perform(self, **kwargs):
    update: UpdateDict = kwargs.get('update')

    before_hooks = find_hooks('before', update['type'])
    after_hooks = find_hooks('after', update['type'])
    progress_items = self.observer.progress['sub_items']

    self.observer.progress['sub_items'] = (
      RunHookGroupActionPart.progress_items(before_hooks) +
      progress_items +
      RunHookGroupActionPart.progress_items(after_hooks)
    )

    RunHookGroupActionPart.perform(
      self.observer, before_hooks
    )

    UpdateManifestDefaultsActionPart.perform(
      self.observer,
      update,
    )
    outcomes = ApplyManifestActionPart.perform(
      self.observer,
      None,
      None,
      []
    )

    AwaitSettledActionPart.perform(
      self.observer,
      outcomes
    )

    RunHookGroupActionPart.perform(
      self.observer, after_hooks
    )

    return dict(success=True)

  def telem_bundle(self) -> Dict:
    return dict(
      type='update_outcome',
      **super().telem_bundle()
    )


def find_hooks(which: str, update_type: str) -> List[Hook]:
  return Hook.by_trigger(
    event='software-update',
    update_type=update_type,
    timing=which,
  )


def fetch_next_update() -> Optional[UpdateDict]:
  config_man.write_last_update_checked(str(datetime.now()))
  return None


def fetch_update(_id: str) -> Optional[UpdateDict]:
  if utils.is_prod():
    uuid = config_man.install_uuid()
    resp = hub_client.get(f'/api/cli/{uuid}/app_updates/{_id}')
    data = resp.json()['data'] if resp.status_code < 205 else None
    return data['bundle'] if data else None
  else:
    model = MockUpdate.inflate_with_key(_id)
    return model.as_bundle()


def next_available() -> Optional[UpdateDict]:
  if utils.is_prod():
    uuid = config_man.install_uuid()
    resp = hub_client.get(f'/api/cli/{uuid}/app_updates/available')
    data = resp.json()['data'] if resp.status_code < 205 else None
    return data['bundle'] if data else None
  else:
    model = MockUpdate.inflate_with_key(next_mock_update_id)
    return model.as_bundle()


def notify_hub_checked() -> bool:
  uuid = config_man.install_uuid()
  if uuid:
    url = f'/{uuid}/app_updates/notify_checked_update'
    resp = hub_client.post(url, dict(data=dict(
      tam_type=config_man.tam().get('type'),
      tam_uri=config_man.tam().get('uri'),
      tam_version=config_man.tam().get('version'),
    )))
    print(f"[updates_man::notify_checked] resp: {resp}")
    return resp.status_code < 205
  else:
    return True


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.read_manifest_vars()
  return {k: all_vars[k] for k in keys}
