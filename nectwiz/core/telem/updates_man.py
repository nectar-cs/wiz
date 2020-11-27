from datetime import datetime
from typing import Dict, List, Optional

from nectwiz.core.core import hub_api_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateDict, ProgressItem
from nectwiz.model.action.action_parts.apply_manifest_action_part \
  import ApplyManifestActionPart
from nectwiz.model.action.action_parts.await_predicates_settle_action_part \
  import AwaitPredicatesSettleActionPart
from nectwiz.model.action.action_parts.run_hooks_action_part \
  import RunHookGroupActionPart
from nectwiz.model.action.action_parts.update_manifest_defaults_action_part \
  import UpdateManifestDefaultsActionPart
from nectwiz.model.action.base.action import Action
from nectwiz.model.adapters.mock_update \
  import MockUpdate, next_mock_update_id
from nectwiz.model.hook.hook import Hook

TYPE_RELEASE = 'release'
TYPE_UPDATE = 'update'


class WizUpdateAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.timing = config['when']
    self.store_telem = True
    self.event_type = f'{self.timing}_wiz_update'
    self.observer.progress = ProgressItem(
      id=f'wiz-{self.timing}-update-action',
      status='running',
      info=f"Runs {self.timing}-installation hooks",
      sub_items=[]
    )

  def perform(self):
    hooks = find_hooks(self.timing, 'wiz_update')
    progress_items = RunHookGroupActionPart.progress_items(self.timing, hooks)
    self.observer.progress['sub_items'] = progress_items
    RunHookGroupActionPart.perform(self.observer, hooks)
    return True


class UpdateAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.store_telem = True
    self.update: UpdateDict = config.get('update')
    self.event_type = 'app_update'
    self.observer.progress = ProgressItem(
      id='app-update-action',
      status='running',
      info="Updates the variable manifest and waits for a settled state",
      sub_items=[
        *UpdateManifestDefaultsActionPart.progress_items(),
        *ApplyManifestActionPart.progress_items(),
        *AwaitPredicatesSettleActionPart.progress_items(),
      ]
    )

  def telem_extras(self):
    return dict(
      **super().telem_extras(),
      **self.update
    )

  def perform(self, **config):
    self.update: UpdateDict = config.get('update')
    update = self.update
    self.event_name = f"{update.get('type')}:{update.get('version')}"

    before_hooks = find_hooks('before', update['type'])
    after_hooks = find_hooks('after', update['type'])
    progress_items = self.observer.progress['sub_items']

    self.observer.progress['sub_items'] = (
      RunHookGroupActionPart.progress_items('before', before_hooks) +
      progress_items +
      RunHookGroupActionPart.progress_items('after', after_hooks)
    )

    RunHookGroupActionPart.perform(
      self.observer,
      before_hooks
    )

    UpdateManifestDefaultsActionPart.perform(
      self.observer,
      update
    )

    outcomes = ApplyManifestActionPart.perform()

    AwaitPredicatesSettleActionPart.perform(
      self.observer,
      outcomes
    )

    RunHookGroupActionPart.perform(
      self.observer,
      after_hooks
    )

    return True


def find_hooks(which: str, update_type: str) -> List[Hook]:
  return Hook.by_trigger(
    event='software-update',
    update_type=update_type,
    timing=which
  )


def fetch_next_update() -> Optional[UpdateDict]:
  config_man.write_last_update_checked(str(datetime.now()))
  return None


def fetch_update(update_id: str) -> Optional[UpdateDict]:
  if config_man.is_real_deployment():
    resp = hub_api_client.get(f'/app_updates/{update_id}')
    if resp.ok:
      return resp.json()['bundle']
    else:
      print(f"[nectwiz::updates_man] err requesting update {resp.status_code}")
  else:
    model = MockUpdate.inflate(update_id)
    return model.as_bundle()


def next_available() -> Optional[UpdateDict]:
  if config_man.is_real_deployment():
    resp = hub_api_client.get(f'/app_updates/available')
    data = resp.json() if resp.status_code < 205 else None
    return data['bundle'] if data else None
  else:
    model = MockUpdate.inflate(next_mock_update_id)
    return model.as_bundle()


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.manifest_vars()
  return {k: all_vars[k] for k in keys}
