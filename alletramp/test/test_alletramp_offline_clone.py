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
from modules import alletramp_offline_clone as offline_clone
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampOfflineClone(unittest.TestCase):
    """
    Test suite for the alletramp_offline_clone Ansible module.
    
    Tests cover Offline Clone operations:
    - create
    - delete
    - resync
    - stop
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_CREATE_CLONE = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'clone_name': 'test_clone',
        'base_volume_name': 'test_volume',
        'dest_cpg': 'test_cpg',
        'priority': 'PRIORITYTYPE_MED',
        'skip_zero': True,
        'expiration_time': 24,
        'expiration_unit': 'hours',
        'retention_time': 48,
        'retention_unit': 'hours',
        'addToSet': None,
        'appSetBusinessUnit': None,
        'appSetComments': None,
        'appSetExcludeAIQoS': None,
        'appSetImportance': None,
        'appSetType': None,
        'bulkvv': None,
        'enableResync': None,
        'reduce': None,
        'selectionType': None
    }

    PARAMS_FOR_CREATE_CLONE_MINIMAL = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'clone_name': 'test_clone',
        'base_volume_name': 'test_volume',
        'dest_cpg': 'test_cpg',
        'priority': 'PRIORITYTYPE_MED',
        'skip_zero': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'addToSet': None,
        'appSetBusinessUnit': None,
        'appSetComments': None,
        'appSetExcludeAIQoS': None,
        'appSetImportance': None,
        'appSetType': None,
        'bulkvv': None,
        'enableResync': None,
        'reduce': None,
        'selectionType': None
    }

    PARAMS_FOR_CREATE_CLONE_WITH_APPSET = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'clone_name': 'test_clone',
        'base_volume_name': 'test_volume',
        'dest_cpg': 'test_cpg',
        'priority': 'PRIORITYTYPE_HIGH',
        'skip_zero': False,
        'expiration_time': 168,
        'expiration_unit': 'hours',
        'retention_time': 336,
        'retention_unit': 'hours',
        'addToSet': 'clone_volumeset',
        'appSetBusinessUnit': 'IT',
        'appSetComments': 'Test clone set',
        'appSetExcludeAIQoS': 'no',
        'appSetImportance': 'HIGH',
        'appSetType': 'Clone',
        'bulkvv': False,
        'enableResync': True,
        'reduce': True,
        'selectionType': 'PARENTVV_INDEX'
    }

    PARAMS_FOR_DELETE_CLONE = {
        'operation': 'delete',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'clone_name': 'test_clone',
        'base_volume_name': 'test_volume',
        'dest_cpg': None,
        'priority': 'PRIORITYTYPE_MED',
        'skip_zero': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'addToSet': None,
        'appSetBusinessUnit': None,
        'appSetComments': None,
        'appSetExcludeAIQoS': None,
        'appSetImportance': None,
        'appSetType': None,
        'bulkvv': None,
        'enableResync': None,
        'reduce': None,
        'selectionType': None
    }

    PARAMS_FOR_RESYNC_CLONE = {
        'operation': 'resync',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'clone_name': 'test_clone',
        'base_volume_name': 'test_volume',
        'dest_cpg': None,
        'priority': 'PRIORITYTYPE_MED',
        'skip_zero': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'addToSet': None,
        'appSetBusinessUnit': None,
        'appSetComments': None,
        'appSetExcludeAIQoS': None,
        'appSetImportance': None,
        'appSetType': None,
        'bulkvv': None,
        'enableResync': None,
        'reduce': None,
        'selectionType': None
    }

    PARAMS_FOR_STOP_CLONE = {
        'operation': 'stop',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'clone_name': 'test_clone',
        'base_volume_name': 'test_volume',
        'dest_cpg': None,
        'priority': 'PRIORITYTYPE_MED',
        'skip_zero': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'addToSet': None,
        'appSetBusinessUnit': None,
        'appSetComments': None,
        'appSetExcludeAIQoS': None,
        'appSetImportance': None,
        'appSetType': None,
        'bulkvv': None,
        'enableResync': None,
        'reduce': None,
        'selectionType': None
    }

    # =========================================================================
    # Test: Create Clone Operations
    # =========================================================================

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_create_clone_success(self, mock_module, mock_client):
        """
        alletramp offline clone - test create clone success
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.copy_volume.return_value = (
            True, True, "Clone test_clone created successfully", {}
        )

        offline_clone.main()

        mock_flowkit_client.copy_volume.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Clone test_clone created successfully"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_create_clone_success_with_issue(self, mock_module, mock_client):
        """
        alletramp offline clone - test create clone success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.copy_volume.return_value = (
            True, True, "Clone created", 
            {"warning": "Clone created with warnings"}
        )

        with self.assertRaises(SystemExit):
            offline_clone.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Clone created", 
            issue={"warning": "Clone created with warnings"}
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_create_clone_minimal_params(self, mock_module, mock_client):
        """
        alletramp offline clone - test create clone with minimal parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CLONE_MINIMAL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.copy_volume.return_value = (
            True, True, "Clone created", {}
        )

        offline_clone.main()

        instance.exit_json.assert_called_with(changed=True, msg="Clone created")

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_create_clone_with_appset_params(self, mock_module, mock_client):
        """
        alletramp offline clone - test create clone with appset parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CLONE_WITH_APPSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.copy_volume.return_value = (
            True, True, "Clone created with appset", {}
        )

        offline_clone.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Clone created with appset"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_create_clone_failure(self, mock_module, mock_client):
        """
        alletramp offline clone - test create clone failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.copy_volume.return_value = (
            False, False, "Clone creation failed | Source volume not found", {}
        )

        offline_clone.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Clone creation failed | Source volume not found"
        )

    # =========================================================================
    # Test: Delete Clone Operations
    # =========================================================================

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_delete_clone_success(self, mock_module, mock_client):
        """
        alletramp offline clone - test delete clone success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = True
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.delete_volume.return_value = (
            True, True, "Clone deleted successfully", {}
        )

        offline_clone.main()

        mock_flowkit_client.delete_volume.assert_called_with('test_clone')
        instance.exit_json.assert_called_with(
            changed=True, msg="Clone deleted successfully"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_delete_clone_busy(self, mock_module, mock_client):
        """
        alletramp offline clone - test delete clone when clone is busy
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = True
        mock_flowkit_client.online_phy_copy_exist.return_value = True
        mock_flowkit_client.offline_phy_copy_exist.return_value = False

        with self.assertRaises(SystemExit):
            offline_clone.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Clone/Volume is busy. Cannot be deleted"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_delete_clone_offline_copy_in_progress(self, mock_module, mock_client):
        """
        alletramp offline clone - test delete clone when offline copy in progress
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = True
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.offline_phy_copy_exist.return_value = True

        with self.assertRaises(SystemExit):
            offline_clone.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Clone/Volume is busy. Cannot be deleted"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_delete_clone_not_exists(self, mock_module, mock_client):
        """
        alletramp offline clone - test delete clone when clone does not exist
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = False
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.offline_phy_copy_exist.return_value = False

        with self.assertRaises(SystemExit):
            offline_clone.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Clone/Volume is busy. Cannot be deleted"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_delete_clone_failure(self, mock_module, mock_client):
        """
        alletramp offline clone - test delete clone failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = True
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.delete_volume.return_value = (
            False, False, "Delete failed", {}
        )

        offline_clone.main()

        instance.fail_json.assert_called_with(changed=False, msg="Delete failed")

    # =========================================================================
    # Test: Resync Clone Operations
    # =========================================================================

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_resync_clone_success(self, mock_module, mock_client):
        """
        alletramp offline clone - test resync clone success
        """
        mock_module.params = self.PARAMS_FOR_RESYNC_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.resync_physical_copy.return_value = (
            True, True, "Clone resync initiated successfully", {}
        )

        offline_clone.main()

        mock_flowkit_client.resync_physical_copy.assert_called_with('test_clone')
        instance.exit_json.assert_called_with(
            changed=True, msg="Clone resync initiated successfully"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_resync_clone_failure(self, mock_module, mock_client):
        """
        alletramp offline clone - test resync clone failure
        """
        mock_module.params = self.PARAMS_FOR_RESYNC_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.resync_physical_copy.return_value = (
            False, False, "Resync failed | Clone not found", {}
        )

        offline_clone.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Resync failed | Clone not found"
        )

    # =========================================================================
    # Test: Stop Clone Operations
    # =========================================================================

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_stop_clone_success(self, mock_module, mock_client):
        """
        alletramp offline clone - test stop clone success
        """
        mock_module.params = self.PARAMS_FOR_STOP_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = True
        mock_flowkit_client.offline_phy_copy_exist.return_value = True
        mock_flowkit_client.stop_physical_copy.return_value = (
            True, True, "Clone stop initiated successfully", {}
        )

        offline_clone.main()

        mock_flowkit_client.stop_physical_copy.assert_called_with('test_clone')
        instance.exit_json.assert_called_with(
            changed=True, msg="Clone stop initiated successfully"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_stop_clone_not_in_progress(self, mock_module, mock_client):
        """
        alletramp offline clone - test stop clone when not in progress
        """
        mock_module.params = self.PARAMS_FOR_STOP_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = True
        mock_flowkit_client.offline_phy_copy_exist.return_value = False

        with self.assertRaises(SystemExit):
            offline_clone.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Offline Cloning not in progress"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_stop_clone_volume_not_exists(self, mock_module, mock_client):
        """
        alletramp offline clone - test stop clone when volume does not exist
        """
        mock_module.params = self.PARAMS_FOR_STOP_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = False
        mock_flowkit_client.offline_phy_copy_exist.return_value = False

        with self.assertRaises(SystemExit):
            offline_clone.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Offline Cloning not in progress"
        )

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_stop_clone_failure(self, mock_module, mock_client):
        """
        alletramp offline clone - test stop clone failure
        """
        mock_module.params = self.PARAMS_FOR_STOP_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.is_volume_exists.return_value = True
        mock_flowkit_client.offline_phy_copy_exist.return_value = True
        mock_flowkit_client.stop_physical_copy.return_value = (
            False, False, "Stop failed", {}
        )

        offline_clone.main()

        instance.fail_json.assert_called_with(changed=False, msg="Stop failed")

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp offline clone - test flowkit client initialization
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CLONE
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.copy_volume.return_value = (True, True, "Created", {})

        offline_clone.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient')
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp offline clone - test flowkit client logout called
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CLONE
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.offline_phy_copy_exist.return_value = False
        mock_flowkit_client.online_phy_copy_exist.return_value = False
        mock_flowkit_client.copy_volume.return_value = (True, True, "Created", {})

        offline_clone.main()

        mock_flowkit_client.logout.assert_called_once()

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_offline_clone.AnsibleClient', None)
    @mock.patch('modules.alletramp_offline_clone.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp offline clone - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CLONE
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            offline_clone.main()

        instance.fail_json.assert_called_with(
            msg='Python hpe_storage_flowkit_py package is required.'
        )


if __name__ == '__main__':
    unittest.main()
