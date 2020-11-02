from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel


class StatusAdapter(WizModel):

  def compute_status(self) -> str:
    return 'running'

  def compute_and_commit_status(self) -> str:
    status = self.compute_status()
    config_man.write_application_status(status)
    return status
