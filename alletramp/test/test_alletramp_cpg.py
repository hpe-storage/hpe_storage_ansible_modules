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
from modules import alletramp_cpg as cpg
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampCpg(unittest.TestCase):
    """
    Test suite for the alletramp_cpg Ansible module.
    
    Tests cover CPG operations:
    - create
    - delete
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_CREATE_CPG = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'cpg_name': 'test_cpg',
        'domain': 'test_domain',
        'growth_increment': 32.0,
        'growth_increment_unit': 'GiB',
        'growth_limit': 1024.0,
        'growth_limit_unit': 'GiB',
        'growth_warning': 512.0,
        'growth_warning_unit': 'GiB',
        'high_availability': 'HAJBOD_DISK',
        'cage': None,
        'position': None,
        'keyValuePairs': None
    }

    PARAMS_FOR_CREATE_CPG_MINIMAL = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'cpg_name': 'test_cpg',
        'domain': None,
        'growth_increment': -1.0,
        'growth_increment_unit': 'GiB',
        'growth_limit': -1.0,
        'growth_limit_unit': 'GiB',
        'growth_warning': -1.0,
        'growth_warning_unit': 'GiB',
        'high_availability': None,
        'cage': None,
        'position': None,
        'keyValuePairs': None
    }

    PARAMS_FOR_DELETE_CPG = {
        'operation': 'delete',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'cpg_name': 'test_cpg',
        'domain': None,
        'growth_increment': -1.0,
        'growth_increment_unit': 'GiB',
        'growth_limit': -1.0,
        'growth_limit_unit': 'GiB',
        'growth_warning': -1.0,
        'growth_warning_unit': 'GiB',
        'high_availability': None,
        'cage': None,
        'position': None,
        'keyValuePairs': None
    }

    # Module argument specification
    fields = {
        "operation": {
            "required": True,
            "choices": ['create', 'delete'],
            "type": 'str'
        },
        "storage_system_ip": {
            "required": True,
            "type": "str"
        },
        "storage_system_username": {
            "required": True,
            "type": "str",
            "no_log": True
        },
        "storage_system_password": {
            "required": True,
            "type": "str",
            "no_log": True
        },
        "cpg_name": {
            "required": True,
            "type": "str"
        },
        "domain": {
            "type": "str"
        },
        "growth_increment": {
            "type": "float",
            "default": -1.0
        },
        "growth_increment_unit": {
            "type": "str",
            "choices": ['TiB', 'GiB', 'MiB'],
            "default": 'GiB'
        },
        "growth_limit": {
            "type": "float",
            "default": -1.0
        },
        "growth_limit_unit": {
            "type": "str",
            "choices": ['TiB', 'GiB', 'MiB'],
            "default": 'GiB'
        },
        "growth_warning": {
            "type": "float",
            "default": -1.0
        },
        "growth_warning_unit": {
            "type": "str",
            "choices": ['TiB', 'GiB', 'MiB'],
            "default": 'GiB'
        },
        "high_availability": {
            "type": "str",
            "choices": ['HAJBOD_JBOD', 'HAJBOD_DISK'],
        },
        "cage": {
            "type": "str",
            "required": False
        },
        "position": {
            "type": "str",
            "required": False
        },
        "keyValuePairs": {
            "type": "dict",
            "default": None
        }
    }

    # =========================================================================
    # Test: Module Arguments Specification
    # =========================================================================

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_module_args(self, mock_module, mock_client):
        """
        alletramp cpg - test module arguments specification
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (True, True, "CPG created successfully", {})
        
        cpg.main()
        
        mock_module.assert_called_with(argument_spec=self.fields)

    # =========================================================================
    # Test: Create CPG Operations
    # =========================================================================

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_success_without_issue(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg success without issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="CPG test_cpg created successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_success_with_issue(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", 
            {"warning": "Some disk space warning"}
        )

        with self.assertRaises(SystemExit):
            cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="CPG test_cpg created successfully", 
            issue={"warning": "Some disk space warning"}
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_already_exists(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg idempotency (cpg already exists)
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, False, "CPG test_cpg already exists", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="CPG test_cpg already exists"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_failure(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            False, False, "CPG test_cpg creation failed | Invalid parameters", {}
        )

        cpg.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            changed=False, msg="CPG test_cpg creation failed | Invalid parameters"
        )

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_minimal_params(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg with minimal parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG_MINIMAL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="CPG test_cpg created successfully"
        )

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_with_growth_params(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg with growth parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", {}
        )

        cpg.main()

        # Verify create_cpg was called with growth parameters
        mock_flowkit_client.create_cpg.assert_called()
        call_args = mock_flowkit_client.create_cpg.call_args
        self.assertEqual(call_args[0][0], 'test_cpg')

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_with_high_availability(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg with high availability option
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="CPG test_cpg created successfully"
        )

    # =========================================================================
    # Test: Delete CPG Operations
    # =========================================================================

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_delete_cpg_success(self, mock_module, mock_client):
        """
        alletramp cpg - test delete cpg success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_cpg.return_value = (
            True, True, "CPG test_cpg deleted successfully", {}
        )

        cpg.main()

        mock_flowkit_client.delete_cpg.assert_called_with(name='test_cpg')
        instance.exit_json.assert_called_with(
            changed=True, msg="CPG test_cpg deleted successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_delete_cpg_not_present(self, mock_module, mock_client):
        """
        alletramp cpg - test delete cpg idempotency (cpg does not exist)
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_cpg.return_value = (
            True, False, "CPG test_cpg does not exist", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="CPG test_cpg does not exist"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_delete_cpg_failure(self, mock_module, mock_client):
        """
        alletramp cpg - test delete cpg failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_cpg.return_value = (
            False, False, "CPG test_cpg deletion failed | CPG in use", {}
        )

        cpg.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            changed=False, msg="CPG test_cpg deletion failed | CPG in use"
        )

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp cpg - test flowkit client is initialized with correct parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG created successfully", {}
        )

        cpg.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp cpg - test flowkit client logout is called after operation
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG created successfully", {}
        )

        cpg.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_flowkit_client_logout_on_failure(self, mock_module, mock_client):
        """
        alletramp cpg - test flowkit client logout is called even on operation failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            False, False, "CPG creation failed", {}
        )

        cpg.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_flowkit_client_logout_exception_suppressed(self, mock_module, mock_client):
        """
        alletramp cpg - test flowkit client logout exception is suppressed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG created successfully", {}
        )
        mock_flowkit_client.logout.side_effect = Exception("Logout failed")

        # Should not raise exception
        cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="CPG created successfully"
        )

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_cpg.AnsibleClient', None)
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp cpg - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            cpg.main()

        instance.fail_json.assert_called_with(
            msg="Python hpe_storage_flowkit_py package is required."
        )

    # =========================================================================
    # Test: Exception Handling
    # =========================================================================

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_exception(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg with exception
        """
        mock_module.params = self.PARAMS_FOR_CREATE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.side_effect = Exception("Connection error")

        cpg.main()

        instance.fail_json.assert_called()
        call_args = instance.fail_json.call_args
        self.assertIn("Exception occured", call_args[1]['msg'])

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_delete_cpg_exception(self, mock_module, mock_client):
        """
        alletramp cpg - test delete cpg with exception
        """
        mock_module.params = self.PARAMS_FOR_DELETE_CPG
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_cpg.side_effect = Exception("API error")

        cpg.main()

        instance.fail_json.assert_called()
        call_args = instance.fail_json.call_args
        self.assertIn("Exception occured", call_args[1]['msg'])

    # =========================================================================
    # Test: Parameter Variations
    # =========================================================================

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_with_cage_and_position(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg with cage and position parameters
        """
        params = self.PARAMS_FOR_CREATE_CPG.copy()
        params['cage'] = '0,1,2'
        params['position'] = '0,1'
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="CPG test_cpg created successfully"
        )

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_with_key_value_pairs(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg with keyValuePairs
        """
        params = self.PARAMS_FOR_CREATE_CPG.copy()
        params['keyValuePairs'] = {'v3_key': 'value1', 'dp_key': 'value2'}
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="CPG test_cpg created successfully"
        )

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_ha_jbod(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg with HAJBOD_JBOD high availability
        """
        params = self.PARAMS_FOR_CREATE_CPG.copy()
        params['high_availability'] = 'HAJBOD_JBOD'
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="CPG test_cpg created successfully"
        )

    @mock.patch('modules.alletramp_cpg.AnsibleClient')
    @mock.patch('modules.alletramp_cpg.AnsibleModule')
    def test_create_cpg_different_units(self, mock_module, mock_client):
        """
        alletramp cpg - test create cpg with different size units
        """
        params = self.PARAMS_FOR_CREATE_CPG.copy()
        params['growth_increment_unit'] = 'TiB'
        params['growth_limit_unit'] = 'MiB'
        params['growth_warning_unit'] = 'TiB'
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_cpg.return_value = (
            True, True, "CPG test_cpg created successfully", {}
        )

        cpg.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="CPG test_cpg created successfully"
        )


if __name__ == '__main__':
    unittest.main()
