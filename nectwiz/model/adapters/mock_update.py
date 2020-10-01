from typing import Dict

import requests

from nectwiz.core.core.types import UpdateDict

from nectwiz.model.base.wiz_model import WizModel


next_mock_update_id = "vendor.mock-updates.next"


class MockUpdate(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.type = config.get('type')
    self.version = config.get('version')
    self.note = config.get('note')
    self.injections = config.get('injections')
    self.tam_type = config.get('tam_type')
    self.tam_uri = config.get('tam_uri')
    if not self.note and config.get('note_url'):
      remote_note = requests.get(config.get('note_url'))
      self.note = remote_note.text

  def as_bundle(self) -> UpdateDict:
    return UpdateDict(
      id=self.id(),
      type=self.type,
      version=self.version,
      tam_type=self.tam_type,
      tam_uri=self.tam_uri,
      injections=self.injections,
      note=self.note,
      manual=False
    )
