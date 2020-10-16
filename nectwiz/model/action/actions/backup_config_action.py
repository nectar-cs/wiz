from datetime import datetime
from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.core.telem import telem_man
from nectwiz.model.action.base.action import Action


class BackupConfigAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer.progress['sub_items'] = [
      dict(
        id='backup_config',
        title='Backup master config',
        info='Writes to current configuration to telem database'
      )
    ]

  def perform(self):
    self.observer.set_item_running('backup_config')
    if telem_man.redis():
      raw = config_man.serialize()
      telem_man.store_config_backup(dict(
        timestamp=str(datetime.now()),
        raw=raw
      ))
      self.observer.set_item_status('backup_config', 'positive')
    else:
      self.observer.process_error(
        fatal=False,
        tone='warning',
        reason='Could not save backup because Telem database not found',
        event_type='apply_manifest'
      )


class UpdateLastCheckedAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer.progress['sub_items'] = [
      dict(
        id='update_last_checked',
        sub_items=[
          dict(
            id='update_config',
            title='Record successful update timestamp',
            info='Commit timestamp to master configmap'
          ),
          dict(
            id='sync_last_checked',
            title='Sync status with Nectar Cloud',
            info='Upload TAM/Wiz metadata'
          )
        ]
      )
    ]

  def perform(self):
    set_sub = lambda *args: self.observer.set_crt_subitem_status(*args)
    self.observer.set_item_running('update_last_checked')

    set_sub('update_config', 'running')
    config_man.set_last_updated(datetime.now())
    set_sub('update_config', 'positive')

    set_sub('sync_last_checked', 'running')
    sync_result = telem_man.upload_meta()

    if sync_result:
      set_sub('sync_last_checked', 'positive')
      self.observer.set_item_status('update_last_checked', 'positive')
    else:
      self.observer.process_error(
        fatal=False,
        tone='warning',
        reason='Failed sync status with Nectar Cloud'
      )
