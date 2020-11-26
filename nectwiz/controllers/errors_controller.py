from flask import Blueprint, jsonify

from nectwiz.core.core import job_client
from nectwiz.model.error.error_handler import ErrorHandler
from nectwiz.model.error.errors_man import errors_man
from nectwiz.serializers.err_serializer import ser_err_diagnosis

controller = Blueprint('errors_controller', __name__)

BASE_PATH = '/api/errors'


@controller.route(f'{BASE_PATH}/<error_id>/diagnose', methods=['POST'])
def start_diagnoses_search_job(error_id: str):
  errdict = errors_man.find_error(error_id)
  if errdict:
    handler = ErrorHandler.find_handler(errdict)
    if handler:
      job_id = job_client.enqueue_func(
        ErrorHandler.compute_diagnoses_ids,
        handler.id()
      )
      return jsonify(status='running', job_id=job_id)
    else:
      return jsonify(status='handler-not-found')
  else:
    return jsonify(status='err-not-found')


@controller.route(f'{BASE_PATH}/<error_id>/diagnoses/<job_id>')
def diagnoses_search_job_status(error_id: str, job_id: str):
  job = job_client.find_job(job_id)
  if job.is_finished:
    errdict = errors_man.find_error(error_id)
    handler = ErrorHandler.find_handler(errdict)
    finder = lambda d: d.id() in job.result
    diagnoses = list(filter(finder, handler.diagnoses()))
    serialized = list(map(ser_err_diagnosis, diagnoses))
    return jsonify(status='ready', diagnoses=serialized)
  elif job.is_failed:
    return jsonify(status='error')
  else:
    return jsonify(status='pending')
