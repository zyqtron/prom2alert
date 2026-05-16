#!/usr/bin/env python3
"""Tests for Prometheus alert JSON processing — adapted for multi-backend."""
import json
import os
import unittest

from prom2notify.app.sender import AlertSender
from prom2notify.prometheus.message_schema import MessageSchema


class TestJSONFields(unittest.TestCase):
    TEST_CONFIG_FILES_PATH = './tests/data/'

    def _load(self, filename):
        with open(os.path.join(self.TEST_CONFIG_FILES_PATH, filename)) as f:
            return json.load(f)

    def test_json_with_all_fields(self):
        """Rendered alert should contain expected fields."""
        json_received = self._load('all_ok.json')
        alerts = MessageSchema().load(json_received)
        rendered = AlertSender()._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)
        data = json.loads(rendered[0])
        self.assertIn('status', data)
        self.assertIn('severity', data)
        self.assertIn('summary', data)
        self.assertIn('instance', data)

    def test_json_without_instance_field(self):
        json_received = self._load('without_instance_field.json')
        alerts = MessageSchema().load(json_received)
        rendered = AlertSender()._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_json_without_mandatory_field(self):
        json_received = self._load('without_mandatory_field.json')
        alerts = MessageSchema().load(json_received)
        rendered = AlertSender()._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_json_without_optional_field(self):
        json_received = self._load('without_optional_field.json')
        alerts = MessageSchema().load(json_received)
        rendered = AlertSender()._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_fingerprint(self):
        json_received = self._load('all_ok.json')
        alerts = MessageSchema().load(json_received)
        self.assertGreater(len(alerts), 0)
        self.assertIn('fingerprint', json_received['alerts'][0])

    def test_without_fingerprint(self):
        json_received = self._load('without_fingerprint.json')
        alerts = MessageSchema().load(json_received)
        self.assertGreater(len(alerts), 0)

    def test_compose_all(self):
        json_received = self._load('all_ok.json')
        alerts = MessageSchema().load(json_received)
        rendered = AlertSender()._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_with_common_items(self):
        json_received = self._load('with_common_items.json')
        alerts = MessageSchema().load(json_received)
        rendered = AlertSender()._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_grouping_multiple_alerts(self):
        json_received = self._load('all_ok_multiple.json')
        alerts = MessageSchema().load(json_received)
        rendered = AlertSender(group_alerts_by='name')._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_with_extra_labels(self):
        json_received = self._load('all_ok_extra_labels.json')
        alerts = MessageSchema(exclude_fields=('pod_name',)).load(json_received)
        rendered = AlertSender()._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_with_extra_annotations(self):
        json_received = self._load('all_ok_extra_annotations.json')
        alerts = MessageSchema(exclude_annotations=('message',)).load(json_received)
        rendered = AlertSender()._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_with_too_long_payload(self):
        json_received = self._load('all_ok_multiple.json')
        alerts = MessageSchema().load(json_received)
        rendered = AlertSender(group_alerts_by='name', teams_client_config={'MAX_PAYLOAD': 1600})._create_alerts(alerts)
        self.assertGreater(len(rendered), 0)

    def test_alert_validation(self):
        json_received = self._load('all_ok.json')
        alerts = MessageSchema().load(json_received)
        for alert in alerts:
            self.assertTrue(hasattr(alert, 'name'))
            self.assertTrue(hasattr(alert, 'status'))
            self.assertTrue(hasattr(alert, 'severity'))
            self.assertTrue(hasattr(alert, 'summary'))


if __name__ == '__main__':
    unittest.main()
