#!/usr/bin/env python3
"""prom2notify.backends.teams — Microsoft Teams connector."""

import json
import logging
from prom2notify.backends import NotifyBackend

log = logging.getLogger('prom2notify')


class TeamsBackend(NotifyBackend):
    """Sends alerts to Microsoft Teams via webhook connector."""

    def _format_payload(self, alert_data: dict) -> str:
        if isinstance(alert_data, str):
            return alert_data
        return json.dumps(alert_data)


class TeamsTemplateBackend(NotifyBackend):
    """Sends alerts using Jinja2 template (original prom2teams behaviour)."""

    def __init__(self, template_composer, config=None):
        super().__init__(config)
        self.composer = template_composer

    def _format_payload(self, alert_data: dict) -> str:
        return self.composer.compose(alert_data)
