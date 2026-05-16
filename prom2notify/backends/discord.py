#!/usr/bin/env python3
"""prom2notify.backends.discord — Discord webhook connector."""

import json
import logging
from prom2notify.backends import NotifyBackend

log = logging.getLogger('prom2notify')


class DiscordBackend(NotifyBackend):
    """Sends alerts to Discord via webhook."""

    def _format_payload(self, alert_data: dict) -> str:
        status = alert_data.get('status', 'firing')
        alerts = alert_data.get('alerts', [alert_data])
        title = alert_data.get('commonLabels', {}).get('alertname', 'Prometheus Alert')
        color = 0xdc3545 if status == 'firing' else 0x28a745

        fields = []
        for alert in alerts[:5]:
            for k, v in list(alert.get('labels', {}).items())[:6]:
                fields.append({'name': k, 'value': str(v), 'inline': True})

        embed = {
            'title': title,
            'color': color,
            'description': f'{len(alerts)} alert(s)',
            'fields': fields,
            'footer': {'text': 'prom2notify'},
        }
        payload = {'username': 'Prometheus', 'embeds': [embed]}
        return json.dumps(payload)
