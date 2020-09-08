from nectwiz.model.field import field

field.Field.is_manifest_bound.__doc__ = """
Checks if the variable should be recorded in the manifest.
:return: True if it should, False otherwise.
"""


field.Field.is_inline_chart_var.__doc__ = """
Checks if the Field is an inline variable.
:return: True if it is, False otherwise.
"""


field.Field.is_chart_var.__doc__ = """
Checks if the Field is standard chart variable.
:return: True if it is, False otherwise.
"""


field.Field.is_state_var.__doc__ = """
Checks if the Field is state-only variable.
:return: True if it is, False otherwise.
"""


field.Field.needs_decorating.__doc__ = """
Checks if the Field is of type "slider" and thus needs decorating.
:return: True if does, False otherwise.
"""


field.Field.options.__doc__ = """
If the Field has an option source, prepares the options list which consists
of k8s resources.
:return: list of k8s resources as dicts.
"""


field.Field.validate.__doc__= """
Validates the value in the Field against each Validator in the associated
Validator list.
:param value: value to be checked.
:return: list with [tone, message] if at least one Validator returns
non-empty, else [None, None].
"""


field.Field.validators.__doc__ = """
Returns a list of inflated Validators associated with a Field.
:return: list of Validators.
"""
