from mock import patch

import dcos.security.secrets as secrets


@patch('dcos.config')
def test_get_url(mock_config):
    store = 'store'
    path = 'foo/bar/qux'
    mock_config.get_config_val.return_value = "http://example.com"
    expected = "http://example.com/secrets/v1/secret/store/foo/bar/qux"
    assert secrets._get_url(path, store) == expected


@patch('dcos.config')
def test_get_url_path_leading_slash(mock_config):
    """A leading slash should still be a correct url."""
    store = 'store'
    path = '/foo/bar/qux'
    mock_config.get_config_val.return_value = "http://example.com"
    expected = "http://example.com/secrets/v1/secret/store/foo/bar/qux"
    assert secrets._get_url(path, store) == expected


@patch('dcos.config')
def test_get_url_path_empty_path(mock_config):
    """An empty path should return a proper url."""
    store = 'store'
    path = '/'
    mock_config.get_config_val.return_value = "http://example.com"
    expected = "http://example.com/secrets/v1/secret/store"
    assert secrets._get_url(path, store) == expected
