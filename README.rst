
==============
Gitlab formula
==============

Gitlab is a free git repository management application based on Ruby on Rails.
It is distributed under the MIT License and its source code can be found on
Github. It is a very active project with a monthly release cycle and ideal for
businesses that want to keep their code private. Consider it as a self hosted
Github but open source.

Sample metadata
===============

Server role
-----------

Gitlab server with local MTA and PostgreSQL database

.. code-block:: yaml

    gitlab:
      server:
        enabled: true
        server_name: 'repo1.domain.com'
        source:
          engine: pkg
        database:
          engine: 'postgresql'
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
          from: 'gitlab@domain.com'
          no_reply: 'no-reply@domain.com'

Gitlab server from custom source code repository

.. code-block:: yaml

    gitlab:
      server:
        enabled: true
        source:
          engine: git
          host: git://git.domain.com
        server_name: 'repo.domain.com'

Gitlab server with LDAP authentication

.. code-block:: yaml

    gitlab:
      server:
        enabled: true
        version: '6.2'
        server_name: 'repo1.domain.com'
        identity:
          engine: ldap
          host: lda.domain.com
          base: OU=ou,DC=domain,DC=com
          port: 389
          uid: sAMAccountName
          method: plain
          bind_dn: uid=ldap,ou=Users,dc=domain,dc=com
          password: pwd


Client role
-----------

Gitlab groups/namespaces

.. code-block:: yaml

    gitlab:
      client:
        enabled: true
        server:
          url: http:/repo.domain.com/
          token: fdsfdsfdsfdsfds
        group:
          hovno53:
            enabled: true
            description: some tex2

Gitlab repository enforcement with import url repository and deploy keys and
hooks.

.. code-block:: yaml

    gitlab:
      client:
        enabled: true
        server:
          url: http:/repo.domain.com/
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


More information
================

* https://github.com/gitlabhq/gitlab-public-wiki/wiki/Trouble-Shooting-Guide


Documentation and Bugs
======================

To learn how to install and update salt-formulas, consult the documentation
available online at:

    http://salt-formulas.readthedocs.io/

In the unfortunate event that bugs are discovered, they should be reported to
the appropriate issue tracker. Use Github issue tracker for specific salt
formula:

    https://github.com/salt-formulas/salt-formula-gitlab/issues

For feature requests, bug reports or blueprints affecting entire ecosystem,
use Launchpad salt-formulas project:

    https://launchpad.net/salt-formulas

You can also join salt-formulas-users team and subscribe to mailing list:

    https://launchpad.net/~salt-formulas-users

Developers wishing to work on the salt-formulas projects should always base
their work on master branch and submit pull request against specific formula.

    https://github.com/salt-formulas/salt-formula-gitlab

Any questions or feedback is always welcome so feel free to join our IRC
channel:

    #salt-formulas @ irc.freenode.net
