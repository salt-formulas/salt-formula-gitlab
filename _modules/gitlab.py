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
        'visibility_level': group.visibility_level,
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
        'visibility_level': project.visibility_level,
        'public': project.public,
        'default_branch': project.default_branch,
    }


def _get_project(gitlab, path_with_namespace):

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
        if len(projects) == 0:
            break
    return selected_project


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
        git = Gitlab(url, token, ssl_verify=False)
    else:
        git = Gitlab(url, email=user, password=password, ssl_verify=False)
    git.auth()
    return git


def hook_get(path_with_namespace, hook_url, **kwargs):
    '''
    Return a specific hook for gitlab repository

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.endpoint_get nova
    '''
    git = auth(**kwargs)
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


def hook_list(project, **kwargs):
    '''
    Return a list of available hooks for project

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.hook_list 341
    '''
    git = auth(**kwargs)
    ret = {}

    project = _get_project(git, project)

    if not project:
        return {'Error': 'Unable to resolve project'}
    for hook in git.getprojecthooks(project.get('id')):
        ret[hook.get('url')] = hook
    return ret


def hook_create(hook_url, issues_events=False, merge_requests_events=False,
                push_events=False, project_id=None, project_name=None, **kwargs):
    '''
    Create an hook for a project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.hook_create 'https://hook.url/' push_events=True project_id=300
    '''
    git = auth(**kwargs)
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


def hook_delete(hook_url, project_id=None, project_name=None, **kwargs):
    '''
    Delete hook of a Gitlab project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.hook_delete 'https://hook.url/' project_id=300
    '''
    git = auth(**kwargs)
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


def deploykey_create(project, name, key, **kwargs):
    '''
    Add deploy key to Gitlab project

    :param project: Project namespace and path
    :param title: Human name of the key
    :param key: The key value itself
    :return: true if sucess, false if not

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.deploykey_create title keyfrsdfdsfds 43
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


def deploykey_delete(path_with_namespace, deploy_key, **kwargs):
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


def deploykey_list(project, **kwargs):
    '''
    Return a list of available deploy keys for project

    CLI Example:

    .. code-block:: bash

        salt '*' gitlab.deploykey_list 341
    '''
    gitlab = auth(**kwargs)
    ret = {}
    project = project_get(project, **kwargs)
    if not 'Error' in project:
        return {'Error': 'Unable to get the repository'}

    keys = gitlab.project_keys.list(project_id=project[project]['id'])
    print keys[0]

    for key in keys:
        ret[key.get('title')] = key
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
    :param visibility_level: Integer 1-20
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
        salt '*' gitlab.project_get id=323
    '''
    gitlab = auth(**kwargs)
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
    projects = gitlab.projects.all()
    for project in projects:
        ret[project.path_with_namespace] = _project_to_dict(project)
    return ret


def project_update(path_with_namespace=None, **kwargs):
    '''
    Update gitlab project

    CLI Examples:

    .. code-block:: bash

        salt '*' gitlab.project_update name-space/project-name
    '''
    git = auth(**kwargs)
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
