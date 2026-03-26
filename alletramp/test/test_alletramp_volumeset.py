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
from modules import alletramp_volumeset as volumeset
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampVolumeset(unittest.TestCase):
    """
    Test suite for the alletramp_volumeset Ansible module.
    
    Tests cover Volume Set operations:
    - create
    - delete
    - add_volumes
    - remove_volumes
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_CREATE_VOLUMESET = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volumeset_name': 'test_volumeset',
        'volumeset_type': 'standard',
        'domain': 'test_domain',
        'setmembers': ['vol1', 'vol2']
    }

    PARAMS_FOR_CREATE_VOLUMESET_MINIMAL = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volumeset_name': 'test_volumeset',
        'volumeset_type': 'standard',
        'domain': None,
        'setmembers': None
    }

    PARAMS_FOR_DELETE_VOLUMESET = {
        'operation': 'delete',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volumeset_name': 'test_volumeset',
        'volumeset_type': None,
        'domain': None,
        'setmembers': None
    }

    PARAMS_FOR_ADD_VOLUMES = {
        'operation': 'add_volumes',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volumeset_name': 'test_volumeset',
        'volumeset_type': None,
        'domain': None,
        'setmembers': ['vol3', 'vol4']
    }

    PARAMS_FOR_REMOVE_VOLUMES = {
        'operation': 'remove_volumes',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volumeset_name': 'test_volumeset',
        'volumeset_type': None,
        'domain': None,
        'setmembers': ['vol1', 'vol2']
    }

    # Module argument specification
    fields = {
        "operation": {
            "required": True,
            "choices": ['create', 'delete', 'add_volumes', 'remove_volumes'],
            "type": 'str'
        },
        "storage_system_ip": {"required": True, "type": "str"},
        "storage_system_username": {"required": True, "type": "str", "no_log": True},
        "storage_system_password": {"required": True, "type": "str", "no_log": True},
        "volumeset_name": {"required": True, "type": "str"},
        "domain": {"type": "str"},
        "setmembers": {"type": "list"},
        "volumeset_type": {"required": False, "type": "str"}
    }

    # =========================================================================
    # Test: Module Arguments Specification
    # =========================================================================

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_module_args(self, mock_module, mock_client):
        """
        alletramp volumeset - test module arguments specification
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUMESET
        mock_module.return_value = mock_module
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volumeset.return_value = (True, True, "Volume set created successfully", {})
        
        volumeset.main()
        
        mock_module.assert_called()

    # =========================================================================
    # Test: Create Volume Set Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_create_volumeset_success_without_issue(self, mock_module, mock_client):
        """
        alletramp volumeset - test create volumeset success without issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUMESET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volumeset.return_value = (
            True, True, "Volume set test_volumeset created successfully", {}
        )

        volumeset.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Volume set test_volumeset created successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_create_volumeset_success_with_issue(self, mock_module, mock_client):
        """
        alletramp volumeset - test create volumeset success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUMESET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volumeset.return_value = (
            True, True, "Volume set created successfully", 
            {"warning": "Some volumes have warnings"}
        )

        volumeset.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Volume set created successfully", 
            issue={"warning": "Some volumes have warnings"}
        )

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_create_volumeset_already_exists(self, mock_module, mock_client):
        """
        alletramp volumeset - test create volumeset idempotency
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUMESET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volumeset.return_value = (
            True, False, "Volume set test_volumeset already exists", {}
        )

        volumeset.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Volume set test_volumeset already exists"
        )

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_create_volumeset_failure(self, mock_module, mock_client):
        """
        alletramp volumeset - test create volumeset failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUMESET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volumeset.return_value = (
            False, False, "Volume set creation failed | Invalid parameters", {}
        )

        volumeset.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Volume set creation failed | Invalid parameters"
        )

    # =========================================================================
    # Test: Delete Volume Set Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_delete_volumeset_success(self, mock_module, mock_client):
        """
        alletramp volumeset - test delete volumeset success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_VOLUMESET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_volumeset.return_value = (
            True, True, "Volume set test_volumeset deleted successfully", {}
        )

        volumeset.main()

        mock_flowkit_client.delete_volumeset.assert_called_with('test_volumeset')
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume set test_volumeset deleted successfully"
        )

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_delete_volumeset_not_present(self, mock_module, mock_client):
        """
        alletramp volumeset - test delete volumeset idempotency
        """
        mock_module.params = self.PARAMS_FOR_DELETE_VOLUMESET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_volumeset.return_value = (
            True, False, "Volume set does not exist", {}
        )

        volumeset.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Volume set does not exist"
        )

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_delete_volumeset_failure(self, mock_module, mock_client):
        """
        alletramp volumeset - test delete volumeset failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_VOLUMESET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_volumeset.return_value = (
            False, False, "Volume set deletion failed | In use", {}
        )

        volumeset.main()

        instance.fail_json.assert_called_with(
            msg="Volume set deletion failed | In use"
        )

    # =========================================================================
    # Test: Add Volumes to Volume Set Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_add_volumes_success(self, mock_module, mock_client):
        """
        alletramp volumeset - test add volumes success
        """
        mock_module.params = self.PARAMS_FOR_ADD_VOLUMES
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_volumes_to_volumeset.return_value = (
            True, True, "Volumes added successfully", {}
        )

        volumeset.main()

        mock_flowkit_client.add_volumes_to_volumeset.assert_called_with(
            'test_volumeset', ['vol3', 'vol4']
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volumes added successfully"
        )

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_add_volumes_already_present(self, mock_module, mock_client):
        """
        alletramp volumeset - test add volumes idempotency
        """
        mock_module.params = self.PARAMS_FOR_ADD_VOLUMES
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_volumes_to_volumeset.return_value = (
            True, False, "Volumes already present", {}
        )

        volumeset.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Volumes already present"
        )

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_add_volumes_failure(self, mock_module, mock_client):
        """
        alletramp volumeset - test add volumes failure
        """
        mock_module.params = self.PARAMS_FOR_ADD_VOLUMES
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_volumes_to_volumeset.return_value = (
            False, False, "Add volumes failed | Volume not found", {}
        )

        volumeset.main()

        instance.fail_json.assert_called_with(
            msg="Add volumes failed | Volume not found"
        )

    # =========================================================================
    # Test: Remove Volumes from Volume Set Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_remove_volumes_success(self, mock_module, mock_client):
        """
        alletramp volumeset - test remove volumes success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_VOLUMES
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_volumes_from_volumeset.return_value = (
            True, True, "Volumes removed successfully", {}
        )

        volumeset.main()

        mock_flowkit_client.remove_volumes_from_volumeset.assert_called_with(
            'test_volumeset', ['vol1', 'vol2']
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volumes removed successfully"
        )

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_remove_volumes_not_present(self, mock_module, mock_client):
        """
        alletramp volumeset - test remove volumes idempotency
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_VOLUMES
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_volumes_from_volumeset.return_value = (
            True, False, "Volumes not present in set", {}
        )

        volumeset.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Volumes not present in set"
        )

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_remove_volumes_failure(self, mock_module, mock_client):
        """
        alletramp volumeset - test remove volumes failure
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_VOLUMES
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_volumes_from_volumeset.return_value = (
            False, False, "Remove volumes failed", {}
        )

        volumeset.main()

        instance.fail_json.assert_called_with(msg="Remove volumes failed")

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp volumeset - test flowkit client initialization
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUMESET
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volumeset.return_value = (True, True, "Created", {})

        volumeset.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_volumeset.AnsibleClient')
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp volumeset - test flowkit client logout called
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUMESET
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volumeset.return_value = (True, True, "Created", {})

        volumeset.main()

        mock_flowkit_client.logout.assert_called_once()

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_volumeset.AnsibleClient', None)
    @mock.patch('modules.alletramp_volumeset.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp volumeset - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUMESET
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            volumeset.main()

        instance.fail_json.assert_called_with(
            msg='Python hpe_storage_flowkit_py package is required.'
        )


if __name__ == '__main__':
    unittest.main()
