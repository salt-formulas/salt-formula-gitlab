# -*- coding: utf-8 -*-
'''
Management of Gitlab resources
==============================

:depends:   - python-gitlab Python module
:configuration: See :py:mod:`salt.modules.gitlab` for setup instructions.

Enforce the project/repository
------------------------------

.. code-block:: yaml

    Gitlab_project:
      gitlab.project_present:
        name:

Enforce the repository hook
---------------------------

.. code-block:: yaml

    jenkins:
      gitlab.hook_present:
      - project: 'namespace/repository'
      - hook: http://url_of_hook

Enforce the repository deploy key
---------------------------------

.. code-block:: yaml

    some_deploy_key:
      gitlab.deploykey_present:
      - project: 'namespace/repository'
      - name: title_of_key
      - key: public_key

'''


def __virtual__():
    '''
    Only load if the gitlab module is in __salt__
    '''
    return 'gitlab' if 'gitlab.auth' in __salt__ else False


def group_present(name, path=None, description="", visibility_level=20, **kwargs):
    '''
    Ensures that the gitlab group exists
    
    :param name: Group name
    :param path: Group path
    :param description: Group description
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Group "{0}" already exists'.format(name)}
    if path == None:
        path = name
    project = __salt__['gitlab.group_get'](name, **kwargs)
    if 'Error' not in project:
        pass
    else:
        __salt__['gitlab.group_create'](name, path, description, visibility_level, **kwargs)
        ret['comment'] = 'Group {0} has been created'.format(name)
        ret['changes']['Group'] = 'Created'
    return ret


def group_absent(name, **kwargs):
    '''
    Ensure that the group doesn't exist in Gitlab

    :param name: The name of the group that should not exist
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Group "{0}" is already absent'.format(name)}
    group = __salt__['gitlab.group_get'](name, **kwargs)
    if 'Error' not in group:
        __salt__['gitlab.group_delete'](name, **kwargs)
        ret['comment'] = 'Group "{0}" has been deleted'.format(name)
        ret['changes']['Group'] = 'Deleted'

    return ret


def project_present(name, description=None, default_branch="master", **kwargs):
    '''
    Ensures that the gitlab project exists
    
    :param name: Project path with namespace
    :param description: Project description
    :param default_branch: Default repository branch
    :param import_url: https://github.com/python-namespace/django-app.git
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Repository "{0}" already exists'.format(name)}

    # Check if project is already present
    project = __salt__['gitlab.project_get'](name, **kwargs)
    print project
    if not 'Error' in project:
        pass
#        if description and not "description" in kwargs:
#          kwargs["description"] = description
#        if project[name.split("/")[1]]['description'] != description:
#            __salt__['gitlab.project_update'](name=name, **kwargs)
#            comment = 'Repository "{0}" has been updated'.format(name)
#            ret['comment'] = comment
#            ret['changes']['Description'] = 'Updated'
    else:
        __salt__['gitlab.project_create'](name, description, default_branch, **kwargs)
        ret['comment'] = 'Repository {0} has been created'.format(name)
        ret['changes']['Repo'] = 'Created'
    return ret


def project_absent(name, **kwargs):
    '''
    Ensure that the gitlab project is absent.

    name
        The name of the project that should not exist
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Repository "{0}" is already absent'.format(name)}
    project = __salt__['gitlab.project_get'](name=name, **kwargs)
    if 'Error' not in project:
        __salt__['gitlab.project_delete'](name=name, **kwargs)
        ret['comment'] = 'Repository "{0}" has been deleted'.format(name)
        ret['changes']['Repository'] = 'Deleted'
    return ret


def deploykey_present(project, key, title, **kwargs):
    '''
    Ensure deploy key present for Gitlab repository

    :param project: Project name (full path)
    :param key: The key value
    :param title: Human name for the key

    Pillar Example:

    .. code-block:: yaml

        repository:
          name-space/repo-name:
            deploy_key:
              key_name:
                enabled: true
                key: ssh-rsa vfdsfdsfewf32rewgrdsgresgrdsvg
    '''
    ret = {'name': title,
           'changes': {},
           'result': True,
           'comment': 'Deploy key "{0}" already exists in project {1}'.format(title, project)}
    deploy_key = __salt__['gitlab.deploykey_get'](project, key, **kwargs)
    if 'Error' not in deploy_key:
        return ret
    else:
        deploy_key = __salt__['gitlab.deploykey_create'](project, key, title, **kwargs)
        ret['comment'] = 'Deploy key {0} has been added'.format(title)
        ret['changes']['Deploykey'] = 'Created'
    return ret


def deploykey_absent(project, key, title, **kwargs):
    '''
    Ensure that the deploy key doesn't exist in Gitlab project

    :param key: The key value
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Deploy key "{0}" is already absent'.format(name)}
    dkey = __salt__['gitlab.deploykey_get'](name,
                                            project,
                                            **kwargs)
    if 'Error' not in dkey:
        __salt__['gitlab.deploykey_delete'](name,
                                            key,
                                            project,
                                            **kwargs)
        ret['comment'] = 'Deploy key "{0}" has been deleted'.format(name)
        ret['changes']['Deploykey'] = 'Deleted'
    return ret


def hook_present(name, project, **kwargs):
    '''
    Ensure hook present in Gitlab project

    name
        The URL of hook

    project
        path to project, i.e. namespace/repo-name

    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Hook "{0}" already exists in project {1}'.format(name, project)}

    # Check if key is already present
    hook = __salt__['gitlab.hook_get'](name,
                                       project_name=project,
                                       **kwargs)

    if 'Error' not in hook:
        return ret
    else:
        # Create hook
        hook = __salt__['gitlab.hook_create'](name,
                                              project_name=project,
                                              **kwargs)
        ret['comment'] = 'Hook "{0}" has been added'.format(name)
        ret['changes']['Hook'] = 'Created'
    return ret
