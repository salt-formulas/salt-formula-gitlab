{%- from "gitlab/map.jinja" import server with context %}
{%- if server.enabled %}

include:
{%- if server.source.engine == 'pkg' %}
- gitlab.server._service_pkg
{%- else %}
- gitlab.server._service_src
{%- endif %}

{%- if server.initial_data is defined %}

gitlab_backup_dirs:
  file.directory:
  - names:
    - /root/gitlab/scripts
    - /root/gitlab/flags
  - user: root
  - group: root
  - mode: 700
  - makedirs: true

/root/gitlab/scripts/restore.sh:
  file.managed:
  - user: root
  - group: root
  - source: salt://gitlab/conf/restore.sh
  - mode: 700
  - template: jinja
  - require:
    - file: gitlab_backup_dirs

restore_gitlab_repos:
  cmd.run:
  - name: /root/gitlab/scripts/restore.sh
  - unless: "[ -f /root/gitlab/flags/gitlab-installed ]"
  - cwd: /root
  - require:
    - file: /root/gitlab/scripts/restore.sh

{%- endif %}

{%- endif %}