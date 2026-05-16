import logging

from flask_restx import Api

log = logging.getLogger(__name__)

api_v1 = Api(version='1.0', title='Prom2Notify API v1',
             description='A swagger interface for Prom2Notify webservices')


@api_v1.errorhandler
def default_error_handler(e):
    msg = 'An unhandled exception occurred.'
    log.exception(msg + e)
    return {'message': msg}, 500
