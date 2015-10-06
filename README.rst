
======
Gitlab
======

Gitlab is a free git repository management application based on Ruby on Rails. It is distributed under the MIT License and its source code can be found on Github. It is a very active project with a monthly release cycle and ideal for businesses that want to keep their code private. Consider it as a self hosted Github but open source.

Sample pillars
==============

Gitlab server with local MTA and MySQL database

    gitlab:
      server:
        enabled: true
        version: '6.5'
        server_name: 'repo1.domain.com'
        mail_from: 'gitlab@domain.com'
        support_email: 'webmaster@domain.com'
        database:
          engine: 'mysql'
          host: 'locslhost'
          name: 'gitlab'
          password: 'LfTno5mYdZmRfoPV'
          user: 'gitlab'
        mail:
          engine: 'smtp'
          host: 'localhost'
          port: 25
          domain: 'domain.com'
          use_tls: false

Gitlab server from custom source code repository

    gitlab:
      server:
        enabled: true
        version: '6.3'
        source:
          engine: git
          address: git://repo.domain.com
          rev: '6.3'
        server_name: 'repo1.domain.com'
        mail_from: 'gitlab@domain.com'
        support_email: 'webmaster@domain.com'

Gitlab server with LDAP authentication

    gitlab:
      server:
        enabled: true
        version: '6.2'
        identity:
          engine: ldap
          host: lda.domain.com
          base: OU=ou,DC=domain,DC=com
          port: 389
          uid: sAMAccountName
          method: plain
          bind_dn: uid=ldap,ou=Users,dc=domain,dc=com
          password: pwd
        server_name: 'repo1.domain.com'
        mail_from: 'gitlab@domain.com'
        support_email: 'webmaster@domain.com'

Gitlab repository enforcement from client side using token with import url repository and deploy keys and hooks

    gitlab:
      client:
        enabled: true
        server:
          host: repo.domain.com
          token: fdsfdsfdsfdsfds
        repository:
          name-space/repo-name:
            enabled: true
            import_url: https://repo01.domain.com/namespace/repo.git
            description: Repo description
            deploy_key:
              keyname:
                enabled: true
                key: public_part_of_ssh_key
            hook:
              hookname:
                enabled: true
                address: http://ci-tool/

Usage
=====

The following rake task will resync all of the SSH keys.

    sudo -u git -H bundle exec rake gitlab:shell:setup RAILS_ENV=production

The following rake task will recreate all of the satellites.

    sudo -u git -H bundle exec rake gitlab:satellites:create RAILS_ENV=production

Read more
=========

* https://github.com/gitlabhq/gitlabhq/blob/6-1-stable/doc/install/installation.md
* https://github.com/gitlabhq/gitlabhq/blob/master/doc/update/6.0-to-6.1.md
* https://github.com/gitlabhq/gitlabhq/tree/master/doc/update
* https://wiki.archlinux.org/index.php/gitlab
* https://github.com/gitlabhq/gitlabhq/issues/6687
* https://github.com/gitlabhq/gitlab-public-wiki/wiki/Trouble-Shooting-Guide
