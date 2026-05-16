import warnings

from flask import current_app as app
from flask import request
from flask_restx import Resource

from prom2notify.app.sender import AlertSender
from prom2notify.prometheus.message_schema import MessageSchema

from .model import *

ns = api_v1.namespace(name='', description='Version 1 connections')


@ns.route('/')
@api_v1.doc(responses={201: 'OK'})
class AlertReceiver(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = MessageSchema()
        self.sender = AlertSender(template_path=app.config.get('TEMPLATE_PATH'),
                                  teams_client_config=app.config.get('TEAMS_CLIENT_CONFIG'))

    @api_v1.expect(message)
    def post(self):
        _show_deprecated_warning("Call to deprecated function. It will be removed in future versions. "
                                 "Please view the README file.")
        alerts = self.schema.load(request.get_json())
        self.sender.send_alerts(alerts, app.config['MICROSOFT_TEAMS']['Connector'])
        return 'OK', 201


def _show_deprecated_warning(msg):
    warnings.warn(message=msg, category=PendingDeprecationWarning)
