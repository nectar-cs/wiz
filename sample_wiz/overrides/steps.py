from typing import Dict

from wiz.model.step.step import Step


class AvailabilityStep(Step):

  @classmethod
  def expected_key(cls):
    return "installation.availability"

  @classmethod
  def type_key(cls):
    return Step.type_key()

  def finalize_chart_values(self, assigns: Dict, all_assigns, op_state):
    exp_users_i = str_num_to_i(all_assigns.get('hub.backend.num_users', 0))
    req_downtime_i = str_num_to_i(all_assigns.get('hub.backend.response_time', 0))
    num_rep = exp_users_i + req_downtime_i
    return {
      "hub.backend.replicas": (num_rep - num_rep) + 1,
      "hub.frontend.replicas": (num_rep - num_rep) + 1
    }

def str_num_to_i(str_rep):
  if str_rep == 'small':
    return 1
  return 3 if str_rep == 'high' else 2
