
def g_con_confs(keys):
  return [g_con_conf(key=key) for key in keys]

def g_con_conf(**kwargs):
  key = kwargs.get('k', 'key')
  bkp_steps = [i + 1 for i in range(kwargs.get('sc', 3))]

  return dict(
    key=key,
    title=kwargs.get('t', f'{key}.title'),
    description=kwargs.get('d', f'{key}.desc'),
    steps=kwargs.get('s', bkp_steps)
  )

def g_step_conf(**kwargs):
  key = kwargs.get('k', 'key')

  return dict(
    key=key,
    title=kwargs.get('t', f'{key}.title'),
  )
