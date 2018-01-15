{% from "gitlab/map.jinja" import runner with context %}
{%- if runner.enabled %}

gitlab-runner_dirs:
  file.directory:
  - names:
    - /srv/gitlab-runner
  - makedirs: true
  - group: root
  - user: root

/srv/gitlab-runner/config.toml:
  file.managed:
  - source: salt://gitlab/conf/runner_config.toml
  - template: jinja

{%- endif %}
