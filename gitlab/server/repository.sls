{%- from "gitlab/map.jinja" import server with context %}

{%- for repo_name, repo in server.repository.iteritems() %}

{%- for key in repo.get('deploy_keys', []) %}

gitlab_deploykey_{{ repo_name }}_{{ key.name }}:
  gitlab.deploykey_present:
    - name: {{ key.name }}
    - key: {{ key.key }}
    - project: {{ repo_name }}

{%- endfor %}

{%- for hook in repo.get('hooks', []) %}

gitlab_hook_{{ repo_name }}_{{ hook.address }}:
  gitlab.hook_present:
    - name: {{ hook.address }}
    - project: {{ repo_name }}

{%- endfor %}

{%- endfor %}