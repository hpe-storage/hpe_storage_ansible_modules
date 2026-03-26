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
from modules import alletramp_qos as qos
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampQos(unittest.TestCase):
    """
    Test suite for the alletramp_qos Ansible module.
    
    Tests cover QoS operations:
    - create_qos
    - modify_qos
    - delete_qos
    - get_qos
    - list_qos
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_CREATE_QOS = {
        'operation': 'create_qos',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'targetName': 'test_volumeset',
        'targetType': 'QOS_TGT_VVSET',
        'iopsMaxLimit': 50000,
        'bandwidthMaxLimitKiB': 512000,
        'enable': True,
        'allowAIQoS': False
    }

    PARAMS_FOR_CREATE_QOS_VOLUME = {
        'operation': 'create_qos',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'targetName': 'test_volume',
        'targetType': 'QOS_TGT_VV',
        'iopsMaxLimit': 10000,
        'bandwidthMaxLimitKiB': 102400,
        'enable': True,
        'allowAIQoS': None
    }

    PARAMS_FOR_CREATE_QOS_DOMAIN = {
        'operation': 'create_qos',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'targetName': 'test_domain',
        'targetType': 'QOS_TGT_DOMAIN',
        'iopsMaxLimit': 100000,
        'bandwidthMaxLimitKiB': 1024000,
        'enable': True,
        'allowAIQoS': True
    }

    PARAMS_FOR_CREATE_QOS_SYSTEM = {
        'operation': 'create_qos',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'targetName': 'system_qos',
        'targetType': 'QOS_TGT_SYSTEM',
        'iopsMaxLimit': 200000,
        'bandwidthMaxLimitKiB': 2048000,
        'enable': True,
        'allowAIQoS': None
    }

    PARAMS_FOR_MODIFY_QOS = {
        'operation': 'modify_qos',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'targetName': 'test_volumeset',
        'targetType': None,
        'iopsMaxLimit': 20000,
        'bandwidthMaxLimitKiB': 204800,
        'enable': True,
        'allowAIQoS': None
    }

    PARAMS_FOR_DELETE_QOS = {
        'operation': 'delete_qos',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'targetName': 'test_volumeset',
        'targetType': None,
        'iopsMaxLimit': None,
        'bandwidthMaxLimitKiB': None,
        'enable': None,
        'allowAIQoS': None
    }

    PARAMS_FOR_GET_QOS = {
        'operation': 'get_qos',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'targetName': 'test_volumeset',
        'targetType': None,
        'iopsMaxLimit': None,
        'bandwidthMaxLimitKiB': None,
        'enable': None,
        'allowAIQoS': None
    }

    PARAMS_FOR_LIST_QOS = {
        'operation': 'list_qos',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'targetName': None,
        'targetType': None,
        'iopsMaxLimit': None,
        'bandwidthMaxLimitKiB': None,
        'enable': None,
        'allowAIQoS': None
    }

    # =========================================================================
    # Test: Create QoS Operations
    # =========================================================================

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_create_qos_volumeset_success(self, mock_module, mock_client):
        """
        alletramp qos - test create qos for volumeset success
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (
            True, True, "QoS rule created successfully", {}
        )

        qos.main()

        mock_flowkit_client.create_qos.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="QoS rule created successfully"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_create_qos_volume_success(self, mock_module, mock_client):
        """
        alletramp qos - test create qos for volume success
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (
            True, True, "QoS rule for volume created successfully", {}
        )

        qos.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="QoS rule for volume created successfully"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_create_qos_domain_success(self, mock_module, mock_client):
        """
        alletramp qos - test create qos for domain success
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS_DOMAIN
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (
            True, True, "QoS rule for domain created successfully", {}
        )

        qos.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="QoS rule for domain created successfully"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_create_qos_system_success(self, mock_module, mock_client):
        """
        alletramp qos - test create qos for system success
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS_SYSTEM
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (
            True, True, "QoS rule for system created successfully", {}
        )

        qos.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="QoS rule for system created successfully"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_create_qos_success_with_issue(self, mock_module, mock_client):
        """
        alletramp qos - test create qos success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (
            True, True, "QoS rule created", 
            {"warning": "AI QoS is overriding"}
        )

        qos.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="QoS rule created", 
            issue={"warning": "AI QoS is overriding"}
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_create_qos_already_exists(self, mock_module, mock_client):
        """
        alletramp qos - test create qos idempotency
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (
            True, False, "QoS rule already exists", {}
        )

        qos.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="QoS rule already exists"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_create_qos_failure(self, mock_module, mock_client):
        """
        alletramp qos - test create qos failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (
            False, False, "QoS creation failed | Target not found", {}
        )

        qos.main()

        instance.fail_json.assert_called_with(
            msg="QoS creation failed | Target not found"
        )

    # =========================================================================
    # Test: Modify QoS Operations
    # =========================================================================

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_modify_qos_success(self, mock_module, mock_client):
        """
        alletramp qos - test modify qos success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_qos.return_value = (
            True, True, "QoS rule modified successfully", {}
        )

        qos.main()

        mock_flowkit_client.modify_qos.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="QoS rule modified successfully"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_modify_qos_no_change(self, mock_module, mock_client):
        """
        alletramp qos - test modify qos idempotency
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_qos.return_value = (
            True, False, "No changes required", {}
        )

        qos.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="No changes required"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_modify_qos_failure(self, mock_module, mock_client):
        """
        alletramp qos - test modify qos failure
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_qos.return_value = (
            False, False, "Modify QoS failed | QoS rule not found", {}
        )

        qos.main()

        instance.fail_json.assert_called_with(
            msg="Modify QoS failed | QoS rule not found"
        )

    # =========================================================================
    # Test: Delete QoS Operations
    # =========================================================================

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_delete_qos_success(self, mock_module, mock_client):
        """
        alletramp qos - test delete qos success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_qos.return_value = (
            True, True, "QoS rule deleted successfully", {}
        )

        qos.main()

        mock_flowkit_client.delete_qos.assert_called_with('test_volumeset')
        instance.exit_json.assert_called_with(
            changed=True, msg="QoS rule deleted successfully"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_delete_qos_not_present(self, mock_module, mock_client):
        """
        alletramp qos - test delete qos idempotency
        """
        mock_module.params = self.PARAMS_FOR_DELETE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_qos.return_value = (
            True, False, "QoS rule does not exist", {}
        )

        qos.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="QoS rule does not exist"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_delete_qos_failure(self, mock_module, mock_client):
        """
        alletramp qos - test delete qos failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_qos.return_value = (
            False, False, "Delete QoS failed", {}
        )

        qos.main()

        instance.fail_json.assert_called_with(msg="Delete QoS failed")

    # =========================================================================
    # Test: Get QoS Operations
    # =========================================================================

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_get_qos_success(self, mock_module, mock_client):
        """
        alletramp qos - test get qos success
        """
        mock_module.params = self.PARAMS_FOR_GET_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        qos_details = {
            "targetName": "test_volumeset",
            "targetType": "QOS_TGT_VVSET",
            "iopsMaxLimit": 50000,
            "bandwidthMaxLimitKiB": 512000,
            "enable": True
        }
        mock_flowkit_client.get_qos.return_value = (
            True, False, "QoS rule retrieved successfully", qos_details
        )

        qos.main()

        mock_flowkit_client.get_qos.assert_called_with('test_volumeset')
        instance.exit_json.assert_called_with(
            changed=False, 
            msg="QoS rule retrieved successfully",
            issue=qos_details
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_get_qos_not_found(self, mock_module, mock_client):
        """
        alletramp qos - test get qos not found
        """
        mock_module.params = self.PARAMS_FOR_GET_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_qos.return_value = (
            False, False, "QoS rule not found", {}
        )

        qos.main()

        instance.fail_json.assert_called_with(msg="QoS rule not found")

    # =========================================================================
    # Test: List QoS Operations
    # =========================================================================

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_list_qos_success(self, mock_module, mock_client):
        """
        alletramp qos - test list qos success
        """
        mock_module.params = self.PARAMS_FOR_LIST_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        qos_list = {
            "rules": [
                {"targetName": "vol1", "iopsMaxLimit": 10000},
                {"targetName": "vol2", "iopsMaxLimit": 20000}
            ]
        }
        mock_flowkit_client.list_qos.return_value = (
            True, False, "QoS rules listed successfully", qos_list
        )

        qos.main()

        mock_flowkit_client.list_qos.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=False, 
            msg="QoS rules listed successfully",
            issue=qos_list
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_list_qos_empty(self, mock_module, mock_client):
        """
        alletramp qos - test list qos empty
        """
        mock_module.params = self.PARAMS_FOR_LIST_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.list_qos.return_value = (
            True, False, "No QoS rules found", {}
        )

        qos.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="No QoS rules found"
        )

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_list_qos_failure(self, mock_module, mock_client):
        """
        alletramp qos - test list qos failure
        """
        mock_module.params = self.PARAMS_FOR_LIST_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.list_qos.return_value = (
            False, False, "Failed to list QoS rules", {}
        )

        qos.main()

        instance.fail_json.assert_called_with(msg="Failed to list QoS rules")

    # =========================================================================
    # Test: Exception Handling
    # =========================================================================

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_exception_handling(self, mock_module, mock_client):
        """
        alletramp qos - test exception handling
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.side_effect = Exception("Connection error")

        qos.main()

        instance.fail_json.assert_called()

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp qos - test flowkit client initialization
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (True, True, "Created", {})

        qos.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_qos.AnsibleClient')
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp qos - test flowkit client logout called
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_qos.return_value = (True, True, "Created", {})

        qos.main()

        mock_flowkit_client.logout.assert_called_once()

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_qos.AnsibleClient', None)
    @mock.patch('modules.alletramp_qos.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp qos - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_QOS
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            qos.main()

        instance.fail_json.assert_called_with(
            msg='Python hpe_storage_flowkit_py package is required.'
        )


if __name__ == '__main__':
    unittest.main()
