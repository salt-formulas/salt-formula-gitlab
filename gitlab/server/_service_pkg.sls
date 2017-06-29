{%- from "gitlab/map.jinja" import server with context %}
{%- if server.enabled %}

gitlab_packages:
  pkg.installed:
  - names: {{ server.pkgs }}

{%- endif %}
