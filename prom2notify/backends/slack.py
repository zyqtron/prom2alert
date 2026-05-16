#!/usr/bin/env python3
"""prom2notify.backends.slack — Slack webhook connector."""

import json
import logging
from prom2notify.backends import NotifyBackend

log = logging.getLogger('prom2notify')


class SlackBackend(NotifyBackend):
    """Sends alerts to Slack via Incoming Webhook."""

    def _format_payload(self, alert_data: dict) -> str:
        status = alert_data.get('status', 'firing')
        alerts = alert_data.get('alerts', [alert_data])
        title = alert_data.get('commonLabels', {}).get('alertname', 'Prometheus Alert')
        color = '#dc3545' if status == 'firing' else '#28a745'

        fields = []
        for alert in alerts[:5]:
            for k, v in list(alert.get('labels', {}).items())[:4]:
                fields.append({'title': k, 'value': str(v), 'short': True})

        payload = {
            'text': f'[{status.upper()}] {title} - {len(alerts)} alert(s)',
            'attachments': [{
                'color': color,
                'title': title,
                'fields': fields,
                'footer': 'prom2notify',
            }]
        }
        return json.dumps(payload)
