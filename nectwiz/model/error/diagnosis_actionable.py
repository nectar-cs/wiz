from typing import Dict

from nectwiz.core.core import job_client
from nectwiz.core.core.types import KoD
from nectwiz.model.base.wiz_model import WizModel


class DiagnosisActionable(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.action_kod: KoD = config.get('action')
    self.operation_id: str = config.get('operation_id')

  def run_action(self):
    return job_client.enqueue_action(self.action_kod)
