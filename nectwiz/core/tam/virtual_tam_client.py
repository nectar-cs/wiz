from typing import List, Dict

from nectwiz.core.core.types import K8sResDict
from nectwiz.core.tam.tam_client import TamClient


class VirtualTamClient(TamClient):
  def template_manifest(self, values: Dict) -> List[K8sResDict]:
    return self._template(values)

  def load_default_values(self) -> Dict[str, str]:
    return self._default_values()

  def _template(self, values: Dict) -> List[Dict]:
    raise NotImplementedError

  def _default_values(self) -> Dict:
    return {}
