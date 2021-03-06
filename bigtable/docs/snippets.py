#!/usr/bin/env python

# Copyright 2018, Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Testable usage examples for Google Cloud Bigtable API wrapper

Each example function takes a ``client`` argument (which must be an instance
of :class:`google.cloud.bigtable.client.Client`) and uses it to perform a task
with the API.

To facilitate running the examples as system tests, each example is also passed
a ``to_delete`` list;  the function adds to the list any objects created which
need to be deleted during teardown.

.. note::
    This file is under progress and will be updated with more guidance from
    the team. Unit tests will be added with guidance from the team.

"""

import datetime
import pytest

from test_utils.system import unique_resource_id
from google.api_core.exceptions import NotFound
from google.cloud._helpers import UTC
from google.cloud.bigtable import Client
from google.cloud.bigtable import enums


INSTANCE_ID = "snippet-tests" + unique_resource_id("-")
CLUSTER_ID = "clus-1-" + unique_resource_id("-")
LOCATION_ID = "us-central1-f"
ALT_LOCATION_ID = "us-central1-a"
PRODUCTION = enums.Instance.Type.PRODUCTION
SERVER_NODES = 3
STORAGE_TYPE = enums.StorageType.SSD
LABEL_KEY = u"python-snippet"
LABEL_STAMP = (
    datetime.datetime.utcnow()
    .replace(microsecond=0, tzinfo=UTC)
    .strftime("%Y-%m-%dt%H-%M-%S")
)
LABELS = {LABEL_KEY: str(LABEL_STAMP)}
INSTANCES_TO_DELETE = []


class Config(object):
    """Run-time configuration to be modified at set-up.

    This is a mutable stand-in to allow test set-up to modify
    global state.
    """

    CLIENT = None
    INSTANCE = None


def setup_module():
    client = Config.CLIENT = Client(admin=True)
    Config.INSTANCE = client.instance(
        INSTANCE_ID, instance_type=PRODUCTION, labels=LABELS
    )
    cluster = Config.INSTANCE.cluster(
        CLUSTER_ID,
        location_id=LOCATION_ID,
        serve_nodes=SERVER_NODES,
        default_storage_type=STORAGE_TYPE,
    )
    operation = Config.INSTANCE.create(clusters=[cluster])
    # We want to make sure the operation completes.
    operation.result(timeout=100)
    INSTANCES_TO_DELETE.append(Config.INSTANCE)


def teardown_module():
    for instance in INSTANCES_TO_DELETE:
        try:
            instance.delete()
        except NotFound:
            pass


def test_bigtable_create_instance():
    # [START bigtable_create_prod_instance]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable import enums

    my_instance_id = "inst-my-" + unique_resource_id("-")
    my_cluster_id = "clus-my-" + unique_resource_id("-")
    location_id = "us-central1-f"
    serve_nodes = 3
    storage_type = enums.StorageType.SSD
    production = enums.Instance.Type.PRODUCTION
    labels = {"prod-label": "prod-label"}

    client = Client(admin=True)
    instance = client.instance(my_instance_id, instance_type=production, labels=labels)
    cluster = instance.cluster(
        my_cluster_id,
        location_id=location_id,
        serve_nodes=serve_nodes,
        default_storage_type=storage_type,
    )
    operation = instance.create(clusters=[cluster])

    # Make sure this instance gets deleted after the test case.
    INSTANCES_TO_DELETE.append(instance)

    # We want to make sure the operation completes.
    operation.result(timeout=100)
    # [END bigtable_create_prod_instance]

    assert instance.exists()
    instance.delete()


def test_bigtable_create_additional_cluster():
    # [START bigtable_create_cluster]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable import enums

    # Assuming that there is an existing instance with `INSTANCE_ID`
    # on the server already.
    # to create an instance see
    # 'https://cloud.google.com/bigtable/docs/creating-instance'

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)

    cluster_id = "clus-my-" + unique_resource_id("-")
    location_id = "us-central1-a"
    serve_nodes = 3
    storage_type = enums.StorageType.SSD

    cluster = instance.cluster(
        cluster_id,
        location_id=location_id,
        serve_nodes=serve_nodes,
        default_storage_type=storage_type,
    )
    operation = cluster.create()
    # We want to make sure the operation completes.
    operation.result(timeout=100)
    # [END bigtable_create_cluster]
    assert cluster.exists()

    cluster.delete()


def test_bigtable_create_app_profile():
    # [START bigtable_create_app_profile]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)

    app_profile_id = "app-prof-" + unique_resource_id("-")
    description = "routing policy-multy"
    routing_policy_type = enums.RoutingPolicyType.ANY

    app_profile = instance.app_profile(
        app_profile_id=app_profile_id,
        routing_policy_type=routing_policy_type,
        description=description,
        cluster_id=CLUSTER_ID,
    )

    app_profile = app_profile.create(ignore_warnings=True)
    # [END bigtable_create_app_profile]
    assert app_profile.exists()

    app_profile.delete(ignore_warnings=True)


def test_bigtable_list_instances():
    # [START bigtable_list_instances]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    (instances_list, failed_locations_list) = client.list_instances()
    # [END bigtable_list_instances]
    assert len(instances_list) > 0


def test_bigtable_list_clusters_on_instance():
    # [START bigtable_list_clusters_on_instance]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    (clusters_list, failed_locations_list) = instance.list_clusters()
    # [END bigtable_list_clusters_on_instance]
    assert len(clusters_list) > 0


def test_bigtable_list_clusters_in_project():
    # [START bigtable_list_clusters_in_project]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    (clusters_list, failed_locations_list) = client.list_clusters()
    # [END bigtable_list_clusters_in_project]
    assert len(clusters_list) > 0


def test_bigtable_list_app_profiles():
    app_profile = Config.INSTANCE.app_profile(
        app_profile_id="app-prof-" + unique_resource_id("-"),
        routing_policy_type=enums.RoutingPolicyType.ANY,
    )
    app_profile = app_profile.create(ignore_warnings=True)

    # [START bigtable_list_app_profiles]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)

    app_profiles_list = instance.list_app_profiles()
    # [END bigtable_list_app_profiles]
    assert len(app_profiles_list) > 0


def test_bigtable_instance_exists():
    # [START bigtable_check_instance_exists]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance_exists = instance.exists()
    # [END bigtable_check_instance_exists]
    assert instance_exists


def test_bigtable_cluster_exists():
    # [START bigtable_check_cluster_exists]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    cluster = instance.cluster(CLUSTER_ID)
    cluster_exists = cluster.exists()
    # [END bigtable_check_cluster_exists]
    assert cluster_exists


def test_bigtable_reload_instance():
    # [START bigtable_reload_instance]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance.reload()
    # [END bigtable_reload_instance]
    assert instance.type_ == PRODUCTION.value


def test_bigtable_reload_cluster():
    # [START bigtable_reload_cluster]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    cluster = instance.cluster(CLUSTER_ID)
    cluster.reload()
    # [END bigtable_reload_cluster]
    assert cluster.serve_nodes == SERVER_NODES


def test_bigtable_update_instance():
    # [START bigtable_update_instance]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    display_name = "My new instance"
    instance.display_name = display_name
    instance.update()
    # [END bigtable_update_instance]
    assert instance.display_name == display_name

    # Make sure this instance gets deleted after the test case.
    INSTANCES_TO_DELETE.append(instance)


def test_bigtable_update_cluster():
    # [START bigtable_update_cluster]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    cluster = instance.cluster(CLUSTER_ID)
    cluster.serve_nodes = 4
    cluster.update()
    # [END bigtable_update_cluster]
    assert cluster.serve_nodes == 4


def test_bigtable_create_table():
    # [START bigtable_create_table]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable import column_family

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    table = instance.table("table_my")
    # Define the GC policy to retain only the most recent 2 versions.
    max_versions_rule = column_family.MaxVersionsGCRule(2)
    table.create(column_families={"cf1": max_versions_rule})
    # [END bigtable_create_table]
    assert table.exists()


def test_bigtable_list_tables():
    # [START bigtable_list_tables]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    tables_list = instance.list_tables()
    # [END bigtable_list_tables]
    assert len(tables_list) > 0


def test_bigtable_delete_cluster():
    # [START bigtable_delete_cluster]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    cluster_id = "clus-my-" + unique_resource_id("-")
    # [END bigtable_delete_cluster]

    cluster = instance.cluster(
        cluster_id,
        location_id=ALT_LOCATION_ID,
        serve_nodes=SERVER_NODES,
        default_storage_type=STORAGE_TYPE,
    )
    operation = cluster.create()
    # We want to make sure the operation completes.
    operation.result(timeout=1000)

    # [START bigtable_delete_cluster]
    cluster_to_delete = instance.cluster(cluster_id)
    cluster_to_delete.delete()
    # [END bigtable_delete_cluster]
    assert not cluster_to_delete.exists()


def test_bigtable_delete_instance():
    from google.cloud.bigtable import Client

    client = Client(admin=True)

    instance = client.instance("inst-my-123", instance_type=PRODUCTION, labels=LABELS)
    cluster = instance.cluster(
        "clus-my-123",
        location_id=ALT_LOCATION_ID,
        serve_nodes=1,
        default_storage_type=STORAGE_TYPE,
    )
    operation = instance.create(clusters=[cluster])

    # Make sure this instance gets deleted after the test case.
    INSTANCES_TO_DELETE.append(instance)

    # We want to make sure the operation completes.
    operation.result(timeout=100)

    # [START bigtable_delete_instance]
    from google.cloud.bigtable import Client

    client = Client(admin=True)

    instance_id = "inst-my-123"
    instance_to_delete = client.instance(instance_id)
    instance_to_delete.delete()
    # [END bigtable_delete_instance]

    assert not instance_to_delete.exists()


def test_bigtable_test_iam_permissions():
    # [START bigtable_test_iam_permissions]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance.reload()
    permissions = ["bigtable.clusters.create", "bigtable.tables.create"]
    permissions_allowed = instance.test_iam_permissions(permissions)
    # [END bigtable_test_iam_permissions]

    assert permissions_allowed == permissions


def test_bigtable_set_iam_policy_then_get_iam_policy():
    service_account_email = Config.CLIENT._credentials.service_account_email

    # [START bigtable_set_iam_policy]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable.policy import Policy
    from google.cloud.bigtable.policy import BIGTABLE_ADMIN_ROLE

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance.reload()
    new_policy = Policy()
    new_policy[BIGTABLE_ADMIN_ROLE] = [Policy.service_account(service_account_email)]

    policy_latest = instance.set_iam_policy(new_policy)
    # [END bigtable_set_iam_policy]

    assert len(policy_latest.bigtable_admins) > 0

    # [START bigtable_get_iam_policy]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    policy = instance.get_iam_policy()
    # [END bigtable_get_iam_policy]

    assert len(policy.bigtable_admins) > 0


def test_bigtable_project_path():
    import re

    # [START bigtable_project_path]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    project_path = client.project_path
    # [END bigtable_project_path]

    _project_path = r"^projects/(?P<project_id>[_a-zA-Z0-9][-_.a-zA-Z0-9]*)$"
    _project_path_re = re.compile(_project_path)
    assert _project_path_re.match(project_path)


def test_bigtable_table_data_client():
    # [START bigtable_table_data_client]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    table_data_client = client.table_data_client
    # [END bigtable_table_data_client]
    assert "BigtableClient" in str(table_data_client)


def test_bigtable_table_admin_client():
    # [START bigtable_table_admin_client]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    table_admin_client = client.table_admin_client
    # [END bigtable_table_admin_client]
    assert "BigtableTableAdmin" in str(table_admin_client)


def test_bigtable_instance_admin_client():
    # [START bigtable_instance_admin_client]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance_admin_client = client.instance_admin_client
    # [END bigtable_instance_admin_client]
    assert "BigtableInstanceAdmin" in str(instance_admin_client)


def test_bigtable_admins_policy():
    service_account_email = Config.CLIENT._credentials.service_account_email

    # [START bigtable_admins_policy]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable.policy import Policy
    from google.cloud.bigtable.policy import BIGTABLE_ADMIN_ROLE

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance.reload()
    new_policy = Policy()
    new_policy[BIGTABLE_ADMIN_ROLE] = [Policy.service_account(service_account_email)]

    policy_latest = instance.set_iam_policy(new_policy)
    policy = policy_latest.bigtable_admins
    # [END bigtable_admins_policy]

    assert len(policy) > 0


def test_bigtable_readers_policy():
    service_account_email = Config.CLIENT._credentials.service_account_email

    # [START bigtable_readers_policy]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable.policy import Policy
    from google.cloud.bigtable.policy import BIGTABLE_READER_ROLE

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance.reload()
    new_policy = Policy()
    new_policy[BIGTABLE_READER_ROLE] = [Policy.service_account(service_account_email)]

    policy_latest = instance.set_iam_policy(new_policy)
    policy = policy_latest.bigtable_readers
    # [END bigtable_readers_policy]

    assert len(policy) > 0


def test_bigtable_users_policy():
    service_account_email = Config.CLIENT._credentials.service_account_email

    # [START bigtable_users_policy]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable.policy import Policy
    from google.cloud.bigtable.policy import BIGTABLE_USER_ROLE

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance.reload()
    new_policy = Policy()
    new_policy[BIGTABLE_USER_ROLE] = [Policy.service_account(service_account_email)]

    policy_latest = instance.set_iam_policy(new_policy)
    policy = policy_latest.bigtable_users
    # [END bigtable_users_policy]

    assert len(policy) > 0


def test_bigtable_viewers_policy():
    service_account_email = Config.CLIENT._credentials.service_account_email

    # [START bigtable_viewers_policy]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable.policy import Policy
    from google.cloud.bigtable.policy import BIGTABLE_VIEWER_ROLE

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance.reload()
    new_policy = Policy()
    new_policy[BIGTABLE_VIEWER_ROLE] = [Policy.service_account(service_account_email)]

    policy_latest = instance.set_iam_policy(new_policy)
    policy = policy_latest.bigtable_viewers
    # [END bigtable_viewers_policy]

    assert len(policy) > 0


def test_bigtable_instance_name():
    import re

    # [START bigtable_instance_name]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance_name = instance.name
    # [END bigtable_instance_name]

    _instance_name_re = re.compile(
        r"^projects/(?P<project>[^/]+)/"
        r"instances/(?P<instance_id>"
        r"[a-z][-a-z0-9]*)$"
    )
    assert _instance_name_re.match(instance_name)


def test_bigtable_cluster_name():
    import re

    # [START bigtable_cluster_name]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    cluster = instance.cluster(CLUSTER_ID)
    cluster_name = cluster.name
    # [END bigtable_cluster_name]

    _cluster_name_re = re.compile(
        r"^projects/(?P<project>[^/]+)/"
        r"instances/(?P<instance>[^/]+)/"
        r"clusters/(?P<cluster_id>"
        r"[_a-zA-Z0-9][-_.a-zA-Z0-9]*)$"
    )

    assert _cluster_name_re.match(cluster_name)


def test_bigtable_instance_from_pb():
    # [START bigtable_instance_from_pb]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable_admin_v2.types import instance_pb2

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)

    name = instance.name
    instance_pb = instance_pb2.Instance(
        name=name, display_name=INSTANCE_ID, type=PRODUCTION, labels=LABELS
    )

    instance2 = instance.from_pb(instance_pb, client)
    # [END bigtable_instance_from_pb]
    assert instance2.name == instance.name


def test_bigtable_cluster_from_pb():
    # [START bigtable_cluster_from_pb]
    from google.cloud.bigtable import Client
    from google.cloud.bigtable_admin_v2.types import instance_pb2

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    cluster = instance.cluster(CLUSTER_ID)

    name = cluster.name
    cluster_state = cluster.state
    cluster_pb = instance_pb2.Cluster(
        name=name,
        location=LOCATION_ID,
        state=cluster_state,
        serve_nodes=SERVER_NODES,
        default_storage_type=STORAGE_TYPE,
    )

    cluster2 = cluster.from_pb(cluster_pb, instance)
    # [END bigtable_cluster_from_pb]
    assert cluster2.name == cluster.name


def test_bigtable_instance_state():
    # [START bigtable_instance_state]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    instance_state = instance.state
    # [END bigtable_instance_state]
    assert not instance_state


def test_bigtable_cluster_state():
    # [START bigtable_cluster_state]
    from google.cloud.bigtable import Client

    client = Client(admin=True)
    instance = client.instance(INSTANCE_ID)
    cluster = instance.cluster(CLUSTER_ID)
    cluster_state = cluster.state
    # [END bigtable_cluster_state]

    assert not cluster_state


if __name__ == "__main__":
    pytest.main()
