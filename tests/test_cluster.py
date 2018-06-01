import os

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

import pytest

from mock import Mock, patch
from test_util import add_cluster_dir, env

from dcos import auth, cluster, config, constants, errors, util


def _cluster(cluster_id):
    c = cluster.Cluster(cluster_id)
    c.get_name = MagicMock(return_value="cluster-{}".format(cluster_id))
    c.get_url = MagicMock(return_value="https://cluster-{}".format(cluster_id))
    return c


def _linked_cluster(cluster_id):
    return cluster.LinkedCluster(
        cluster_url='https://example.org',
        cluster_id=cluster_id,
        cluster_name="It's me, Mario!",
        provider=auth.AUTH_TYPE_OIDC_AUTHORIZATION_CODE_FLOW,
    )


def _test_cluster_list():
    return [_cluster("a"), _cluster("b"), _cluster("c")]


@patch('dcos.cluster.get_clusters')
def test_get_cluster(get_clusters):
    clusters = [_cluster("its_me_mario"), _cluster("its_me_luigi")]
    get_clusters.return_value = clusters

    expected_msg = ('Multiple clusters matching "cluster-its_me", '
                    'please use the cluster ID.')
    with pytest.raises(errors.DCOSException, message=expected_msg):
        assert cluster.get_cluster("its_me")

    assert cluster.get_cluster("cluster-its_me_mario") == clusters[0]
    assert cluster.get_cluster("its_me_m") == clusters[0]
    assert cluster.get_cluster("its_me_mario") == clusters[0]

    assert cluster.get_cluster("cluster-its_me_luigi") == clusters[1]
    assert cluster.get_cluster("its_me_l") == clusters[1]
    assert cluster.get_cluster("its_me_luigi") == clusters[1]

    assert cluster.get_cluster("cluster-its_not_me") is None


def test_get_clusters():
    with env(), util.tempdir() as tempdir:
        os.environ[constants.DCOS_DIR_ENV] = tempdir

        # no config file of any type
        assert cluster.get_clusters() == []

        # cluster dir exists, no cluster
        clusters_dir = os.path.join(tempdir, constants.DCOS_CLUSTERS_SUBDIR)
        util.ensure_dir_exists(clusters_dir)
        assert cluster.get_clusters() == []

        # a valid cluster
        cluster_id = "a8b53513-63d4-4059-8b08-fde4fe1f1a83"
        add_cluster_dir(cluster_id, tempdir)

        # Make sure clusters dir can contain random files / folders
        # cf. https://jira.mesosphere.com/browse/DCOS_OSS-1782
        util.ensure_file_exists(os.path.join(clusters_dir, '.DS_Store'))
        util.ensure_dir_exists(os.path.join(clusters_dir, 'not_a_cluster'))

        assert cluster.get_clusters() == [_cluster(cluster_id)]


@patch('dcos.cluster.get_linked_clusters')
def test_get_clusters_with_configured_link(get_linked_clusters):
    with env(), util.tempdir() as tempdir:
        os.environ[constants.DCOS_DIR_ENV] = tempdir
        cluster_id = "a8b53513-63d4-4059-8b08-fde4fe1f1a83"
        add_cluster_dir(cluster_id, tempdir)
        get_linked_clusters.return_value = [_linked_cluster(cluster_id)]

        clusters = cluster.get_clusters(True)
        assert len(clusters) == 1
        assert type(clusters[0]) == cluster.Cluster


def test_set_attached():
    with env(), util.tempdir() as tempdir:
        os.environ[constants.DCOS_DIR_ENV] = tempdir

        cluster_path = add_cluster_dir("a", tempdir)
        # no attached_cluster
        assert cluster.set_attached(cluster_path) is None
        assert config.get_attached_cluster_path() == cluster_path

        cluster_path2 = add_cluster_dir("b", tempdir)
        # attach cluster already attached
        assert cluster.set_attached(cluster_path2) is None
        assert config.get_attached_cluster_path() == cluster_path2

        # attach cluster through environment
        os.environ[constants.DCOS_CLUSTER] = "a"
        assert config.get_attached_cluster_path() == cluster_path

        # attach back to old cluster through environment
        os.environ[constants.DCOS_CLUSTER] = "b"
        assert config.get_attached_cluster_path() == cluster_path2


@patch('dcos.http.get')
def test_setup_cluster_config(mock_get):
    with env(), util.tempdir() as tempdir:
        os.environ[constants.DCOS_DIR_ENV] = tempdir
        with cluster.setup_directory() as setup_temp:

            cluster.set_attached(setup_temp)

            cluster_id = "fake"
            mock_resp = Mock()
            mock_resp.json.return_value = {
                "CLUSTER_ID": cluster_id,
                "cluster": cluster_id
            }
            mock_get.return_value = mock_resp
            c = cluster.setup_cluster_config("fake_url", setup_temp, False)
            path = c.get_cluster_path()
            expected_path = os.path.join(
                tempdir, constants.DCOS_CLUSTERS_SUBDIR, cluster_id)
            assert path == expected_path
            assert os.path.exists(path)
            assert os.path.exists(os.path.join(path, "dcos.toml"))

        assert not os.path.exists(setup_temp)
