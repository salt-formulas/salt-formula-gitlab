# -*- coding: utf-8 -*-
'''
Module for handling Gitlab calls.

:optdepends:    - python-gitlab Python adapter
:configuration: This module is not usable until the following are specified
    either in a pillar or in the minion's config file::

        gitlab.user: admin
        gitlab.password: verybadpass
        gitlab.url: 'https://gitlab.domain.com/'

        or (for API token based authentication)

        gitlab.user: admin
        gitlab.token: '432432432432432'
        gitlab.url: 'https://gitlab.domain.com'
'''

from __future__ import absolute_import

import logging

LOG = logging.getLogger(__name__)

HAS_GITLAB = False
try:
    from gitlab import Gitlab
    HAS_GITLAB = True
except ImportError:
    pass


def __virtual__():
    '''
    Only load this module if gitlab lib is installed on this minion.
    '''
    if HAS_GITLAB:
        return 'gitlab'
    return False


def _group_to_dict(group):
    return {
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'path': group.path,
        'url': group.web_url,
        'lfs_enabled': group.lfs_enabled,
        'request_access_enabled': group.request_access_enabled,
    }


def _project_to_dict(project):
    return {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'path': project.path,
        'path_with_namespace': project.path_with_namespace,
        'url': project.web_url,
        'default_branch': project.default_branch,
    }


def auth(**kwargs):
    '''
    Set up gitlab authenticated client
    '''

    prefix = "gitlab."

    # look in kwargs first, then default to config file
    def get_key(key, default=None):
        return kwargs.get('connection_' + key,
                          __salt__['config.get'](prefix + key, default))

    user = get_key('user', 'admin')
    password = get_key('password', 'ADMIN')
    token = get_key('token')
    url = get_key('url', 'https://localhost/')
    LOG.info("Making HTTP request to {0} ...".format(url))
    if token:
        git = Gitlab(url, private_token=token)
    else:
        git = Gitlab(url, email=user, password=password)
    git.auth()
    return git


def deploykey_get(title, **kwargs):
    '''
    Return a specific deploy key

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.deploykey_get key.domain.com
    '''
    deploykeys = deploykey_list(**kwargs)
    if title in deploykeys:
        return {title: deploykeys[title]}
    return {'Error': 'Could not find deploy key for the specified project'}


def deploykey_list(**kwargs):
    '''
    Return a list of available deploy keys

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.deploykey_list
    '''
    ret = {}
    gitlab = auth(**kwargs)
    keys = gitlab.deploykeys.list()

    for key in keys:
        ret[key.title] = {
            'title': key.title,
            'key': key.key,
            'id': key.id,
        }
    return ret


def project_key_create(path_with_namespace, title, key, **kwargs):
    '''
    Create deploy key

    :param path_with_namespace: Name of project
    :param key: Value of the key
    :param key: Value of the key

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.deploykey_create key-title 'ssh-key ...'
    '''
    gitlab = auth(**kwargs)
    project = gitlab.projects.get(path_with_namespace)
    new_key = project.keys.create({'title': title,
                                   'key': key})
    if new_key:
        return {title: 'Deploy key "{0}" was created'.format(title)}
    return {'Error': 'Could not create deploy key "{}"'.format(title)}


def project_key_enable(path_with_namespace, title, **kwargs):
    '''
    Add deploy key to Gitlab project

    :param path_with_namespace: Project namespace with path
    :param title: Name of the key

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_key_enable ns/repo key-title
    '''
    gitlab = auth(**kwargs)
    project = gitlab.projects.get(path_with_namespace)
    keys = gitlab.deploykeys.list()
    key_id=None
    for key in keys:
        if key.title == title:
            key_id = key.id
    if key_id is not None:
        project.keys.enable(key_id)
        return {title: 'Deploy key "{0}" was added to {1}'.format(title, path_with_namespace)}
    return {'Error': 'Could not find deploy key "{}"'.format(title)}


def project_key_disable(path_with_namespace, title, **kwargs):
    '''
    Delete a deploy key from Gitlab project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_key_disable ns/repo key.domain.com
    '''
    gitlab = auth(**kwargs)
    project = gitlab.projects.get(path_with_namespace)
    keys = gitlab.deploykeys.list()
    key_id = None
    for key in keys:
        if key.title == title:
            key_id = key.id
    if key_id is not None:
        project.keys.disable(key_id)
    return {'Error': 'Could not find deploy key "{}" for the specified project'.format(title)}


def project_key_get(path_with_namespace, title, **kwargs):
    '''
    Return a specific deploy key

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_key_get ns/repo key.domain.com
    '''
    deploykeys = project_key_list(path_with_namespace, **kwargs)
    if title in deploykeys:
        return {title: deploykeys[title]}
    return {'Error': 'Could not find deploy key for the specified project'}


def project_key_list(path_with_namespace, **kwargs):
    '''
    Return a list of available deploy keys for project

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.project_key_list group/repo-name
    '''
    ret = {}
    gitlab = auth(**kwargs)
    project = gitlab.projects.get(path_with_namespace)
    keys = project.keys.list()

    for key in keys:
        ret[key.title] = {
            'title': key.title,
            'key': key.key,
            'id': key.id,
        }
    return ret


def project_create(path_with_namespace, description="", default_branch="master", **kwargs):
    '''
    Create a gitlab project

    :param path_with_namespace: new project name
    :param description: short project description
    :param issues_enabled:
    :param merge_requests_enabled:
    :param wiki_enabled:
    :param snippets_enabled:
    :param public: if true same as setting visibility_level = 20
    :param import_url: https://git.tcpcloud.eu/django/django-kedb.git

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_create namespace/nova description='nova project'
        salt '*' gitlab.project_create namespace/test enabled=False    
    '''
    gitlab = auth(**kwargs)
    ret = {}
    group_name, project_name = path_with_namespace.split('/')
    projects = project_list(**kwargs)
    if path_with_namespace in projects:
        LOG.info("Project {0} already exists".format(path_with_namespace))
        ret[path_with_namespace] = projects[path_with_namespace]
        return ret
    namespace = group_get(group_name)
    if "Error" in namespace:
        LOG.info("Group {0} does not exists".format(group_name))
        return ret
    else:
        group = namespace[group_name]

    new_project_data = {
        'name': project_name,
        'namespace_id': group['id'],
        'description': description,
        'default_branch': default_branch
    }

    if 'import_url' in kwargs:
        new_project_data['import_url'] = kwargs['import_url']

    new_project = gitlab.projects.create(new_project_data)
    if not new_project:
        return {'Error': 'Error creating project %s' % path_with_namespace}
    else:
        return project_get(path_with_namespace)


def project_delete(path_with_namespace, **kwargs):
    '''
    Delete a project (gitlab project-delete)

    :params path_with_namespace: Path with namespace of the repository

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_delete namespace/demo
    '''
    gitlab = auth(**kwargs)
    ret = {}
    projects = project_list(**kwargs)
    if not path_with_namespace in projects:
        LOG.info("Project {0} does not exist".format(path_with_namespace))
        return ret
    else:
        gitlab.projects.delete(projects[path_with_namespace]["id"])
        ret = 'Project {0} deleted'.format(path_with_namespace)
        return ret


def project_get(path_with_namespace, **kwargs):
    '''
    Return specific project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_get namespace/repository
    '''
    ret = {}
    projects = project_list(**kwargs)
    if path_with_namespace in projects:
        ret[path_with_namespace] = projects.get(path_with_namespace)
    if len(ret) == 0:
        return {'Error': 'Error in retrieving project'}
    return ret


def project_list(**kwargs):
    '''
    Return a list of all projects

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.project_list
    '''
    gitlab = auth(**kwargs)
    ret = {}
    projects = gitlab.projects.list()
    for project in projects:
        ret[project.path_with_namespace] = _project_to_dict(project)
    return ret


def project_update(path_with_namespace=None, description=None, default_branch=None, **kwargs):
    '''
    Update gitlab project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_update name-space/project-name
    '''
    gitlab = auth(**kwargs)
    project = project_get(path_with_namespace, **kwargs)
    if not project.has_key('Error'):
        project = project[path_with_namespace.split("/")[1]]
    if description == None:
        description = project['description']
    if default_branch == None:
        default_branch = project['default_branch']
    gitlab.editproject(project[path_with_namespace]['id'], default_branch=default_branch)


def group_list(**kwargs):
    '''
    Return a list of available groups

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.group_list
    '''
    gitlab = auth(**kwargs)
    ret = {}
    groups = gitlab.groups.list(all=True)
    for group in groups:
        ret[group.name] = _group_to_dict(group)
    return ret


def group_get(name, **kwargs):
    '''
    Return a specific group

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.group_get groupname
    '''
    gitlab = auth(**kwargs)
    ret = {}
    groups = group_list(**kwargs)
    if name in groups:
        ret[name] = groups.get(name)
    if len(ret) == 0:
        return {'Error': 'Error in retrieving group'}
    return ret


def group_create(name, path=None, description="", visibility_level=20, **kwargs):
    '''
    Create a new group

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.group_create group_name

    '''
    if path == None:
        path = name
    groups = group_list(**kwargs)
    gitlab = auth(**kwargs)
    namespace = None
    if name in groups:
        try:
            namespace = groups.get(name)
        except:
            pass
    if namespace == None:
        group_data = {
            'name': name,
            'path': path,
            'description': description,
            'visibility_level': visibility_level
        }
        gitlab.groups.create(group_data)
        return group_get(name)
    else:
        return {'Error': 'Group %s already exists' % name}


def group_delete(name, **kwargs):
    '''
    Delete a Group

    :params name: Name of the group

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.group_delete groupname
    '''
    gitlab = auth(**kwargs)
    ret = {}
    groups = group_list(**kwargs)
    if not name in groups:
        LOG.info("Group {0} does not exist".format(name))
        return ret
    else:
        gitlab.groups.delete(groups[name]['id'])
        ret = 'Group {0} deleted'.format(name)
        return ret
