from k8kat.auth.kube_broker import broker

from nectwiz.model.base.wiz_model import models_man

broker.connect(dict(
  auth_type='kube-config',
  context='wear'
))

models_man.add_defaults()

print("[nectwiz::shell] loaded packages for shell mode")