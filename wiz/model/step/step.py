from wiz.core.wiz_globals import wiz_globals
from wiz.model.field.field import Field

class Step:

  def __init__(self, config):
    self.config = config
    self.key = config['key']
    self.title = config['title']
    self.state = wiz_globals.step_state

  def next_step_key(self):
    root = self.config.get('')
    if type(root) == str:
      return root
    else:
      operator, left, right = parse_cond(root)
      left, right = [self.cond_value(left), self.cond_value(right)]
      return operator(left, right)

  def cond_value(self, str_rep):
    if str_rep.lower() == 'true':
      return True
    elif str_rep.lower() == 'false':
      return False
    else:
      return self.state.value(str_rep)

  def field(self, key):
    field_key = [s for s in self.config['fields'] if s == key][0]
    field_config = wiz_globals.step_config(field_key)
    return Field.inflate(field_config)

  def fields(self):
    return [self.field(key) for key in self.config['fields']]

  def apply(self):
    pass

  @classmethod
  def inflate(cls, config):
    custom_subclass = wiz_globals.step_class(config['key'])
    host_class = custom_subclass or cls
    return host_class(config)



def parse_cond(cond_str: str):
  operator = None
  var_names = None
  if len(cond_str.split(' = ')) == 2:
    operator = lambda left, right: left == right
    var_names = cond_str.split(' = ')
  elif len(cond_str.split(' != ')) == 2:
    operator = lambda left, right: left != right
    var_names = cond_str.split(' != ')
  if not operator:
    raise RuntimeError(f"Bad cond string formatting: {cond_str}")
  return operator, var_names[0], var_names[1]
