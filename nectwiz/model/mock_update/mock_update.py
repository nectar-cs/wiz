from typing import Dict

from nectwiz.model.base.wiz_model import WizModel


next_mock_update_id = "vendor.mock-updates.next"


class MockUpdate(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.type = config.get('type')
    self.version = config.get('version')
    self.note = config.get('note')
    self.injections = config.get('injections')
    # self.tam_type = config.get('tam_type')
    # self.tam_uri = config.get('tam_uri')
