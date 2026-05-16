#!/bin/sh
python /opt/prom2notify/replace_config.py

if [ ! -f "/opt/prom2notify/config.ini" ]; then
    mv /opt/prom2notify/config.ini.tmp /opt/prom2notify/config.ini
fi

if [ ! -f "/opt/prom2notify/uwsgi.ini" ]; then
    mv /opt/prom2notify/uwsgi.ini.tmp /opt/prom2notify/uwsgi.ini
fi

uwsgi /opt/prom2notify/uwsgi.ini
