#!/usr/bin/env python3
"""Tests for prom2notify configuration — adapted for YAML/INI hybrid loader."""

import json
import os
import unittest

from prom2notify.app import configuration, exceptions


class TestServer(unittest.TestCase):
    TEST_CONFIG_FILES_PATH = './tests/data/'
    DEFAULT_CONFIG_RELATIVE_PATH = './prom2notify/config.ini'

    def test_get_config_with_invalid_path(self):
        invalid_relative_path = os.path.join(self.TEST_CONFIG_FILES_PATH, 'invalid_path')
        self.assertRaises(FileNotFoundError, configuration._config_provided, invalid_relative_path)

    def test_get_config_without_required_keys_should_raise_exception(self):
        empty_config_relative_path = os.path.join(self.TEST_CONFIG_FILES_PATH, 'empty_config.ini')
        self.assertRaises(exceptions.MissingConnectorConfigKeyException, configuration._config_provided,
                          empty_config_relative_path)

    def test_get_config_without_override(self):
        provided_config_relative_path = os.path.join(self.TEST_CONFIG_FILES_PATH, 'not_overriding_defaults.ini')
        config = configuration._config_provided(provided_config_relative_path)
        # INI loaded — should have MICROSOFT_TEAMS key
        self.assertTrue('MICROSOFT_TEAMS' in config)
        self.assertIn('connector', config['MICROSOFT_TEAMS'])

    def test_get_config_overriding_defaults(self):
        provided_config_relative_path = os.path.join(self.TEST_CONFIG_FILES_PATH, 'overriding_defaults.ini')
        config = configuration._config_provided(provided_config_relative_path)
        self.assertEqual(config.get('HOST'), '1.1.1.1')
        self.assertEqual(config.get('PORT'), '9089')
        self.assertIn('connector', config['MICROSOFT_TEAMS'])

    def test_connectors_configured(self):
        provided_config_relative_path = os.path.join(self.TEST_CONFIG_FILES_PATH, 'multiple_connectors_config.ini')
        config = configuration._config_provided(provided_config_relative_path)
        teams = config['MICROSOFT_TEAMS']
        self.assertEqual(teams['connector1'], 'teams_webhook_url')
        self.assertEqual(teams['connector2'], 'another_teams_webhook_url')
        self.assertEqual(teams['connector3'], 'definitely_another_teams_webhook_url')

    def test_get_config_for_all_fields(self):
        provided_config_relative_path = os.path.join(self.TEST_CONFIG_FILES_PATH, 'all_fields.ini')
        config = configuration._config_provided(provided_config_relative_path)
        self.assertEqual(config.get('HOST'), '1.1.1.1')
        self.assertEqual(config.get('PORT'), '9089')
        self.assertEqual(config['MICROSOFT_TEAMS'].get('connector'), 'some_url')
        self.assertEqual(config.get('LOG_LEVEL'), 'TEST')
        self.assertEqual(config.get('LOG_FILE_PATH'), '/var/log/prom2notify/test.log')
        self.assertEqual(config.get('TEMPLATE_PATH'), 'jinja2/template/path')
        self.assertEqual(config.get('GROUP_ALERTS_BY'), 'name')


if __name__ == '__main__':
    unittest.main()
