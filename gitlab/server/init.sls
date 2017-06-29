{%- from "gitlab/map.jinja" import server with context %}
include:
- gitlab.server.service
- gerrit.server.service
