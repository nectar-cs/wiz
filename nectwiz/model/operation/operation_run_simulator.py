from typing import Dict, Optional, List

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation import Operation
from nectwiz.model.operation.stage import Stage


class OperationRunSimulator(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.force_ns: str = config['namespace']
    self.operation: Operation = Operation.inflate(config['operation'])
    self.stage_sims: List[Dict] = config.get('stages', [])
    self.validate_input: bool = config.get('validations', True)
    self.run_preflight: bool = config.get('preflight', False)
    self.print_progress: bool = config.get('print_progress', True)

  def stage_at(self, index: int) -> Optional[Stage]:
    if index < len(self.stage_sims):
      stage_sim = self.stage_sims[index]
      return self.operation.stage(stage_sim['stage'])

  def step_input(self, stage_index: int, step_id: str) -> Dict:
    stage_sim = self.stage_sims[stage_index]
    step_sim_finder = lambda step_dict: step_dict['step'] == step_id
    step_sim = next(filter(step_sim_finder, stage_sim['steps']))
    return step_sim['input']
