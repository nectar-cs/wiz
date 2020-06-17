from wiz.model.step.step import Step


class AvailabilityStep(Step):

  @classmethod
  def key(cls):
    return "availability"

  @classmethod
  def type_key(cls):
    return Step.type_key()

  @staticmethod
  def str_num_to_i(str_rep):
    if str_rep == 'small':
      return 1
    return 3 if str_rep == 'high' else 2

  def sanitize_field_values(self, values):
    exp_users_i = self.str_num_to_i(values['hub.backend.num_users'])
    req_downtime_i = self.str_num_to_i(values['hub.backend.response_time'])
    num_rep = exp_users_i + req_downtime_i
    return {
      "hub.backend.replicas": (num_rep - num_rep) + 1,
      "hub.frontend.replicas": (num_rep - num_rep) + 1
    }


class LocateExternalDatabaseStep(Step):

  @classmethod
  def key(cls):
    return "locate_external_db"

  @classmethod
  def type_key(cls):
    return Step.type_key()

  @staticmethod
  def can_connect(**connection_props):
    return False

  def commit(self, values):
    if self.can_connect(**values):
      return super().commit(values)
    else:
      return "negative", "Connection to the database failed"

