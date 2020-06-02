from wiz.model.adapters.adapter import Adapter


class AppEndpointAdapter(Adapter):

  def name(self):
    raise NotImplementedError

  def url(self):
    raise NotImplementedError
