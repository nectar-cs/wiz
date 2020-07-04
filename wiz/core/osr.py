from typing import Dict
from pathlib import Path

from flask import json

from wiz.model.operations.operation import Operation

class OperationRecord:

  def __init__(self, raw_record: Dict):
    raw_steps = raw_record.get('steps', [])
    self.step_records = [StepRecord(raw) for raw in raw_steps]

  def record_step_started(self, step_name: str, bundle):
    pass

  def record_step_terminated(self, step_name: str, bundle):
    pass

  def step_record(self, step_name: str):
    matcher = (sr for sr in self.step_records if sr.lid == step_name)
    return next(matcher)


class StepRecord:

  def __init__(self, raw_record: Dict):
    pass



class OperationStateRecorder:
  def __init__(self, ser_operation_record: Dict):
    self.record = OperationRecord(ser_operation_record)

  def record_step_started(self):
    pass

  def record_step_terminated(self):
    pass

  def persist(self):
    pass

  @classmethod
  def retrieve(cls, _id):
    raw = read_serialized_op_state(_id)
    return OperationStateRecorder(raw)


BASE_DIR = '/tmp/nectar-wiz'

sample_record = {
  'id': 'random-str',
  'started_at': 'datetime',
  'operation_id': 'installation',
  'steps': [
    {
      'id': 'strategy',
      'started_at': 'datetime',
      'submitted_at': 'datetime',
      'finished_at': 'datetime',
      'assignments': {
        'hub.storage.strategy': 'internal'
      },
      'computed': {
        'hub.storage.strategy': 'internal'
      },
      'job': {
        'id': 'random-str',
        'started_at': 'datetime',
        'finished_at': 'datetime',
        'exit_code': '0',
        'logs': []
      }
    }
  ]
}


def read_serialized_op_state(record_id):
  file = Path(f'{BASE_DIR}/osr-{record_id}.json')
  file.touch(exist_ok=True)
  with file.open('r') as readable_file:
    contents = readable_file.read()
    return json.loads(contents)


def commit_op_started(operation: Operation):
  pass
