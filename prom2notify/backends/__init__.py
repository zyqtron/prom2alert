#!/usr/bin/env python3
"""
prom2notify.backends.base — Abstract base for notification backends.

Each backend implements a single method: `send(webhook_url, payload_dict)`.
The base class handles common concerns like timeout, retry, and payload validation.
"""

import logging
from abc import ABC, abstractmethod

import requests
from tenacity import retry, wait_fixed, after_log

log = logging.getLogger('prom2notify')


class NotifyBackend(ABC):
    """
    Abstract notification backend.
    Subclasses must implement _format_payload() and can override _do_send().
    """

    DEFAULT_CONFIG = {
        'TIMEOUT': 30,
        'MAX_PAYLOAD': 24576,
        'RETRY_ENABLE': False,
        'RETRY_WAIT_TIME': 60,
    }

    def __init__(self, config=None):
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

        merged = {**self.DEFAULT_CONFIG, **(config or {})}
        self.timeout = merged['TIMEOUT']
        self.max_payload_length = merged['MAX_PAYLOAD']
        self.retry_enabled = merged['RETRY_ENABLE']
        self.wait_time = merged['RETRY_WAIT_TIME']

    @abstractmethod
    def _format_payload(self, alert_data: dict) -> str:
        """
        Transform a Prometheus alert dict into the platform-specific payload.
        Must return a JSON string ready to POST.
        """
        ...

    def _validate_payload(self, payload: str) -> str:
        """Ensure payload doesn't exceed max length."""
        if len(payload) > self.max_payload_length:
            log.warning(f'Payload truncated from {len(payload)} to {self.max_payload_length}')
            return payload[:self.max_payload_length]
        return payload

    def _do_send(self, webhook_url: str, payload: str):
        """Actual HTTP POST — can be overridden for auth flows."""
        payload = self._validate_payload(payload)
        response = self.session.post(webhook_url, data=payload, timeout=self.timeout)
        log.debug(f'Sent to {webhook_url}: status={response.status_code}')
        if response.status_code not in (200, 201, 202, 204):
            raise RuntimeError(
                f'Error sending to {webhook_url}: HTTP {response.status_code} - {response.text[:200]}'
            )

    def send(self, webhook_url: str, alert_data: dict):
        """Send a formatted alert to the given webhook URL."""
        payload = self._format_payload(alert_data)

        if self.retry_enabled:
            @retry(wait=wait_fixed(self.wait_time), after=after_log(log, logging.WARN))
            def _send_with_retry():
                self._do_send(webhook_url, payload)
            _send_with_retry()
        else:
            self._do_send(webhook_url, payload)
