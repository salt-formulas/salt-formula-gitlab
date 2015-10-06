{%- from "gitlab/map.jinja" import client with context %}
{%- if client.enabled %}

gitlab_client_packages:
  pkg.installed:
  - names:
    - python-pip
  pip.installed:
  - name: {{ client.pip_pkg }}
  - require:
    - pkg: gitlab_client_packages

{%- for repo_name, repo in client.repository.iteritems() %}

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

{%- for hook_name, hook in repo.get('hook', {}).iteritems() %}

{%- if hook.enabled %}

gitlab_hook_{{ repo_name }}_{{ hook_name }}:
  gitlab.hook_present:
  - name: {{ hook.address }}
  - project: {{ repo_name }}

{%- else %}

gitlab_hook_{{ repo_name }}_{{ hook_name }}:
  gitlab.hook_absent:
  - name: {{ hook.address }}
  - project: {{ repo_name }}

{%- endif %}

{%- endfor %}

{%- for hook_name, hook in client.get('global_hook', {}).iteritems() %}

{%- if hook.enabled %}

gitlab_hook_{{ repo_name }}_{{ hook_name }}:
  gitlab.hook_present:
  - name: {{ hook.address }}
  - project: {{ repo_name }}

{%- else %}

gitlab_hook_{{ repo_name }}_{{ hook_name }}:
  gitlab.hook_absent:
  - name: {{ hook.address }}
  - project: {{ repo_name }}

{%- endif %}

{%- endfor %}

{%- endfor %}

{%- endif %}