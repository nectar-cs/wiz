# noinspection PyUnresolvedReferences
import dotenv


# noinspection PyUnresolvedReferences
from k8_kat.res.rbac.rbac import KatClusterRole, KatRole, \
  KatClusterRoleBinding, KatRoleBinding
# noinspection PyUnresolvedReferences
from k8_kat.res.pod.kat_pod import KatPod
# noinspection PyUnresolvedReferences
from k8_kat.res.dep.kat_dep import KatDep
# noinspection PyUnresolvedReferences
# noinspection PyUnresolvedReferences
from k8_kat.auth.kube_broker import broker
# noinspection PyUnresolvedReferences
from k8_kat.res.ns.kat_ns import KatNs

if __name__ == '__main__':
  dotenv.load_dotenv()
  broker.connect()

