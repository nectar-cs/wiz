from nectwiz.core.telem import telem_sync
from nectwiz.core.core.types import ActionOutcome
from nectwiz.model.action.action import Action


class FlushTelemAction(Action):
  def perform(self) -> ActionOutcome:
    metric = telem_sync.upload_operation_outcomes()
    return ActionOutcome(
      charge='positive',
      summary=f'Uploaded {metric} unsynced telemetry data',
      data={}
    )
