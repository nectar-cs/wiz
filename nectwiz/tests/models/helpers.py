
def g_conf(**kwargs):
  key = kwargs.pop('k', 'key')

  return dict(
    key=key,
    kind=kwargs.get('i', 'kind'),
    title=kwargs.get('t', f'{key}.title'),
    info=kwargs.get('d', f'{key}.desc'),
    **kwargs
  )
