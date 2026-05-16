#!/usr/bin/env python3
"""Tests for prom2notify backends."""
import json
import pytest
from prom2notify.backends.slack import SlackBackend
from prom2notify.backends.discord import DiscordBackend
from prom2notify.backends.telegram import TelegramBackend
from prom2notify.backends.generic import GenericWebhookBackend
from prom2notify.backends import NotifyBackend


class _TestBackend(NotifyBackend):
    """Concrete subclass for testing base class."""
    def _format_payload(self, alert_data: dict) -> str:
        return json.dumps(alert_data)


SAMPLE_ALERT = {
    "status": "firing",
    "labels": {"alertname": "HighCPU", "severity": "critical", "instance": "server01"},
    "annotations": {"summary": "CPU > 90%", "description": "CPU at 95% for 5 min"},
    "startsAt": "2026-05-16T20:00:00Z",
    "generatorURL": "http://prometheus:9090/graph?g0.expr=..."
}

SAMPLE_ALERTMANAGER = {
    "status": "firing",
    "alerts": [SAMPLE_ALERT],
    "commonLabels": {"alertname": "HighCPU"},
    "commonAnnotations": {},
    "groupLabels": {"alertname": "HighCPU"},
    "receiver": "prom2notify",
}

def test_base_interface():
    b = _TestBackend()
    assert b.timeout == 30
    assert b.max_payload_length == 24576
    assert b.retry_enabled == False

def test_base_truncation():
    b = _TestBackend(config={"MAX_PAYLOAD": 50})
    p = b._validate_payload("x" * 100)
    assert len(p) == 50

def test_slack_format():
    b = SlackBackend()
    p = json.loads(b._format_payload(SAMPLE_ALERTMANAGER))
    assert "text" in p
    assert "attachments" in p
    assert "FIRING" in p["text"]

def test_slack_single_alert():
    b = SlackBackend()
    p = json.loads(b._format_payload(SAMPLE_ALERT))
    assert "attachments" in p

def test_discord_format():
    b = DiscordBackend()
    p = json.loads(b._format_payload(SAMPLE_ALERTMANAGER))
    assert "embeds" in p
    assert p["username"] == "Prometheus"
    assert len(p["embeds"]) == 1

def test_telegram_format():
    b = TelegramBackend()
    p = json.loads(b._format_payload(SAMPLE_ALERTMANAGER))
    assert "text" in p
    assert "🔴" in p["text"]
    assert "<b>" in p["text"]

def test_telegram_truncation():
    b = TelegramBackend()
    big_alert = dict(SAMPLE_ALERTMANAGER)
    big_alert["alerts"] = [SAMPLE_ALERT] * 100  # would exceed 4096
    p = json.loads(b._format_payload(big_alert))
    assert len(p["text"]) <= 4096

def test_generic_format():
    b = GenericWebhookBackend()
    p = json.loads(b._format_payload(SAMPLE_ALERTMANAGER))
    assert p["status"] == "firing"
    assert "alerts" in p
