{%- from "gitlab/map.jinja" import client with context %}
{%- if client.enabled %}

gitlab_client_packages:
  pkg.installed:
  - names: {{ client.pkg }}

{%- endif %}
