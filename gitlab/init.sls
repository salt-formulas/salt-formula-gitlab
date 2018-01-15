{%- if pillar.gitlab is defined %}
include:
{%- if pillar.gitlab.server is defined %}
- gitlab.server
{%- endif %}
{%- if pillar.gitlab.client is defined %}
- gitlab.client
{%- endif %}
{%- if pillar.gitlab.runner is defined %}
- gitlab.runner
{%- endif %}
{%- endif %}
