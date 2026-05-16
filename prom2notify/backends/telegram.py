#!/usr/bin/env python3
"""prom2notify.backends.telegram — Telegram bot connector."""

import json
import logging
from prom2notify.backends import NotifyBackend

log = logging.getLogger('prom2notify')


class TelegramBackend(NotifyBackend):
    """Sends alerts to Telegram via bot API."""

    DEFAULT_CONFIG = {**NotifyBackend.DEFAULT_CONFIG, 'PARSE_MODE': 'HTML'}

    def __init__(self, config=None):
        super().__init__(config)
        merged = {**self.DEFAULT_CONFIG, **(config or {})}
        self.parse_mode = merged['PARSE_MODE']

    def _format_payload(self, alert_data: dict) -> str:
        status = alert_data.get('status', 'firing')
        alerts = alert_data.get('alerts', [alert_data])
        title = alert_data.get('commonLabels', {}).get('alertname', 'Prometheus Alert')
        emoji = '🔴' if status == 'firing' else '🟢'
        lines = [f'{emoji} <b>{title}</b> ({status})']

        for alert in alerts[:5]:
            for k, v in alert.get('labels', {}).items():
                lines.append(f'<b>{k}:</b> {v}')
            for k, v in alert.get('annotations', {}).items():
                lines.append(f'<i>{k}:</i> {v}')
            lines.append('---')

        text = '\n'.join(lines)[:4096]
        return json.dumps({'parse_mode': self.parse_mode, 'text': text})

    def _do_send(self, webhook_url: str, payload: str):
        data = json.loads(self._validate_payload(payload))
        resp = self.session.post(webhook_url, json=data, timeout=self.timeout)
        if resp.status_code != 200:
            raise RuntimeError(f'Telegram error: HTTP {resp.status_code} - {resp.text[:200]}')
