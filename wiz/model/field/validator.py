class Validator:
  def __init__(self, config, checker=None):
    self.checker = checker
    self.check = config['check']
    self.message = config['message']
    self.tone = config['tone'].lower()

    if self.tone not in ['warning', 'error']:
      raise RuntimeError(f'Tone must be warning or error, got {self.tone}')

  def perform(self, value):
    if self.checker:
      self.checker(value, self.check)
    else:
      raise NotImplementedError

  def validate(self, value):
    if self.perform(value):
      return [self.tone, self.message]
    else:
      return [None, None]

  @classmethod
  def inflate(cls, config):
    _type = config['type']
    if _type == 'equality':
      op = lambda x, y: str(x).lower() == str(y).lower()
      return Validator(config, op)
    elif _type == 'inequality':
      op = lambda x, y: str(x).lower() != str(y).lower()
      return Validator(config, op)
    else:
      raise RuntimeError(f"Don't know validation type {_type}")