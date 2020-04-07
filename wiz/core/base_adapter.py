
class Backend:
  pass

class HelmBackend(Backend):

  def commit_values(self):
    #modify values.yaml?
    pass

  def apply(self):
    #run helm upgrade?
    pass

class PythonBackend(Backend):

  def commit_values(self):
    # write to config map?
    pass

  def apply(self):
    pass

  def apply_here(self):
    # vendor overrides: import local source
    # my_py_manifests.some_manifest.run(self.values_subset)
    pass

  def apply_remotely(self):
    #
    pass

