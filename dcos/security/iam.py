"""
Functions to manipulate IAM on a DC/OS enterprise cluster

Lightweight wrapper around the web API.

For reference: https://docs.mesosphere.com/1.10/security/ent/iam-api/#/
"""

import dcos.config
import dcos.http
from dcos.errors import DCOSException


# Users
def check_user_args(**kwargs):
    required = ('password', 'public_key', 'secret')
    if not any(arg in kwargs for arg in required):
        raise DCOSException(
                "One of these arguments must be supplied for a new user: "
                "password, public_key, or secret")
    return kwargs


def create_user(uid, **kwargs):
    return put('users', uid, json=check_user_args(**kwargs))


def list_users():
    return get('users')


def get_user(uid):
    return get('users', uid)


def get_user_groups(uid):
    return get('users', uid, 'groups')


def list_user_permissions(uid):
    return get('users', uid, 'permissions')


def get_user_permission(uid, rid, action):
    return get('acls', rid, 'users', uid, action)


def grant_permission_to_user(uid, rid, action):
    return put('acls', rid, 'users', uid, action)


def revoke_permission_from_user(uid, rid, action):
    return delete('acls', rid, 'users', uid, action)


def update_user(uid, **kwargs):
    return patch('users', uid, json=check_user_args(**kwargs))


def delete_user(uid):
    return delete('users', uid)


# Groups
def create_group(gid, description):
    return put('groups', gid, json={'description': description})


def list_groups():
    return get('groups')


def get_group(gid):
    return get('groups', gid)


def get_group_users(gid):
    return get('groups', gid, 'users')


def list_group_permissions(gid):
    return get('groups', gid, 'permissions')


def get_group_permission(gid, rid, action):
    return get('acls', rid, 'groups', gid, action)


def grant_permission_to_group(gid, rid, action):
    return put('acls', rid, 'groups', gid, action)


def revoke_permission_from_group(gid, rid, action):
    return delete('acls', rid, 'groups', gid, action)


def update_group(gid, description):
    return patch('groups', gid, json={'description': description})


def delete_group(gid):
    return delete('groups', gid)


# Resources
def list_resources():
    return get('acls')


def get_resource(rid):
    return get('acls', rid)


def get_resource_permissions(rid):
    return get('acls', rid, 'permissions')


def create_resource(rid, description):
    return put('acls', rid, json={'description': description})


# web API utility functions
def create_url(*args):
    """Get a URL for the IAM API."""
    base = dcos.config.get_config_val('core.dcos_url') + '/acs/api/v1'
    path = '/'.join(args)
    return '{}/{}'.format(base, path).strip('/')


def get(*args):
    r = dcos.http.get(create_url(*args)).json()
    if list(r.keys()) == ['array']:
        return r['array']
    return r


def patch(*args, **kwargs):
    return dcos.http.patch(create_url(*args), **kwargs)


def put(*args, **kwargs):
    return dcos.http.put(create_url(*args), **kwargs)


def delete(*args):
    return dcos.http.delete(create_url(*args))
