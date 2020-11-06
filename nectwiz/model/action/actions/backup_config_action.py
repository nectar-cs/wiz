import time
import traceback
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
        status='idle',
        title='Backup master config',
        info='Writes to current configuration to telem database'
      )
    ]

  def perform(self):
    self.observer.set_item_running('backup_config')
    time.sleep(2)
    if telem_man.get_db():
      cmap_contents = config_man.serialize()
      print(f"[nectwiz:backup_config_action] saving {cmap_contents}")
      telem_man.store_config_backup(dict(
        event_type='backup_action',
        data=cmap_contents,
        timestamp=str(datetime.now())
      ))
      self.observer.set_item_status('backup_config', 'positive')
    else:
      self.observer.process_error(
        fatal=False,
        tone='warning',
        reason='Could not save backup because Telem database not found',
        event_type='backup_config'
      )


class UpdateLastCheckedAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer.progress['sub_items'] = [
      dict(
        id='update_last_checked',
        title='Record successful update',
        info='Record event locally and sync status with Nectar Cloud',
        status='idle',
        sub_items=[
          dict(
            id='update_config',
            title='Record successful update timestamp',
            info='Commit timestamp to master configmap',
            status='idle'
          ),
          dict(
            id='sync_last_checked',
            title='Sync status with Nectar Cloud',
            info='Upload TAM/Wiz metadata',
            status='idle'
          )
        ]
      )
    ]

  def perform(self):
    set_sub = lambda *args: self.observer.set_crt_subitem_status(*args)
    self.observer.set_item_running('update_last_checked')

    set_sub('update_config', 'running')
    time.sleep(1)
    config_man.write_last_synced(datetime.now())
    set_sub('update_config', 'positive')

    set_sub('sync_last_checked', 'running')
    sync_result = False
    time.sleep(1)
    try:
      telem_man.upload_all_meta()
      sync_result = True
    except:
      print("[nectwiz::update_last_checked_action] hub rejected sync")
      print(traceback.format_exc())

    if sync_result:
      set_sub('sync_last_checked', 'positive')
      self.observer.set_item_status('update_last_checked', 'positive')
    else:
      self.observer.process_error(
        fatal=False,
        tone='warning',
        status='idle',
        reason='Failed sync status with Nectar Cloud'
      )
