from typing import Tuple

from wiz.core import core, utils


class TemplatingBackend:
  # I intake a dictionary
  # Wait I should live in the separate docker image
  pass

class ErbTemplatingBackend:
  # Mount the ConfigMap to filesystem
  # Not a server at all, just Docker container waiting for cmds
  # docker run "apply by_name[svc:this deploy:that]"
  # inflate all files into hashes (in memory)
  # find(res_type, name), kubectl apply << hack EOF

  # Alternatively, there can be a file-pointer in the wiz app
  # and things get easier e.g apply by_file[file1 file2]
  pass

class K8KatTemplatingBackend:
  pass

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

  @classmethod
  def commit_values(cls, assignments: [Tuple[str, any]]):
    master_map = core.master_map().json('master')
    for assignment in assignments:
      fqdk_array = assignment[0].split('.')
      value = assignment[1]
      utils.deep_set(master_map, fqdk_array, value)
    core.master_map().set_json('master', master_map)

  @classmethod
  def apply(cls, resources: Tuple[str, str]):
    pass

  def apply_here(self):
    # vendor overrides: import local source
    # my_py_manifests.some_manifest.run(self.values_subset)
    pass

  def apply_remotely(self):
    #
    pass

