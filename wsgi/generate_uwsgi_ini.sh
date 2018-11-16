#!/bin/bash

echo -e "[uwsgi]
module = flaskr/wsgi:app

master = true
processes = 5

socket = http2mqtt.sock
chmod-socket = 660
uid = $(whoami)
gid = www-data
vacuum = true

die-on-term = true
" > http2mqtt.ini
