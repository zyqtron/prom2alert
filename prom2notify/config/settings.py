#!/usr/bin/env python3
"""
prom2notify.config.settings — Default application configuration.
"""

import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
APP_NAME = 'prom2notify'
API_V1_URL_PREFIX = '/v1'
API_V2_URL_PREFIX = '/v2'
HOST = '0.0.0.0'
PORT = 8080
LOG_LEVEL = 'INFO'
LOG_FILE_PATH = '/var/log/prom2notify.log'

# Backend connectors: name -> (type, url, config_dict_or_None)
# type can be: teams, teams_template, slack, discord, telegram, generic
BACKENDS = {
    # 'teams': ('teams', 'https://outlook.office.com/webhook/...', None),
    # 'slack': ('slack', 'https://hooks.slack.com/services/...', None),
}

# Legacy settings (kept for backward compat)
MICROSOFT_TEAMS = {}
LABELS_EXCLUDED = ()
ANNOTATIONS_EXCLUDED = ()
GROUP_ALERTS_BY = None
TEMPLATE_PATH = None
TEAMS_CLIENT_CONFIG = None
APP_CONFIG_FILE = None
FINISH_INIT = False
