{%- from "gitlab/map.jinja" import server with context %}
{%- if server.enabled %}

include:
- git
- ruby

gitlab_packages:
  pkg.installed:
  - names: {{ server.source_pkgs }}

gitlab_user:
  user.present:
  - name: git
  - system: True
  - home: /srv/gitlab

/srv/gitlab:
  file.directory:
  - user: git
  - group: git
  - mode: 755
  - makedirs: True
  - require:
    - user: gitlab_user
    - pkg: ruby_packages

gitlab_repo:
  git.latest:
  {%- if server.source is defined %}
  - name: {{ server.source.address }}
  {%- else %}
  - name: https://github.com/gitlabhq/gitlabhq.git
  {%- endif  %}
  - target: /srv/gitlab/gitlab
  - runas: root
  {%- if server.source is defined %}
  - rev: {{ server.source.rev }}
  {%- else %}
  - rev: {{ server.version|replace(".", "-") }}-stable
  {%- endif  %}
  - require:
    - pkg: git_packages
    - pkg: gitlab_packages
    - file: /srv/gitlab

gitlab_shell_repo:
  git.latest:
  - name: https://gitlab.com/gitlab-org/gitlab-shell.git
  - target: /srv/gitlab/gitlab-shell
  - runas: git
  - rev: v{{ server.shell_version }}
  - require:
    - git: gitlab_repo

/srv/gitlab/gitlab-shell/config.yml:
  file.managed:
  - source: salt://gitlab/files/config/config.yml
  - template: jinja
  - require:
    - git: gitlab_shell_repo

install_gitlab_shell:
  cmd.wait:
  - name: ./bin/install
  - cwd: /srv/gitlab/gitlab-shell
  - user: git
  - watch:
    - git: gitlab_shell_repo
  - require:
    - user: gitlab_user
    - file: /srv/gitlab/gitlab-shell/config.yml

/srv/gitlab/gitlab/config/gitlab.yml:
  file.managed:
  - source: salt://gitlab/files/config/gitlab.yml
  - template: jinja
  - require:
    - cmd: install_gitlab_shell

/srv/gitlab/gitlab/config/database.yml:
  file.managed:
  - source: salt://gitlab/files/config/database.yml
  - template: jinja
  - require:
    - cmd: install_gitlab_shell

/srv/gitlab/gitlab/config/unicorn.rb:
  file.managed:
  - source: salt://gitlab/files/config/unicorn.rb
  - template: jinja
  - require:
    - cmd: install_gitlab_shell

/etc/init.d/gitlab:
  file.managed:
  - source: salt://gitlab/files/config/gitlab
  - template: jinja
  - mode: 755
  - require:
    - cmd: install_gitlab_shell

gitlab_dirs:
  file.directory:
  - names:
    - /srv/gitlab/gitlab/tmp
    - /srv/gitlab/gitlab/tmp/pids
    - /srv/gitlab/gitlab/tmp/sockets
    - /srv/gitlab/gitlab/log
    - /srv/gitlab/gitlab/public/uploads
    - /srv/gitlab/gitlab/public/assets
    - /srv/gitlab/gitlab/.bundle
    - /srv/gitlab/satellites
  - user: git
  - group: git
  - mode: 755
  - makedirs: True
  require:
  - file: /srv/gitlab/gitlab/config.yml

/srv/gitlab/gitlab/.secret:
  file.managed:
  - source: salt://gitlab/files/config/secret
  - template: jinja
  - user: git
  - group: git
  - mode: 644
  require:
  - file: /srv/gitlab/gitlab/config.yml

/srv/gitlab/gitlab/.gitlab_shell_secret:
  file.managed:
  - source: salt://gitlab/files/config/secret
  - template: jinja
  - user: git
  - group: git
  - mode: 644
  require:
  - file: /srv/gitlab/gitlab/config.yml

/srv/gitlab/gitlab/db/schema.rb:
  file.managed:
  - user: git
  - group: git
  - mode: 644
  require:
  - file: /srv/gitlab/gitlab/config.yml

/srv/gitlab/gitlab/config/environments/production.rb:
  file.managed:
  - source: salt://gitlab/files/config/environment.rb
  - template: jinja
  - user: git
  - group: git
  - mode: 644
  require:
  - file: /srv/gitlab/gitlab/db/schema.rb

/srv/gitlab/gitlab/vendor/bundle:
  file.directory:
  - user: git
  - group: git
  - mode: 755
  - makedirs: True
  require:
  - file: /srv/gitlab/gitlab/config.yml

install_gitlab:
  cmd.wait:
  - name: sudo -u git -H bundle install --deployment --without development test
  - cwd: /srv/gitlab/gitlab
  - watch:
    - git: gitlab_repo
  - require:
    - file: /srv/gitlab/gitlab/.bundle
    - file: /srv/gitlab/gitlab/vendor/bundle
    - file: /srv/gitlab/gitlab/config/database.yml

{# fix missing file #}

/srv/gitlab/gitlab/config/environments/boot.rb:
  file.symlink:
    - target: /srv/gitlab/gitlab/config/boot.rb

migrate_gitlab_database:
  cmd.wait:
  - name: sudo -u git -H bundle exec rake db:migrate RAILS_ENV=production
  - cwd: /srv/gitlab/gitlab
  - watch:
    - cmd: install_gitlab

{% if server.version == '6.1' %}
migrate_gitlab_iids:
  cmd.wait:
  - name: sudo -u git -H bundle exec rake migrate_iids RAILS_ENV=production
  - cwd: /srv/gitlab/gitlab
  - watch:
    - cmd: migrate_gitlab_database
{% endif %}

clean_gitlab_assets:
  cmd.wait:
  - name: sudo -u git -H bundle exec rake assets:clean RAILS_ENV=production
  - cwd: /srv/gitlab/gitlab
  - watch:
    - cmd: migrate_gitlab_database
  - require:
    - file: /srv/gitlab/gitlab/public/assets

precompile_gitlab_assets:
  cmd.wait:
  - name: sudo -u git -H bundle exec rake assets:precompile RAILS_ENV=production
  - cwd: /srv/gitlab/gitlab
  - watch:
    - cmd: clean_gitlab_assets

clear_gitlab_cache:
  cmd.wait:
  - name: sudo -u git -H bundle exec rake cache:clear RAILS_ENV=production
  - cwd: /srv/gitlab/gitlab
  - watch:
    - cmd: precompile_gitlab_assets

setup_gitlab_git:
  cmd.run:
  - names:
    - sudo -u git -H git config --global user.name  "GitLab"
    - sudo -u git -H git config --global user.email "{{ server.mail_from }}"
  - cwd: /srv/gitlab
  - require:
    - cmd: install_gitlab

gitlab_service:
  service.running:
  - enable: true
  - name: {{ server.service }}
  - require:
    - file: /etc/init.d/gitlab
    - git: gitlab_repo
    - git: gitlab_shell_repo
    - file: /srv/gitlab/gitlab/.secret
    - file: /srv/gitlab/gitlab/config/environments/production.rb
  - watch:
    - git: gitlab_repo
    - git: gitlab_shell_repo
    - file: /srv/gitlab/gitlab/.secret
    - file: /srv/gitlab/gitlab/config/environments/production.rb

{%- if server.initial_data is defined %}

gitlab_backup_dirs:
  file.directory:
  - names:
    - /root/gitlab/scripts
    - /root/gitlab/flags
  - user: root
  - group: root
  - mode: 700
  - makedirs: true

/root/gitlab/scripts/restore.sh:
  file.managed:
  - user: root
  - group: root
  - source: salt://gitlab/files/config/restore.sh
  - mode: 700
  - template: jinja
  - require:
    - file: gitlab_backup_dirs

restore_gitlab_repos:
  cmd.run:
  - name: /root/gitlab/scripts/restore.sh
  - unless: "[ -f /root/gitlab/flags/gitlab-installed ]"
  - cwd: /root
  - require:
    - file: /root/gitlab/scripts/restore.sh

{%- endif %}

{%- endif %}
