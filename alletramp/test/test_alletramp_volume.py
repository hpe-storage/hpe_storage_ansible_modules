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
from modules import alletramp_volume as volume
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampVolume(unittest.TestCase):
    """
    Test suite for the alletramp_volume Ansible module.
    
    Tests cover Volume operations:
    - create
    - delete
    - modify
    - grow
    - tune
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_CREATE_VOLUME = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'cpg': 'test_cpg',
        'size': 10240,
        'size_unit': 'MiB',
        'new_name': None,
        'expiration_time': None,
        'retention_time': None,
        'expiration_unit': 'hours',
        'retention_unit': 'hours',
        'userAllocWarning': None,
        'type': 'CONVERSIONTYPE_V1',
        'reduce': None,
        'comments': None,
        'count': None,
        'dataReduction': None,
        'keyValuePairs': None,
        'ransomWare': None,
        'growth_size_mib': None,
        'wwn': None,
        'saveToNewName': None
    }

    PARAMS_FOR_CREATE_VOLUME_WITH_OPTIONS = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'cpg': 'test_cpg',
        'size': 10240,
        'size_unit': 'GiB',
        'new_name': None,
        'expiration_time': 24,
        'retention_time': 48,
        'expiration_unit': 'hours',
        'retention_unit': 'hours',
        'userAllocWarning': 80,
        'type': 'CONVERSIONTYPE_V1',
        'reduce': None,
        'comments': 'Test volume',
        'count': 1,
        'dataReduction': True,
        'keyValuePairs': {'v3_app': 'test'},
        'ransomWare': True,
        'growth_size_mib': None,
        'wwn': None,
        'saveToNewName': None
    }

    PARAMS_FOR_DELETE_VOLUME = {
        'operation': 'delete',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'cpg': None,
        'size': None,
        'size_unit': 'MiB',
        'new_name': None,
        'expiration_time': None,
        'retention_time': None,
        'expiration_unit': 'hours',
        'retention_unit': 'hours',
        'userAllocWarning': None,
        'type': 'CONVERSIONTYPE_V1',
        'reduce': None,
        'comments': None,
        'count': None,
        'dataReduction': None,
        'keyValuePairs': None,
        'ransomWare': None,
        'growth_size_mib': None,
        'wwn': None,
        'saveToNewName': None
    }

    PARAMS_FOR_MODIFY_VOLUME = {
        'operation': 'modify',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'cpg': None,
        'size': None,
        'size_unit': 'MiB',
        'new_name': 'new_test_volume',
        'expiration_time': None,
        'retention_time': None,
        'expiration_unit': 'hours',
        'retention_unit': 'hours',
        'userAllocWarning': 90,
        'type': 'CONVERSIONTYPE_V1',
        'reduce': None,
        'comments': 'Modified volume',
        'count': None,
        'dataReduction': None,
        'keyValuePairs': None,
        'ransomWare': None,
        'growth_size_mib': None,
        'wwn': None,
        'saveToNewName': None
    }

    PARAMS_FOR_GROW_VOLUME = {
        'operation': 'grow',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'cpg': None,
        'size': None,
        'size_unit': 'MiB',
        'new_name': None,
        'expiration_time': None,
        'retention_time': None,
        'expiration_unit': 'hours',
        'retention_unit': 'hours',
        'userAllocWarning': None,
        'type': 'CONVERSIONTYPE_V1',
        'reduce': None,
        'comments': None,
        'count': None,
        'dataReduction': None,
        'keyValuePairs': None,
        'ransomWare': None,
        'growth_size_mib': 5120,
        'wwn': None,
        'saveToNewName': None
    }

    PARAMS_FOR_TUNE_VOLUME = {
        'operation': 'tune',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'cpg': 'new_cpg',
        'size': None,
        'size_unit': 'MiB',
        'new_name': None,
        'expiration_time': None,
        'retention_time': None,
        'expiration_unit': 'hours',
        'retention_unit': 'hours',
        'userAllocWarning': None,
        'type': 'CONVERSIONTYPE_V2',
        'reduce': None,
        'comments': None,
        'count': None,
        'dataReduction': None,
        'keyValuePairs': None,
        'ransomWare': None,
        'growth_size_mib': None,
        'wwn': None,
        'saveToNewName': 'tuned_volume'
    }

    # Module argument specification
    fields = {
        "operation": {
            "required": True,
            "choices": ['create', 'delete', 'modify', 'grow', 'tune'],
            "type": 'str'
        },
        "storage_system_ip": {"required": True, "type": "str"},
        "storage_system_username": {"required": True, "type": "str", "no_log": True},
        "storage_system_password": {"required": True, "type": "str", "no_log": True},
        "volume_name": {"required": True, "type": "str"},
        "cpg": {"type": "str", "default": None},
        "size": {"type": "int", "default": None},
        "size_unit": {"choices": ['MiB', 'GiB', 'TiB'], "type": 'str', "default": 'MiB'},
        "new_name": {"type": "str"},
        "expiration_time": {"type": "int", "default": None},
        "retention_time": {"type": "int", "default": None},
        "expiration_unit": {"type": "str", "default": "hours"},
        "retention_unit": {"type": "str", "default": "hours"},
        "userAllocWarning": {"type": "int"},
        "type": {
            "choices": ["CONVERSIONTYPE_THIN", "CONVERSIONTYPE_V1", "CONVERSIONTYPE_V2"],
            "type": "str",
            "default": "CONVERSIONTYPE_V1"
        },
        "reduce": {"type": "bool"},
        "comments": {"type": "str"},
        "count": {"type": "int", "default": None},
        "dataReduction": {"type": "bool", "default": None},
        "keyValuePairs": {"type": "dict", "default": None},
        "ransomWare": {"type": "bool", "default": None},
        "growth_size_mib": {"type": "int"},
        "wwn": {"type": "str"},
        "saveToNewName": {"type": "str"}
    }

    # =========================================================================
    # Test: Module Arguments Specification
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_module_args(self, mock_module, mock_client):
        """
        alletramp volume - test module arguments specification
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (True, True, "Volume created successfully", {})
        
        volume.main()
        
        mock_module.assert_called_with(argument_spec=self.fields)

    # =========================================================================
    # Test: Create Volume Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_create_volume_success_without_issue(self, mock_module, mock_client):
        """
        alletramp volume - test create volume success without issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (
            True, True, "Volume test_volume created successfully", {}
        )

        volume.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Volume test_volume created successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_create_volume_success_with_issue(self, mock_module, mock_client):
        """
        alletramp volume - test create volume success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (
            True, True, "Volume test_volume created successfully", 
            {"warning": "Space warning"}
        )

        with self.assertRaises(SystemExit):
            volume.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Volume test_volume created successfully", 
            issue={"warning": "Space warning"}
        )

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_create_volume_already_exists(self, mock_module, mock_client):
        """
        alletramp volume - test create volume idempotency (volume already exists)
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (
            True, False, "Volume test_volume already exists", {}
        )

        volume.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Volume test_volume already exists"
        )

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_create_volume_failure(self, mock_module, mock_client):
        """
        alletramp volume - test create volume failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (
            False, False, "Volume creation failed | CPG not found", {}
        )

        volume.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            changed=False, msg="Volume creation failed | CPG not found"
        )

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_create_volume_with_all_options(self, mock_module, mock_client):
        """
        alletramp volume - test create volume with all options
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME_WITH_OPTIONS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (
            True, True, "Volume test_volume created successfully", {}
        )

        volume.main()

        mock_flowkit_client.create_volume.assert_called()
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume test_volume created successfully"
        )

    # =========================================================================
    # Test: Delete Volume Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_delete_volume_success(self, mock_module, mock_client):
        """
        alletramp volume - test delete volume success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_volume.return_value = (
            True, True, "Volume test_volume deleted successfully", {}
        )

        volume.main()

        mock_flowkit_client.delete_volume.assert_called_with(name='test_volume')
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume test_volume deleted successfully"
        )

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_delete_volume_not_present(self, mock_module, mock_client):
        """
        alletramp volume - test delete volume idempotency (volume does not exist)
        """
        mock_module.params = self.PARAMS_FOR_DELETE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_volume.return_value = (
            True, False, "Volume test_volume does not exist", {}
        )

        volume.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Volume test_volume does not exist"
        )

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_delete_volume_failure(self, mock_module, mock_client):
        """
        alletramp volume - test delete volume failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_volume.return_value = (
            False, False, "Volume deletion failed | Volume in use", {}
        )

        volume.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            changed=False, msg="Volume deletion failed | Volume in use"
        )

    # =========================================================================
    # Test: Modify Volume Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_modify_volume_success(self, mock_module, mock_client):
        """
        alletramp volume - test modify volume success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_volume.return_value = (
            True, True, "Volume test_volume modified successfully", {}
        )

        volume.main()

        mock_flowkit_client.modify_volume.assert_called()
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume test_volume modified successfully"
        )

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_modify_volume_failure(self, mock_module, mock_client):
        """
        alletramp volume - test modify volume failure
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_volume.return_value = (
            False, False, "Volume modification failed | Volume not found", {}
        )

        volume.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            changed=False, msg="Volume modification failed | Volume not found"
        )

    # =========================================================================
    # Test: Grow Volume Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_grow_volume_success(self, mock_module, mock_client):
        """
        alletramp volume - test grow volume success
        """
        mock_module.params = self.PARAMS_FOR_GROW_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.grow_volume.return_value = (
            True, True, "Volume test_volume grown successfully", {}
        )

        volume.main()

        mock_flowkit_client.grow_volume.assert_called_with('test_volume', 5120)
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume test_volume grown successfully"
        )

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_grow_volume_failure(self, mock_module, mock_client):
        """
        alletramp volume - test grow volume failure
        """
        mock_module.params = self.PARAMS_FOR_GROW_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.grow_volume.return_value = (
            False, False, "Grow volume failed | Insufficient space", {}
        )

        volume.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            changed=False, msg="Grow volume failed | Insufficient space"
        )

    # =========================================================================
    # Test: Tune Volume Operations
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_tune_volume_success(self, mock_module, mock_client):
        """
        alletramp volume - test tune volume success
        """
        mock_module.params = self.PARAMS_FOR_TUNE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.tune_volume.return_value = (
            True, True, "Volume test_volume tuned successfully", {}
        )

        volume.main()

        mock_flowkit_client.tune_volume.assert_called()
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume test_volume tuned successfully"
        )

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_tune_volume_failure(self, mock_module, mock_client):
        """
        alletramp volume - test tune volume failure
        """
        mock_module.params = self.PARAMS_FOR_TUNE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.tune_volume.return_value = (
            False, False, "Tune volume failed | Invalid conversion type", {}
        )

        volume.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            changed=False, msg="Tune volume failed | Invalid conversion type"
        )

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp volume - test flowkit client is initialized with correct parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (True, True, "Volume created", {})

        volume.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp volume - test flowkit client logout is called after operation
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (True, True, "Volume created", {})

        volume.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_flowkit_client_logout_exception_suppressed(self, mock_module, mock_client):
        """
        alletramp volume - test flowkit client logout exception is suppressed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.return_value = (True, True, "Volume created", {})
        mock_flowkit_client.logout.side_effect = Exception("Logout failed")

        volume.main()

        instance.exit_json.assert_called_with(changed=True, msg="Volume created")

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient', None)
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp volume - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            volume.main()

        instance.fail_json.assert_called_with(
            msg="Python hpe_storage_flowkit_py package is required."
        )

    # =========================================================================
    # Test: Exception Handling
    # =========================================================================

    @mock.patch('modules.alletramp_volume.AnsibleClient')
    @mock.patch('modules.alletramp_volume.AnsibleModule')
    def test_create_volume_exception(self, mock_module, mock_client):
        """
        alletramp volume - test create volume with exception
        """
        mock_module.params = self.PARAMS_FOR_CREATE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_volume.side_effect = Exception("Connection error")

        volume.main()

        instance.fail_json.assert_called()
        call_args = instance.fail_json.call_args
        self.assertIn("Exception occured", call_args[1]['msg'])


if __name__ == '__main__':
    unittest.main()
