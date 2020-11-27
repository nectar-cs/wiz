from nectwiz.model.operation import predicate_statuses_computer

predicate_statuses_computer.eval_pred.__doc__ = """
  Evaluates the passed condition and prepares an output with details of the
  evaluation.
  :param predicate: condition to be evaluated.
  :return: dict with results of evaluation.
"""

predicate_statuses_computer.all_conditions_met.__doc__ = """
Checks that all conditions in the passed list are met.
:param conditions: list of conditions statuses, as TECS instances.
:return: True if all conditions are True, else False.
"""

predicate_statuses_computer.any_condition_met.__doc__ = """
  Checks that at least one condition in the passed list is met.
  :param conditions: list of conditions statuses, as TECS instances.
  :return: True if at lease one condition is True, else False.
  """
