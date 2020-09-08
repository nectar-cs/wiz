
def g_conf(**kwargs):
  key = kwargs.pop('k', 'key')

  return dict(
    id=key,
    kind=kwargs.pop('i', 'kind'),
    title=kwargs.pop('t', f'{key}.title'),
    info=kwargs.pop('d', f'{key}.desc'),
    **kwargs
  )
