#!/bin/sh

{%- from "gitlab/map.jinja" import server with context %}

scp -r backupninja@{{ server.initial_data.source }}:/srv/backupninja/{{ server.initial_data.host }}/srv/gitlab/repositories/repositories.0/* /srv/gitlab/repositories
cd /srv/gitlab
chown git:git ./repositories -R
touch /root/gitlab/flags/gitlab-installed
