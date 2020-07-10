from functools import cached_property
from typing import Dict

from sqlalchemy import Column, Integer, String, TIMESTAMP, UnicodeText

from wiz.core import tedi_client
from wiz.core.telem.ost import OperationState


class AuditConfig:

  @cached_property
  def config_dict(self) -> Dict:
    kat_map = tedi_client.master_cmap()
    chart = kat_map.jget('master', {}) if kat_map else {}
    return chart.get('nectar', {}).get('auditing', {})

  def is_persistence_enabled(self) -> bool:
    strategy = self.config_dict.get('storage_strategy', '')
    return bool(strategy.strip())


class AuditableEvent:
  __tablename__ = 'audit_items'

  id = Column(Integer, primary_key=True)
  kind = Column(String(250), nullable=False)
  identifier = Column(String(250), nullable=False)
  outcome = Column(String(250), nullable=False)
  data = Column(UnicodeText, nullable=False)
  sync_status = Column(String, nullable=False)
  created_at = Column(TIMESTAMP, nullable=False)


class AuditSink:

  def __init__(self):
    self.db = None

  def save_op_outcome(self, op_state: OperationState, sync_status: bool):
    print("Soon save_op_outcome!")

  def save_chart_var_assign(self, var_name: str):
    pass

  def save_chart_upgrade_outcome(self):
    pass

  def save_image_update_outcome(self):
    pass


audit_sink = AuditSink()
