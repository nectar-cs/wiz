from nectwiz.core.core.types import ActionOutcome
from nectwiz.model.action.action import Action


class FlushTelemAction(Action):
  
  def __init__(self, config):
    config['title'] = config.get('title', 'Upload Unsynced Telemetry')
    config['info'] = config.get('info', "Try uploaded unsynced telemetry to Nectar")
    super().__init__(config)
  
  def perform(self) -> ActionOutcome:
    # metric = telem_sync.upload_operation_outcomes()
    print("I AM ACTION")
    return ActionOutcome(
      **self.outcome_template(),
      charge='positive',
      summary=f'Uploaded {3} unsynced telemetry data',
      data={}
    )
