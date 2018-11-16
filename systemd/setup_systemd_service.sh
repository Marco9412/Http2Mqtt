#!/bin/bash

cd ..

# Generate service description
echo -e "[Unit]
Description=uWSGI instance to serve Http2Mqtt
After=network.target

[Service]
User=$(whoami)
Group=www-data
WorkingDirectory=$(pwd)
Environment=\"PATH=/usr/local/bin\"
ExecStart=/usr/local/bin/uwsgi --ini wsgi/http2mqtt.ini

[Install]
WantedBy=multi-user.target
" > systemd/Http2Mqtt.service

# Generate uwsgi config file
./wsgi/generate_uswgi_ini.sh

# Enable and start service
sudo cp systemd/Http2Mqtt.service /etc/systemd/system/
sudo systemctl start Http2Mqtt
sudo systemctl enable Http2Mqtt

