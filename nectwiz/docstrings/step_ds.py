from nectwiz.model.step import step


step.Step.applies_manifest.__doc__ = """
Decides whether to kubectl apply the manifest at this time.
:return: True if yes, False otherwise.
"""


step.Step.sanitize_field_assigns.__doc__= """
Converts the values in the passed key-value dict from strings to sanitized
instances of the Fields class.
:param values: dict to be sanitized.
:return: sanitized key-values dict.
"""


step.Step.partition_user_asgs.__doc__ = """
Partitions new assigns into 3 buckets (chart, inline, state) and
merges with existing assigns in each bucket.
:param assigns: new assigns to be partitioned.
:param prev_state: state from which to collect existing assigns.
:return: tuple of all chart assigns, partitioned and merged.
"""


step.Step.fields.__doc__ = """
Finds the Field by key and inflates (instantiates) into a Field instance.
:param key: identifier for desired Field.
:return: Field instance.
"""
