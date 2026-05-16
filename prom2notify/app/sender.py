#!/usr/bin/env python3
"""
prom2notify.app.sender — Multi-backend alert sender.

Dispatches Prometheus alerts to any configured notification backend.
"""

import logging

from prom2notify.backends.teams import TeamsBackend, TeamsTemplateBackend
from prom2notify.backends.slack import SlackBackend
from prom2notify.backends.discord import DiscordBackend
from prom2notify.backends.telegram import TelegramBackend
from prom2notify.backends.generic import GenericWebhookBackend
from prom2notify.teams.alert_mapper import map_and_group, map_prom_alerts_to_teams_alerts
from prom2notify.teams.composer import TemplateComposer

log = logging.getLogger('prom2notify')

BACKEND_REGISTRY = {
    'teams': TeamsBackend,
    'teams_template': TeamsTemplateBackend,
    'slack': SlackBackend,
    'discord': DiscordBackend,
    'telegram': TelegramBackend,
    'generic': GenericWebhookBackend,
}


def backend_from_config(name, backend_config=None):
    """Factory: instantiate a backend from its name."""
    cls = BACKEND_REGISTRY.get(name)
    if not cls:
        raise ValueError(f'Unknown backend: {name}. Available: {", ".join(BACKEND_REGISTRY)}')
    return cls(config=backend_config)


class AlertSender:
    """
    Dispatches alerts to multiple backends.
    Each connector in the config maps to (backend_type, webhook_url, backend_config).
    """

    def __init__(self, template_path=None, group_alerts_by=False, connectors=None, teams_client_config=None):
        """connectors: dict of name -> (backend_type, webhook_url, backend_config_or_None)"""
        self.json_composer = TemplateComposer(template_path) if template_path else None
        self.group_alerts_by = group_alerts_by

        self.backends = {}  # name -> (backend_instance, webhook_url)
        if connectors:
            for name, (btype, url, bconfig) in connectors.items():
                if btype == 'teams_template' and self.json_composer:
                    backend = TeamsTemplateBackend(self.json_composer, config=bconfig or teams_client_config)
                else:
                    backend = backend_from_config(btype, config=bconfig or teams_client_config)
                self.backends[name] = (backend, url)
                log.info(f'Backend "{name}": {btype} -> {url[:50]}...')

    def _create_alerts(self, alerts):
        if self.group_alerts_by and self.json_composer:
            max_payload = 24576  # teams default
            mapped = map_and_group(alerts, self.group_alerts_by, self.json_composer.compose, max_payload)
        else:
            mapped = map_prom_alerts_to_teams_alerts(alerts)
        # Ensure JSON strings for downstream consumers
        import json
        return [json.dumps(m) if isinstance(m, dict) else m for m in mapped]

    def send_alerts(self, alerts, teams_webhook_url=None):
        """
        Send alerts to all configured backends.
        teams_webhook_url kept for backward compat — if set and no backends, create a TeamsBackend.
        """
        if not self.backends and teams_webhook_url:
            # Legacy mode: single Teams webhook
            self.backends['default'] = (TeamsBackend(), teams_webhook_url)

        if not self.backends:
            log.error('No backends configured and no webhook URL provided')
            return

        formatted = self._create_alerts(alerts)

        for name, (backend, url) in self.backends.items():
            for alert_data in formatted:
                try:
                    if isinstance(backend, TeamsTemplateBackend):
                        # TeamsTemplateBackend.compose returns already-formatted
                        backend.send(url, alert_data)
                    else:
                        backend.send(url, alert_data)
                    log.info(f'Alert sent via "{name}" ({len(formatted)} items)')
                except Exception as e:
                    log.error(f'Failed to send via "{name}": {e}')
