{%- from "gitlab/map.jinja" import server with context %}
{%- if server.enabled %}

gitlab_server_packages:
  pkg.installed:
  - names: {{ server.pkgs }}

gitlab_server_user:
  user.present:
  - name: git
  - system: true
  - home: /var/opt/gitlab
  - require:
    - pkg: gitlab_server_packages

gitlab_server_group:
  group.present:
  - name: gitlab-www
  - require:
    - pkg: gitlab_server_packages

/etc/gitlab/gitlab.rb:
  file.managed:
  - source: salt://gitlab/files/gitlab.rb
  - template: jinja
  - require:
    - user: gitlab_server_user
    - group: gitlab_server_group

gitlab_server_reconfigure:
  cmd.wait:
  - name: gitlab-ctl reconfigure
  - user: root
  - watch:
    - file: /etc/gitlab/gitlab.rb
    - pkg: gitlab_server_packages

{%- if server.initial_data is defined %}

{%- endif %}

{%- endif %}
