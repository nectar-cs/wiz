import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from wiz.core.osr import OperationState

class Person:
  __tablename__ = 'audit_items'
  id = Column(Integer, primary_key=True)
  kind = Column(String(250), nullable=False)
  identifier = Column(String(250), nullable=False)
  outcome = Column(String(250), nullable=False)
  content = Column(BLOB)
  timestamp = Column(TIMESTAMP, nullable=False)




class AuditSink:

  def __init__(self):
    self.db = None

  def save_operation_outcome(self, op_state: OperationState):
    pass

  def save_chart_var_assign(self, var_name: str):
    pass

  def save_chart_upgrade_outcome(self):
    pass

  def save_image_update_outcome(self):
    pass


audit_sink = AuditSink()
