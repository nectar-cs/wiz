import sys
import time

from nectwiz.core.core import utils, job_client
from nectwiz.core.core.config_man import coerce_ns
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.operation.operation_run_simulator import OperationRunSimulator
from nectwiz.model.operation.operation_state import OperationState


def start():
  simulator: OperationRunSimulator = read_simulator()
  coerce_ns(simulator.force_ns)
  state = OperationState(utils.rand_str(), simulator.operation.id())

  print(f"Operation[{simulator.operation.title}]")

  stage_ind = 0
  step_id = None

  while simulator.stage_at(stage_ind) is not None:
    stage = simulator.stage_at(stage_ind)
    print(f"  Stage [{stage.title}]:")
    if step_id is None:
      step_id = stage.steps()[0].id() if len(stage.steps()) > 0 else 'done'
    while not step_id == 'done':
      step = stage.step(step_id)
      print(f"    Step [{step.title}]:")
      step_input = simulator.step_input(stage_ind, step_id)
      if simulator.validate_input:
        print("     Validation")
        for input_key, input_val in step_input.items():
          validation = step.validate_field(input_key, input_val, state)
          met, tone = validation['met'], validation['tone']
          pretty = validation_emoji(met, tone)
          print(f"        {input_key}={input_val} => {pretty}")
          if tone == 'error' and not met:
            return "HALT VALIDATION FAILED"
        print("     Validation complete")
      step_state = state.gen_step_state(step)
      step.run(step_input, step_state)
      step.compute_status(step_state)
      print("     Run")
      while step_state.status == 'running':
        if simulator.print_progress:
          job_id = step_state.job_id
          progress = job_client.job_progress(job_id)
          print_progress(progress)
          time.sleep(3)
          step.compute_status(step_state)
      print("     Run Complete")
      step_id = stage.next_step_id(step, state)
      print("   Step complete")
    print(" Stage complete")
    stage_ind += 1
  print("Operation complete")


def print_progress(progress: ProgressItem):
  sub_items = progress.get('sub_items', [])
  for item in sub_items:
    if not item['status'] == 'idle':
      base = f"        {item['title']}"
      print(f"{base}: {status_emoji(item['status'])}")
      for sub_sub_item in item['sub_items']:
        base = f"          {sub_sub_item['title']}"
        print(f"{base}: {status_emoji(sub_sub_item['status'])}")


def read_simulator() -> OperationRunSimulator:
  _id = sys.argv[2] if len(sys.argv) >= 3 else None
  return OperationRunSimulator.inflate(_id)


def status_emoji(charge):
  if charge == 'running':
    return '▶'
  elif charge == 'positive':
    return '✔'
  elif charge == 'negative':
    return '⚠⚠'
  elif charge == 'idle':
    return "✋"
  else:
    return "⁉"


def validation_emoji(met, tone):
  if met:
    return "✔"
  else:
    if tone == 'warning':
      return "⚠"
    elif tone == 'error':
      return "🚨💥💣💣💣💣🧨🥀🚨🚨⚠⚠"
    else:
      return "⁉"
