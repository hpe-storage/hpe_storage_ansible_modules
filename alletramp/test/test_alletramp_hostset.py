#    (c) Copyright 2026 Hewlett Packard Enterprise Development LP
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import mock
from modules import alletramp_hostset as hostset
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampHostset(unittest.TestCase):
    """
    Test suite for the alletramp_hostset Ansible module.
    
    Tests cover Host Set operations:
    - create
    - delete
    - add_hosts
    - remove_hosts
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_CREATE_HOSTSET = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'hostset_name': 'test_hostset',
        'domain': 'test_domain',
        'setmembers': ['host1', 'host2']
    }

    PARAMS_FOR_CREATE_HOSTSET_MINIMAL = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'hostset_name': 'test_hostset',
        'domain': None,
        'setmembers': None
    }

    PARAMS_FOR_DELETE_HOSTSET = {
        'operation': 'delete',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'hostset_name': 'test_hostset',
        'domain': None,
        'setmembers': None
    }

    PARAMS_FOR_ADD_HOSTS = {
        'operation': 'add_hosts',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'hostset_name': 'test_hostset',
        'domain': None,
        'setmembers': ['host3', 'host4']
    }

    PARAMS_FOR_REMOVE_HOSTS = {
        'operation': 'remove_hosts',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'hostset_name': 'test_hostset',
        'domain': None,
        'setmembers': ['host1', 'host2']
    }

    # Module argument specification
    fields = {
        'operation': {'required': True, 'choices': ['create', 'delete', 'add_hosts', 'remove_hosts'], 'type': 'str'},
        'storage_system_ip': {'required': True, 'type': 'str'},
        'storage_system_username': {'required': True, 'type': 'str', 'no_log': True},
        'storage_system_password': {'required': True, 'type': 'str', 'no_log': True},
        'hostset_name': {'required': True, 'type': 'str'},
        'domain': {'type': 'str'},
        'setmembers': {'type': 'list'}
    }

    # =========================================================================
    # Test: Module Arguments Specification
    # =========================================================================

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_module_args(self, mock_module, mock_client):
        """
        alletramp hostset - test module arguments specification
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (True, True, "Host set created successfully", {})
        
        hostset.main()
        
        mock_module.assert_called_with(argument_spec=self.fields)

    # =========================================================================
    # Test: Create Host Set Operations
    # =========================================================================

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_create_hostset_success_without_issue(self, mock_module, mock_client):
        """
        alletramp hostset - test create hostset success without issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (
            True, True, "Host set test_hostset created successfully", {}
        )

        hostset.main()

        mock_flowkit_client.create_hostset.assert_called_with(
            'test_hostset', domain='test_domain', setmembers=['host1', 'host2']
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Host set test_hostset created successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_create_hostset_success_with_issue(self, mock_module, mock_client):
        """
        alletramp hostset - test create hostset success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (
            True, True, "Host set test_hostset created successfully", 
            {"warning": "Some hosts have warnings"}
        )

        hostset.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Host set test_hostset created successfully", 
            issue={"warning": "Some hosts have warnings"}
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_create_hostset_already_exists(self, mock_module, mock_client):
        """
        alletramp hostset - test create hostset idempotency (hostset already exists)
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (
            True, False, "Host set test_hostset already exists", {}
        )

        hostset.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host set test_hostset already exists"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_create_hostset_failure(self, mock_module, mock_client):
        """
        alletramp hostset - test create hostset failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (
            False, False, "Host set creation failed | Invalid parameters", {}
        )

        hostset.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Host set creation failed | Invalid parameters"
        )

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_create_hostset_minimal_params(self, mock_module, mock_client):
        """
        alletramp hostset - test create hostset with minimal parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET_MINIMAL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (
            True, True, "Host set test_hostset created successfully", {}
        )

        hostset.main()

        mock_flowkit_client.create_hostset.assert_called_with(
            'test_hostset', domain=None, setmembers=None
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Host set test_hostset created successfully"
        )

    # =========================================================================
    # Test: Delete Host Set Operations
    # =========================================================================

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_delete_hostset_success(self, mock_module, mock_client):
        """
        alletramp hostset - test delete hostset success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_hostset.return_value = (
            True, True, "Host set test_hostset deleted successfully", {}
        )

        hostset.main()

        mock_flowkit_client.delete_hostset.assert_called_with('test_hostset')
        instance.exit_json.assert_called_with(
            changed=True, msg="Host set test_hostset deleted successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_delete_hostset_not_present(self, mock_module, mock_client):
        """
        alletramp hostset - test delete hostset idempotency (hostset does not exist)
        """
        mock_module.params = self.PARAMS_FOR_DELETE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_hostset.return_value = (
            True, False, "Host set test_hostset does not exist", {}
        )

        hostset.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host set test_hostset does not exist"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_delete_hostset_failure(self, mock_module, mock_client):
        """
        alletramp hostset - test delete hostset failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_hostset.return_value = (
            False, False, "Host set deletion failed | Host set in use", {}
        )

        hostset.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Host set deletion failed | Host set in use"
        )

    # =========================================================================
    # Test: Add Hosts to Host Set Operations
    # =========================================================================

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_add_hosts_success(self, mock_module, mock_client):
        """
        alletramp hostset - test add hosts to hostset success
        """
        mock_module.params = self.PARAMS_FOR_ADD_HOSTS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_hosts_to_hostset.return_value = (
            True, True, "Hosts added to host set test_hostset successfully", {}
        )

        hostset.main()

        mock_flowkit_client.add_hosts_to_hostset.assert_called_with(
            'test_hostset', ['host3', 'host4']
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Hosts added to host set test_hostset successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_add_hosts_already_present(self, mock_module, mock_client):
        """
        alletramp hostset - test add hosts when hosts already in hostset (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_ADD_HOSTS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_hosts_to_hostset.return_value = (
            True, False, "Hosts already present in host set", {}
        )

        hostset.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Hosts already present in host set"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_add_hosts_failure(self, mock_module, mock_client):
        """
        alletramp hostset - test add hosts to hostset failure
        """
        mock_module.params = self.PARAMS_FOR_ADD_HOSTS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_hosts_to_hostset.return_value = (
            False, False, "Add hosts failed | Host not found", {}
        )

        hostset.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Add hosts failed | Host not found"
        )

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_add_hosts_with_issue(self, mock_module, mock_client):
        """
        alletramp hostset - test add hosts with issue dict
        """
        mock_module.params = self.PARAMS_FOR_ADD_HOSTS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_hosts_to_hostset.return_value = (
            True, True, "Hosts added successfully", {"partial": "Some hosts skipped"}
        )

        hostset.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Hosts added successfully", issue={"partial": "Some hosts skipped"}
        )

    # =========================================================================
    # Test: Remove Hosts from Host Set Operations
    # =========================================================================

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_remove_hosts_success(self, mock_module, mock_client):
        """
        alletramp hostset - test remove hosts from hostset success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_HOSTS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_hosts_from_hostset.return_value = (
            True, True, "Hosts removed from host set test_hostset successfully", {}
        )

        hostset.main()

        mock_flowkit_client.remove_hosts_from_hostset.assert_called_with(
            'test_hostset', ['host1', 'host2']
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Hosts removed from host set test_hostset successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_remove_hosts_not_present(self, mock_module, mock_client):
        """
        alletramp hostset - test remove hosts when hosts not in hostset (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_HOSTS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_hosts_from_hostset.return_value = (
            True, False, "Hosts not present in host set", {}
        )

        hostset.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Hosts not present in host set"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_remove_hosts_failure(self, mock_module, mock_client):
        """
        alletramp hostset - test remove hosts from hostset failure
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_HOSTS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_hosts_from_hostset.return_value = (
            False, False, "Remove hosts failed | Host set not found", {}
        )

        hostset.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Remove hosts failed | Host set not found"
        )

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp hostset - test flowkit client is initialized with correct parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (
            True, True, "Host set created successfully", {}
        )

        hostset.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp hostset - test flowkit client logout is called after operation
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (
            True, True, "Host set created successfully", {}
        )

        hostset.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_hostset.AnsibleClient')
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_flowkit_client_logout_exception_suppressed(self, mock_module, mock_client):
        """
        alletramp hostset - test flowkit client logout exception is suppressed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_hostset.return_value = (
            True, True, "Host set created successfully", {}
        )
        mock_flowkit_client.logout.side_effect = Exception("Logout failed")

        # Should not raise exception
        hostset.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Host set created successfully"
        )

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_hostset.AnsibleClient', None)
    @mock.patch('modules.alletramp_hostset.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp hostset - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            hostset.main()

        instance.fail_json.assert_called_with(
            msg='Python hpe_storage_flowkit_py package is required.'
        )


if __name__ == '__main__':
    unittest.main()
