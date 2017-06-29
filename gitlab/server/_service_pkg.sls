{%- from "gitlab/map.jinja" import server with context %}
{%- if server.enabled %}

gitlab_server_packages:
  pkg.installed:
  - names: {{ server.pkgs }}

/etc/gitlab/gitlab.rb:
  file.managed:
  - source: salt://gitlab/files/gitlab.rb
  - template: jinja
  - require:
    - pkg: gitlab_server_packages

gitlab_server_reconfigure:
  cmd.wait:
  - name: gitlab-ctl reconfigure
  - user: root
  - watch:
    - file: /etc/gitlab/gitlab.rb
    - pkg: gitlab_server_packages

{%- endif %}
