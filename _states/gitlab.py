# -*- coding: utf-8 -*-
'''
Management of Gitlab projects
==============================

:depends:   - pyapi-gitlab Python module
:configuration: See :py:mod:`salt.modules.gitlab` for setup instructions.

.. code-block:: yaml

    Gitlab projects:
      gitlab.project_present:
      - names:
        - namespace1/repository1
        - namespace1/repository2
        - namespace2/repository1

    jenkins:
      gitlab.hook_present:
      - name: http://url_of_hook
      - project: 'namespace/repository'

    some_deploy_key:
      gitlab.deploykey_present:
      - name: title_of_key
      - key: public_key
      - project: 'namespace/repository'
'''


def __virtual__():
    '''
    Only load if the gitlab module is in __salt__
    '''
    return 'gitlab' if 'gitlab.auth' in __salt__ else False


def project_present(name, default_branch="master", description=None, **kwargs):
    '''
    Ensures that the gitlab project exists
    
    :param name: new project name
    :param default_branch: default branch
    :param description: short project description
    :param import_url: https://git.tcpcloud.eu/python-apps/django-kedb.git
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Repository "{0}" already exists'.format(name)}

    # Check if project is already present
    project = __salt__['gitlab.project_get'](name=name, **kwargs)


    if 'Error' not in project:

        #if default_branch and not "default_branch" in kwargs:
        #  kwargs["default_branch"] = default_branch
        #if project[name.split("/")[1]]['default_branch'] != default_branch:
        #    __salt__['gitlab.project_update'](name=name, **kwargs)
        #    comment = 'Repository "{0}" has been updated'.format(name)
        #    ret['comment'] = comment
        #    ret['changes']['Default branch'] = 'Updated'
        if description and not "description" in kwargs:
          kwargs["description"] = description
        if project[name.split("/")[1]]['description'] != description:
            __salt__['gitlab.project_update'](name=name, **kwargs)
            comment = 'Repository "{0}" has been updated'.format(name)
            ret['comment'] = comment
            ret['changes']['Description'] = 'Updated'
    else:
        # Create project
        __salt__['gitlab.project_create'](name, **kwargs)
        ret['comment'] = 'Repo "{0}" has been added'.format(name)
        ret['changes']['Repo'] = 'Created'
    return ret


def project_absent(name, profile=None, **kwargs):
    '''
    Ensure that the gitlab project is absent.

    name
        The name of the project that should not exist
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Repository "{0}" is already absent'.format(name)}

    if profile and not "profile" in kwargs:
      kwargs["profile"] = profile

    # Check if project is present
    project = __salt__['gitlab.project_get'](name=name, **kwargs)
    if 'Error' not in project:
        # Delete project
        __salt__['gitlab.project_delete'](name=name, **kwargs)
        ret['comment'] = 'Repository "{0}" has been deleted'.format(name)
        ret['changes']['Repository'] = 'Deleted'

    return ret


def deploykey_present(name, key, project, **kwargs):
    '''
    Ensure deploy key present in Gitlab project

    :param title: title of the key
    :param key: the key itself
    :param project: project id

    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Deploy key "{0}" already exists in project {1}'.format(name, project)}

    # Check if key is already present
    dkey = __salt__['gitlab.deploykey_get'](name,
                                            project,
                                            **kwargs)

    if 'Error' not in dkey:
        return ret
    else:
        # Create deploy key
        dkey = __salt__['gitlab.deploykey_create'](name, 
                                                   key,
                                                   project,
                                                   **kwargs)
        ret['comment'] = 'Deploy key "{0}" has been added'.format(name)
        ret['changes']['Deploykey'] = 'Created'
    return ret


def deploykey_absent(name, key, project, **kwargs):
    '''
    Ensure that the deploy key doesn't exist in Gitlab project

    name
        The name of the service that should not exist
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Deploy key "{0}" is already absent'.format(name)}

    # Check if key is present
    dkey = __salt__['gitlab.deploykey_get'](name,
                                            project,
                                            **kwargs)
    if 'Error' not in dkey:
        # Delete key
        __salt__['gitlab.deploykey_delete'](name,
                                            key,
                                            project,
                                            **kwargs)
        ret['comment'] = 'Deploy key "{0}" has been deleted'.format(name)
        ret['changes']['Deploykey'] = 'Deleted'

    return ret


def hook_present(name, project, **connection_args):
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
                                       **connection_args)

    if 'Error' not in hook:
        return ret
    else:
        # Create hook
        hook = __salt__['gitlab.hook_create'](name,
                                              project_name=project,
                                              **connection_args)
        ret['comment'] = 'Hook "{0}" has been added'.format(name)
        ret['changes']['Hook'] = 'Created'
    return ret
