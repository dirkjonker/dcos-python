"""
Functions to manipulate secrets on a DC/OS enterprise cluster
"""

import dcos.config
import dcos.http


def create(path, value, store='default'):
    """Create a secret."""
    url = _get_url(path, store)
    return dcos.http.put(url, json={'value': value})


def delete(path, store='default'):
    """Delete a secret."""
    url = _get_url(path, store)
    return dcos.http.delete(url)


def get(path, store='default', default=None):
    """Get a secret from the store by its path.

    If the secret is not found, returns None or a default value
    """
    url = _get_url(path, store)
    try:
        return dcos.http.get(url).json().get('value')
    except dcos.http.DCOSHTTPException as e:
        if e.status() == 404:
            return default
        raise


def list(path='/', store='default'):
    """List secret keys in a given path."""
    url = _get_url(path, store)
    r = dcos.http.get(url, params={'list': 'true'})
    return r.json().get('array', [])


def update(path, value, store='default'):
    """Update a secret."""
    url = _get_url(path, store)
    return dcos.http.patch(url, json={'value': value})


def _get_url(path, store):
    """Get the URL for a secret."""
    base = dcos.config.get_config_val('core.dcos_url')
    api = 'secrets/v1/secret'
    return '/'.join([base, api, store, path.strip('/')]).strip('/')
