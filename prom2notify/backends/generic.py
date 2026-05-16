#!/usr/bin/env python3
"""prom2notify.backends.generic — Generic webhook connector."""

import json

from prom2notify.backends import NotifyBackend


class GenericWebhookBackend(NotifyBackend):
    """Sends raw Prometheus alertmanager JSON to any HTTP endpoint."""

    def _format_payload(self, alert_data: dict) -> str:
        return json.dumps(alert_data, indent=2)
