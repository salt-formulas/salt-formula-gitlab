{%- from "gitlab/map.jinja" import server with context %}
{%- if server.enabled %}

include:
{%- if server.source.engine == 'pkg' %}
- gitlab.server._service_pkg
{%- else %}
- gitlab.server._service_src
{%- endif %}

{%- endif %}