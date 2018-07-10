{%- from "gitlab/map.jinja" import client with context %}
{%- if client.enabled %}

{%- for group_name, group in client.get('group', {}).iteritems() %}

{%- if group.get('enabled', true) %}

gitlab_group_{{ group_name }}:
  gitlab.group_present:
  - name: {{ group_name }}
{%- if group.description is defined  %}
  - description: {{ group.description }}
{%- endif  %}

{%- else %}

gitlab_group_{{ group_name }}:
  gitlab.group_absent:
  - name: {{ group_name }}

{%- endif %}

{%- endfor %}

{%- for repo_name, repo in client.get('repository', {}).iteritems() %}

{%- if repo.enabled %}

gitlab_repo_{{ repo_name }}:
  gitlab.project_present:
  - name: {{ repo_name }}
  {%- if repo.import_url is defined  %}
  - import_url: {{ repo.import_url }}
  {%- endif  %}
  {%- if repo.title is defined  %}
  - title: {{ repo.title }}
  {%- endif  %}
  {%- if repo.description is defined  %}
  - description: {{ repo.description }}
  {%- endif  %}

{%- endif %}

{%- for key_name, key in repo.get('deploy_key', {}).iteritems() %}

{%- if key.enabled %}

gitlab_deploykey_{{ repo_name }}_{{ key_name }}:
  gitlab.deploykey_present:
  - name: {{ key_name }}
  - key: {{ key.key }}
  - project: {{ repo_name }}

{%- else %}

gitlab_deploykey_{{ repo_name }}_{{ key_name }}:
  gitlab.deploykey_absent:
  - name: {{ key_name }}
  - key: {{ key.key }}
  - project: {{ repo_name }}

{%- endif %}

{%- endfor %}

{%- for key_name, key in client.get('global_deploy_key', {}).iteritems() %}

{%- if key.enabled %}

gitlab_deploykey_{{ repo_name }}_{{ key_name }}:
  gitlab.deploykey_present:
  - name: {{ key_name }}
  - key: {{ key.key }}
  - project: {{ repo_name }}

{%- else %}

gitlab_deploykey_{{ repo_name }}_{{ key_name }}:
  gitlab.deploykey_absent:
  - name: {{ key_name }}
  - key: {{ key.key }}
  - project: {{ repo_name }}

{%- endif %}

{%- endfor %}

{%- endfor %}

{%- endif %}