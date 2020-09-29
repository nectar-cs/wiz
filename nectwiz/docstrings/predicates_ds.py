from nectwiz.model.pre_built.common_predicates import ManifestVarComparePredicate, ResCountComparePredicate, \
  ResPropComparePredicate

ManifestVarComparePredicate.evaluate.__doc__ = """
Evaluates if a given chart variable matches up with the desired value.
:return: True if matches up, False otherwise.
"""

ResCountComparePredicate.evaluate.__doc__ = """
Evaluates if the resource matches up with the desired value.
:return: True if matches up, False otherwise.
"""

ResPropComparePredicate.evaluate.__doc__ = """
Evaluates a certain attribute for all eligible KatRes resources. Occurs in
3 steps:
  1. Locate the eligible resource set based on Predicate's selector
  2. Evaluate the chosen attribute for each of the eligible resoruces
  3. Depending on match type (all or any) output a boolean to describe
  evaluation success or failure
:return: True if evaluation succeeds, False otherwise.
"""
