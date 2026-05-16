#!/usr/bin/env python3
"""
prom2notify.app.configuration — Application configuration loader.

Supports legacy INI config (Microsoft Teams) and new YAML config (multi-backend).
"""

import argparse
import configparser
import logging.config
import os
import sys

import yaml

from prom2notify import root
from prom2notify.app.exceptions import MissingConnectorConfigKeyException

log = logging.getLogger('prom2notify')


def _config_command_line():
    parser = argparse.ArgumentParser(
        description='Receives alert notifications from Prometheus Alertmanager '
                    'and sends them to multiple notification channels (Teams, Slack, Discord, Telegram, webhooks).')

    parser.add_argument('-c', '--configpath', help='config file path (INI or YAML)', required=False)
    parser.add_argument('-g', '--groupalertsby', help='group alerts with same attribute into one alert', required=False)
    parser.add_argument('-l', '--logfilepath', help='log file path', required=False)
    parser.add_argument('-v', '--loglevel', help='log level', required=False)
    parser.add_argument('-t', '--templatepath', help='Jinja2 template file path', required=False)
    parser.add_argument('-s', '--labelsexcluded', help='prometheus custom labels to be ignored', required=False)
    parser.add_argument('-a', '--annotationsexcluded', help='prometheus custom annotations to be ignored', required=False)
    parser.add_argument('-m', '--enablemetrics', action='store_true', help='enable Prom2Notify Prometheus metrics', required=False)
    return parser.parse_args()


def _load_yaml_config(filepath):
    """Load a modern YAML config file with multi-backend support."""
    with open(filepath) as f:
        config = yaml.safe_load(f)

    backends = {}
    if 'backends' in config:
        for name, cfg in config['backends'].items():
            btype = cfg.get('type', 'generic')
            url = cfg.get('url', '')
            bconfig = cfg.get('config', {})
            backends[name] = (btype, url, bconfig if bconfig else None)

    result = {
        'BACKENDS': backends,
    }

    # Optional: fallback legacy Teams config
    if 'microsoft_teams' in config and 'MICROSOFT_TEAMS' not in result:
        result['MICROSOFT_TEAMS'] = config['microsoft_teams']

    # Config values
    for key, cfg_key in [('LOG_LEVEL', 'loglevel'), ('LOG_FILE_PATH', 'logfile'),
                          ('TEMPLATE_PATH', 'template'), ('GROUP_ALERTS_BY', 'group_alerts_by'),
                          ('HOST', 'host'), ('PORT', 'port')]:
        if cfg_key in config:
            result[key] = config[cfg_key]

    if 'labels_excluded' in config:
        result['LABELS_EXCLUDED'] = tuple(config['labels_excluded'])
    if 'annotations_excluded' in config:
        result['ANNOTATIONS_EXCLUDED'] = tuple(config['annotations_excluded'])

    return result


def _load_ini_config(filepath):
    """Load a legacy INI config file (original prom2teams format)."""
    config = configparser.ConfigParser()
    try:
        with open(filepath) as f:
            config.read_file(f)
    except configparser.NoSectionError:
        raise MissingConnectorConfigKeyException('missing required section in config')

    result = {}

    if 'Microsoft Teams' in config:
        result['MICROSOFT_TEAMS'] = {}
        for key, val in config['Microsoft Teams'].items():
            result['MICROSOFT_TEAMS'][key] = val

    if 'Backends' in config:
        backends = {}
        for key, val in config['Backends'].items():
            parts = val.split('|', 2)
            btype = parts[0].strip() if len(parts) > 0 else 'generic'
            url = parts[1].strip() if len(parts) > 1 else ''
            bconfig = parts[2].strip() if len(parts) > 2 else None
            backends[key] = (btype, url, bconfig)
        result['BACKENDS'] = backends

    # No backends configured — raise
    if 'BACKENDS' not in result and 'MICROSOFT_TEAMS' not in result:
        raise MissingConnectorConfigKeyException('missing required section in config')

    if 'Microsoft Teams Client' in config:
        result['TEAMS_CLIENT_CONFIG'] = {
            'TIMEOUT': config.getint('Microsoft Teams Client', 'RequestTimeout', fallback=30),
            'RETRY_ENABLE': config.getboolean('Microsoft Teams Client', 'RetryEnable', fallback=False),
            'RETRY_WAIT_TIME': config.getint('Microsoft Teams Client', 'RetryWaitTime', fallback=60),
            'MAX_PAYLOAD': config.getint('Microsoft Teams Client', 'MaxPayload', fallback=24576),
        }

    if 'Template' in config and 'Path' in config['Template']:
        result['TEMPLATE_PATH'] = config['Template']['Path']
    if 'Log' in config:
        if 'Level' in config['Log']:
            result['LOG_LEVEL'] = config['Log']['Level']
        if 'Path' in config['Log']:
            result['LOG_FILE_PATH'] = config['Log']['Path']
    if 'Group Alerts' in config:
        result['GROUP_ALERTS_BY'] = config['Group Alerts']['Field']
    if 'HTTP Server' in config:
        if 'Host' in config['HTTP Server']:
            result['HOST'] = config['HTTP Server']['Host']
        if 'Port' in config['HTTP Server']:
            result['PORT'] = config['HTTP Server']['Port']
    if 'Labels' in config:
        result['LABELS_EXCLUDED'] = tuple(config['Labels']['Excluded'].replace(' ', '').split(','))
    if 'Annotations' in config:
        result['ANNOTATIONS_EXCLUDED'] = tuple(config['Annotations']['Excluded'].replace(' ', '').split(','))

    return result


def _config_provided(filepath):
    """Detect config format (YAML or INI) and load."""
    if filepath.endswith(('.yml', '.yaml')):
        return _load_yaml_config(filepath)
    else:
        return _load_ini_config(filepath)


def setup_logging(application):
    with open(os.path.join(root, 'config/logging.yml'), 'rt') as f:
        config = yaml.safe_load(f.read())
        for logger in config['loggers']:
            config['loggers'][logger]['level'] = application.config.get('LOG_LEVEL', 'INFO')
        config['root']['level'] = application.config.get('LOG_LEVEL', 'INFO')
        config['loggers']['prom2notify_app']['level'] = 'INFO'

        environment = os.getenv('APP_ENVIRONMENT', 'None')
        log_file = application.config.get('LOG_FILE_PATH', '/var/log/prom2notify.log')
        if environment in ('pro', 'pre') and log_file:
            config['handlers']['file']['filename'] = log_file
            for logger in config['loggers']:
                config['loggers'][logger]['handlers'] = ['file']
            config['root']['handlers'] = ['file']
        else:
            config['handlers'].pop('file', None)

        logging.config.dictConfig(config)


def _setup_metrics(application):
    """Start Prometheus metrics exporter."""
    if os.environ.get('DEBUG_METRICS'):
        if application.config.get('ENV') == 'werkzeug':
            from prometheus_flask_exporter import PrometheusMetrics
            PrometheusMetrics(application)
        else:
            from prometheus_flask_exporter.multiprocess import UWsgiPrometheusMetrics
            metrics = UWsgiPrometheusMetrics(application)
            metrics.start_http_server(int(os.getenv('PROMETHEUS_MULTIPROC_PORT', 9100)))


def config_app(application):
    try:
        # Load default configuration
        application.config.from_object('prom2notify.config.settings')

        # Load instance config if exists
        instance = os.path.join(os.path.join(root, os.pardir), 'instance')
        config_file = os.path.join(instance, 'config.py')
        if os.path.isdir(instance) and os.path.exists(config_file):
            application.config.from_pyfile(config_file)

        # Load from APP_CONFIG_FILE env var or command line
        args = _config_command_line()
        config_path = None
        if 'APP_CONFIG_FILE' in os.environ:
            config_path = os.environ.get('APP_CONFIG_FILE')
        if args.configpath:
            config_path = args.configpath

        if config_path and os.path.exists(config_path):
            provided = _config_provided(config_path)
            for key, val in provided.items():
                application.config[key] = val

        # Apply CLI overrides
        if args.loglevel:
            application.config['LOG_LEVEL'] = args.loglevel
        if args.logfilepath:
            application.config['LOG_FILE_PATH'] = args.logfilepath
        if args.templatepath:
            application.config['TEMPLATE_PATH'] = args.templatepath
        if args.groupalertsby:
            application.config['GROUP_ALERTS_BY'] = args.groupalertsby
        if args.enablemetrics or os.environ.get('PROM2TEAMS_PROMETHEUS_METRICS'):
            os.environ['DEBUG_METRICS'] = 'True'
            _setup_metrics(application)

    except MissingConnectorConfigKeyException as e:
        sys.exit(f'Config error: {e}')
