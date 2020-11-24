from nectwiz.model.field.field import Field

def document():
  Field.is_manifest_bound.__doc__ = """
  Checks if the variable should be recorded in the manifest.
  :return: True if it should, False otherwise.
  """
