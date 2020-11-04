from typing import Dict


def ser_config_backup(config: Dict) -> Dict:
  return dict(
    id=str(config.get('_id')),
    name=config.get('name'),
    event_type=config.get('event_type'),
    timestamp=config.get('timestamp')
  )


def ser_config_backup_full(config: Dict) -> Dict:
  return dict(
    **ser_config_backup(config),
    data=config.get('data', {})
  )
