# -*- coding: utf-8 -*-
'''
Module for handling Gitlab calls.

:optdepends:    - pyapi-gitlab Python adapter
:configuration: This module is not usable until the following are specified
    either in a pillar or in the minion's config file::

        gitlab.user: admin
        gitlab.password: verybadpass
        gitlab.url: 'https://gitlab.domain.com/'

        OR (for API based authentication)

        gitlab.user: admin
        gitlab.api: '432432432432432'
        gitlab.url: 'https://gitlab.domain.com'
'''

from __future__ import absolute_import

import logging
import os

LOG = logging.getLogger(__name__)

# Import third party libs
HAS_GITLAB = False
try:
    from gitlab import Gitlab
    HAS_GITLAB = True
except ImportError:
    pass

PER_PAGE = os.getenv("GITLAB_PER_PAGE", 1000)

def __virtual__():
    '''
    Only load this module if gitlab
    is installed on this minion.
    '''
    if HAS_GITLAB:
        return 'gitlab'
    return False

__opts__ = {}


def _get_project_by_id(git, id):
    selected_project = git.getproject(id)
    return selected_project


def _get_project(git, name):
    if str(name).isdigit():
        return _get_project_by_id(git, name)

    selected_project = None
    projects = git.getprojectsall(per_page=PER_PAGE)
    page = 1

    while not selected_project:
        for project in projects:
            if project.get('path_with_namespace') == name:
                selected_project = project
                break
        page += 1
        projects = git.getprojectsall(page=page, per_page=PER_PAGE)
        if len(projects) == 0: break
    return selected_project


def auth(**connection_args):
    '''
    Set up gitlab credentials

    Only intended to be used within Gitlab-enabled modules
    '''
   
    prefix = "gitlab."

    # look in connection_args first, then default to config file
    def get(key, default=None):
        return connection_args.get('connection_' + key,
            __salt__['config.get'](prefix + key, default))

    user = get('user', 'admin')
    password = get('password', 'ADMIN')
    token = get('token')
    url = get('url', 'https://localhost/')
    if token:
        git = Gitlab(url, token=token, verify_ssl=False)
    else:
        git = Gitlab(url)
        git.login(user, password, verify_ssl=False)
    return git


def hook_get(hook_url, project_id=None, project_name=None, **connection_args):
    '''
    Return a specific endpoint (gitlab endpoint-get)

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.endpoint_get nova
    '''
    git = auth(**connection_args)
    if project_name:
        project = _get_project(git, project_name)
    else:
        project = _get_project_by_id(git, project_id)
    if not project:
        return {'Error': 'Unable to resolve project'}
    for hook in git.getprojecthooks(project.get('id'), per_page=PER_PAGE):
        if hook.get('url') == hook_url:
            return {hook.get('url'): hook}
    return {'Error': 'Could not find hook for the specified project'}


def hook_list(project, **connection_args):
    '''
    Return a list of available hooks for project

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.hook_list 341
    '''
    git = auth(**connection_args)
    ret = {}

    project = _get_project(git, project)

    if not project:
        return {'Error': 'Unable to resolve project'}
    for hook in git.getprojecthooks(project.get('id')):
        ret[hook.get('url')] = hook
    return ret


def hook_create(hook_url, issues_events=False, merge_requests_events=False, \
    push_events=False, project_id=None, project_name=None, **connection_args):
    '''
    Create an hook for a project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.hook_create 'https://hook.url/' push_events=True project_id=300
    '''
    git = auth(**connection_args)
    if project_name:
        project = _get_project(git, project_name)
    else:
        project = _get_project_by_id(git, project_id)
    if not project:
        return {'Error': 'Unable to resolve project'}
    create = True
    for hook in git.getprojecthooks(project.get('id')):
        if hook.get('url') == hook_url:
            create = False
    if create:  
        git.addprojecthook(project['id'], hook_url)
    return hook_get(hook_url, project_id=project['id'])


def hook_delete(hook_url, project_id=None, project_name=None, **connection_args):
    '''
    Delete hook of a Gitlab project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.hook_delete 'https://hook.url/' project_id=300
    '''
    git = auth(**connection_args)
    if project_name:
        project = _get_project(git, project_name)
    else:
        project = _get_project_by_id(git, project_id)
    if not project:
        return {'Error': 'Unable to resolve project'}
    for hook in git.getprojecthooks(project.get('id')):
        if hook.get('url') == hook_url:
            return git.deleteprojecthook(project['id'], hook['id'])
    return {'Error': 'Could not find hook for the specified project'}


def deploykey_create(title, key, project, **kwargs):
    '''
    Add deploy key to Gitlab project

    :param project_id: project id
    :param title: title of the key
    :param key: the key itself
    :return: true if sucess, false if not

    Reclass definition
    -----

    .. code-block:: yaml

        repository:
          name-space/repo-name:
            deploy_key:
              keyname:
                enabled: true
                key: public_part_of_ssh_key

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.deploykey_create title keyfrsdfdsfds 43 --log-level=debug

    '''
    git = auth(**kwargs)

    project = _get_project(git, project)

    if not project:
        LOG.error("project not exists")
        return {'Error': 'Unable to resolve project'}

    try:
        result = git.adddeploykey(project['id'], title, key)
    except Exception, e:
        raise e

    LOG.debug("%s deploykey_create: %s" % (title, result))

    return 'Gitlab deploy key ID "{0}" was added to {1}'.format(title, project['path_with_namespace'])

def deploykey_delete(title, key, project, **kwargs):
    '''
    Delete a deploy key from Gitlab project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.deploykey_delete key.domain.com project_id=12
        salt '*' gitlab.deploykey_delete key.domain.com project=namespace/path
    '''
    git = auth(**kwargs)
    if project:
        project = _get_project(git, project)
    else:
        project = _get_project_by_id(git, project_id)
    if not project:
        return {'Error': 'Unable to resolve project'}
    for key in git.getdeploykeys(project.get('id')):
        if key.get('title') == title:
            git.deletedeploykey(project['id'], key['id'])
            return 'Gitlab deploy key ID "{0}" deleted'.format(key['id'])
    return {'Error': 'Could not find deploy key for the specified project'}


def deploykey_get(title, project, **kwargs):
    '''
    Return a specific deploy key

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.deploykey_get key.domain.com 12
        salt '*' gitlab.deploykey_get key.domain.com project_name=namespace/path
    '''
    git = auth(**kwargs)

    project = _get_project(git, project)

    if not project:
        return {'Error': 'Unable to resolve project'}
    for key in git.getdeploykeys(project.get('id')):
        if key.get('title') == title:
            return {key.get('title'): key}
    return {'Error': 'Could not find deploy key for the specified project'}


def deploykey_list(project_id=None, project_name=None, **connection_args):
    '''
    Return a list of available deploy keys for project

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.deploykey_list 341
    '''
    git = auth(**connection_args)
    ret = {}
    if project_name:
        project = _get_project(git, project_name)
    else:
        project = _get_project_by_id(git, project_id)
    if not project:
        return {'Error': 'Unable to resolve project'}
    for key in git.getdeploykeys(project.get('id')):
        ret[key.get('title')] = key
    return ret


def project_create(name, **kwargs):
    '''
    Create a gitlab project

    :param name: new project name
    :param path: custom repository name for new project. By default generated based on name
    :param namespace_id: namespace for the new project (defaults to user)
    :param description: short project description
    :param issues_enabled:
    :param merge_requests_enabled:
    :param wiki_enabled:
    :param snippets_enabled:
    :param public: if true same as setting visibility_level = 20
    :param visibility_level:
    :param import_url: https://git.tcpcloud.eu/django/django-kedb.git

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_create namespace/nova description='nova project'
        salt '*' gitlab.project_create namespace/test enabled=False
    
    '''
    ret = {}
    git = auth(**kwargs)

    project = _get_project(git, name)

    if project and not "Error" in project:
        LOG.debug("Project {0} exists".format(name))
        ret[project.get('path_with_namespace')] = project
        return ret

    group_name, name = name.split('/')
    group = group_get(name=group_name)[group_name]
    kwargs['namespace_id'] = group.get('id')
    kwargs['name'] = name
    LOG.debug(kwargs)

    new = git.createproject(**kwargs)
    if not new:
        return {'Error': 'Error creating project %s' % new}
    else:
        LOG.debug(new)
        ret[new.get('path_with_namespace')] = new
        return ret

def project_delete(project, **kwargs):
    '''
    Delete a project (gitlab project-delete)

    :params project: Name or ID

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_delete c965f79c4f864eaaa9c3b41904e67082
        salt '*' gitlab.project_delete project_id=c965f79c4f864eaaa9c3b41904e67082
        salt '*' gitlab.project_delete name=demo
    '''
    git = auth(**kwargs)

    project = _get_project(git, project)

    if not project:
        return {'Error': 'Unable to resolve project'}

    del_ret = git.deleteproject(project["id"])
    ret = 'Project ID {0} deleted'.format(project["path_with_namespace"])
    ret += ' ({0})'.format(project["path_with_namespace"])

    return ret


def project_get(project_id=None, name=None, **kwargs):
    '''
    Return a specific project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_get 323
        salt '*' gitlab.project_get project_id=323
        salt '*' gitlab.project_get name=namespace/repository
    '''
    git = auth(**kwargs)
    ret = {}
    #object_list = project_list(kwargs)

    project = _get_project(git, name or project_id)
    if not project:
        return {'Error': 'Error in retrieving project'}
    ret[project.get('name')] = project
    return ret


def project_list(**connection_args):
    '''
    Return a list of available projects

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.project_list
    '''
    git = auth(**connection_args)
    ret = {}

    projects = git.getprojectsall(per_page=PER_PAGE)
    page = 1

    while len(projects) > 0:
        for project in projects:
            ret[project.get('path_with_namespace')] = project
        page += 1
        projects = git.getprojectsall(page=page, per_page=PER_PAGE)
    return ret

def project_update(project_id=None, name=None, email=None,
                  enabled=None, default_branch=None, description=None, **connection_args):
    '''
    Update a project's information (gitlab project-update)
    The following fields may be updated: name, email, enabled.
    Can only update name if targeting by ID

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_update name=admin enabled=True
        salt '*' gitlab.project_update 123
    '''
    git = auth(**connection_args)
    if project_id:
        project = project_get(project_id)
    else:
        project = project_get(name)
    project = project_get(name=name)
    if not project.has_key('Error'):
      project = project[name.split("/")[1]]
    if description == None:
        description = project['description']
    if default_branch == None:
        default_branch = project['default_branch']
    git.editproject(project_id, default_branch=default_branch)


def group_list(group_name=None, **connection_args):
    '''
    Return a list of available groups

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.group_list
    '''
    git = auth(**connection_args)
    ret = {}
    for group in git.getgroups(group_id=None, page=1, per_page=100):
        ret[group.get('name')] = group
    return ret


def group_get(id=None, name=None, **connection_args):
    '''
    Return a specific group

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.group_get 323
        salt '*' gitlab.group_get name=namespace

    '''
    git = auth(**connection_args)
    ret = {}
    if id == None:
        for group in git.getgroups(group_id=None, page=1, per_page=100):
            if group.get('path') == name or group.get('name') == name:
                ret[group.get('path')] = group
    else:
        group = git.getgroups(id)
        if group != False:
            ret[group.get('path')] = group
    if len(ret) == 0:
        return {'Error': 'Error in retrieving group'}
    return ret

