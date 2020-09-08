from typing import Dict, List

from nectwiz.model.predicate.predicate import Predicate


POS = 'positive'
NEG = 'negative'


def default_exit_preds(charge) -> List[Predicate]:
  if self.step.applies_manifest():
    if self.step.res_selector_descs:
      custom_cond_name = default_some_res_exit_conds[charge]
      custom_cond = Predicate.inflate(custom_cond_name)
      custom_cond.config['selector'] = self.step.res_selector_descs
      return [custom_cond]
    else:
      default_cond_names = default_res_exit_cond_ids[charge]
      return list(map(Predicate.inflate, default_cond_names))
  elif self.step.runs_action():
    default_cond_names = default_job_exit_conds[charge]
    return list(map(Predicate.inflate, default_cond_names))
  else:
    return []


default_some_res_exit_conds: Dict[str, str] = {
  POS: 'nectar.exit_conditions.select_resources_positive',
  NEG: 'nectar.exit_conditions.select_resources_negative',
}


default_res_exit_cond_ids: Dict[str, List[str]] = {
  POS: ['nectar.exit_conditions.all_resources_positive'],
  NEG: ['nectar.exit_conditions.any_resource_negative']
}


default_job_exit_conds: Dict[str, List[str]] = {
  POS: ['nectar.exit_conditions.job_in_succeeded_phase'],
  NEG: ['nectar.exit_conditions.job_in_failed_phase']
}
