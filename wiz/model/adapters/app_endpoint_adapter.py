from wiz.model.adapters.adapter import Adapter


class AppEndpointAdapter(Adapter):

  def name(self):
    raise NotImplementedError

  def url(self):
    raise NotImplementedError

  def serialize(self, **kwargs):
    return dict(
      name=self.name(),
      url=self.url()
    )
