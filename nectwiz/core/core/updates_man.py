from datetime import datetime
from typing import Dict, List, Optional

from nectwiz.core.core import hub_api_client, utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateDict, InjectionDesc, K8sResDict
from nectwiz.core.core.utils import deep_merge
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.adapters import mock_update
from nectwiz.model.adapters.injection_orchestrator import InjectionOrchestrator
from nectwiz.model.adapters.mock_update \
  import MockUpdate
from nectwiz.model.hook.hook import Hook


def is_using_latest_injection() -> bool:
  bundle = latest_injection_bundle()
  return bundle is None


def fetch_next_update() -> Optional[UpdateDict]:
  config_man.write_last_update_checked(str(datetime.now()))
  return None


def latest_injection_bundle() -> Optional[InjectionDesc]:
  if config_man.is_real_deployment():
    last_injected = str(config_man.last_injected(True, True))
    endpoint = f'/injections/latest?last_injected={last_injected}'
    resp = hub_api_client.get(endpoint)
    if resp.ok:
      return resp.json()['bundle']
    else:
      print(f"[nectwiz::updates_man] err requesting injection {resp.status_code}")
      return None
  else:
    model = MockUpdate.inflate(mock_update.injection_bundle_id)
    return model.as_injection_bundle()


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
    model = MockUpdate.inflate(mock_update.app_update_id)
    return model.as_bundle()


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.manifest_vars()
  return {k: all_vars[k] for k in keys}


def find_hooks(timing: str, update: UpdateDict) -> List[Hook]:
  return Hook.by_trigger(
    event='software-update',
    timing=timing,
    **update
  )


def find_injection_hooks(timing: str) -> List[Hook]:
  return Hook.by_trigger(
    event='injection',
    timing=timing
  )


def preview_injection(injection: InjectionDesc) -> Dict:
  old_defaults = config_man.manifest_defaults()
  old_manifest = tam_client().template_manifest_std()

  orchestrator = InjectionOrchestrator.inflate_singleton()
  new_defaults = deep_merge(old_defaults, injection['chart'])

  new_resources = []
  if len(injection['inlines']) > 0:
    new_resources = tam_client().dry_run(
      values=injection['inlines'],
      rules=orchestrator.apply_selectors
    )

  new_manifest = [r for r in old_manifest]

  def find_twin(res: K8sResDict) -> Optional[int]:
    for (i, _res) in enumerate(new_manifest):
      if utils.same_res(res, _res):
        return i
    return None

  for new_res in new_resources:
    old_version_ind = find_twin(new_res)
    if old_version_ind:
      old_version = new_manifest[old_version_ind]
      new_manifest[old_version_ind] = deep_merge(old_version, new_res)
    else:
      new_manifest.append(new_res)

  return dict(
    defaults=dict(
      old=old_defaults,
      new=new_defaults
    ),
    manifest=dict(
      old=old_manifest,
      new=new_manifest
    )
  )


def preview(update_dict: UpdateDict) -> Dict:
  old_defaults = config_man.manifest_defaults()
  old_manifest = tam_client().template_manifest_std()

  new_tam = updated_release_tam(update_dict)
  new_tam_client = tam_client(tam=new_tam)

  new_defaults = new_tam_client.load_default_values()
  new_manifest_vars = deep_merge(new_defaults, config_man.manifest_vars())
  new_manifest = new_tam_client.template_manifest(new_manifest_vars)

  return dict(
    defaults=dict(
      old=old_defaults,
      new=new_defaults
    ),
    manifest=dict(
      old=old_manifest,
      new=new_manifest
    )
  )


def commit_new_tam(update_dict: UpdateDict):
  new_tam = updated_release_tam(update_dict)
  config_man.patch_tam(new_tam)


def commit_new_defaults(update_dict: UpdateDict):
  new_tam = updated_release_tam(update_dict)
  new_defaults = tam_client(tam=new_tam).load_default_values()
  config_man.patch_manifest_defaults(new_defaults)


def updated_release_tam(update: UpdateDict) -> Dict:
  tam = dict(version=update['version'])
  if update.get('tam_type'):
    tam['type'] = update.get('tam_type')
  if update.get('tam_uri'):
    tam['uri'] = update.get('tam_uri')
  return {**config_man.tam(), **tam}
