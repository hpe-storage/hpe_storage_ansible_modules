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
from modules import alletramp_host as host
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampHost(unittest.TestCase):
    """
    Test suite for the alletramp_host Ansible module.
    
    Tests cover all host operations through the new architecture flow:
    hpe_storage_ansible_modules → hpe_storage_flowkit_py → v1 workflows
    
    Operations tested:
    - create_host
    - delete_host  
    - modify_host
    - add_initiator_chap
    - remove_initiator_chap
    - add_target_chap
    - remove_target_chap
    - add_fc_path_to_host
    - remove_fc_path_from_host
    - add_iscsi_path_to_host
    - remove_iscsi_path_from_host
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_CREATE_HOST = {
        'operation': 'create_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': 'testdomain',
        'host_new_name': None,
        'host_fc_wwns': ['20:00:00:00:00:00:00:01', '20:00:00:00:00:00:00:02'],
        'host_iscsi_names': ['iqn.2020-01.com.example:storage.target1'],
        'host_persona': 'GENERIC_ALUA',
        'force_path_removal': None,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_CREATE_HOST_MINIMAL = {
        'operation': 'create_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_DELETE_HOST = {
        'operation': 'delete_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_MODIFY_HOST = {
        'operation': 'modify_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': 'newhostname',
        'host_fc_wwns': None,
        'host_iscsi_names': None,
        'host_persona': 'VMWARE',
        'force_path_removal': None,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_ADD_INITIATOR_CHAP = {
        'operation': 'add_initiator_chap',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': 'chapuser',
        'chap_secret': 'secretsecret',  # 12 characters minimum
        'chap_secret_hex': False
    }

    PARAMS_FOR_ADD_INITIATOR_CHAP_HEX = {
        'operation': 'add_initiator_chap',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': 'chapuser',
        'chap_secret': '0123456789abcdef0123456789abcdef',  # 32 hex characters
        'chap_secret_hex': True
    }

    PARAMS_FOR_REMOVE_INITIATOR_CHAP = {
        'operation': 'remove_initiator_chap',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_ADD_TARGET_CHAP = {
        'operation': 'add_target_chap',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': 'targetchapuser',
        'chap_secret': 'targetsecret12',  # 12-16 characters
        'chap_secret_hex': False
    }

    PARAMS_FOR_REMOVE_TARGET_CHAP = {
        'operation': 'remove_target_chap',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_ADD_FC_PATH = {
        'operation': 'add_fc_path_to_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': ['20:00:00:00:00:00:00:01', '20:00:00:00:00:00:00:02'],
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_REMOVE_FC_PATH = {
        'operation': 'remove_fc_path_from_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': ['20:00:00:00:00:00:00:01'],
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': False,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_REMOVE_FC_PATH_FORCE = {
        'operation': 'remove_fc_path_from_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': ['20:00:00:00:00:00:00:01'],
        'host_iscsi_names': None,
        'host_persona': None,
        'force_path_removal': True,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_ADD_ISCSI_PATH = {
        'operation': 'add_iscsi_path_to_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': ['iqn.2020-01.com.example:storage.target1', 'iqn.2020-01.com.example:storage.target2'],
        'host_persona': None,
        'force_path_removal': None,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_REMOVE_ISCSI_PATH = {
        'operation': 'remove_iscsi_path_from_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': ['iqn.2020-01.com.example:storage.target1'],
        'host_persona': None,
        'force_path_removal': False,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    PARAMS_FOR_REMOVE_ISCSI_PATH_FORCE = {
        'operation': 'remove_iscsi_path_from_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'host_name': 'testhost',
        'host_domain': None,
        'host_new_name': None,
        'host_fc_wwns': None,
        'host_iscsi_names': ['iqn.2020-01.com.example:storage.target1'],
        'host_persona': None,
        'force_path_removal': True,
        'chap_name': None,
        'chap_secret': None,
        'chap_secret_hex': None
    }

    # Module argument specification
    fields = {
        "operation": {
            "required": True,
            "choices": [
                'create_host',
                'delete_host',
                'modify_host',
                'add_initiator_chap',
                'remove_initiator_chap',
                'add_target_chap',
                'remove_target_chap',
                'add_fc_path_to_host',
                'remove_fc_path_from_host',
                'add_iscsi_path_to_host',
                'remove_iscsi_path_from_host'
            ],
            "type": 'str'
        },
        "storage_system_ip": {"required": True, "type": "str"},
        "storage_system_username": {"required": True, "type": "str", "no_log": True},
        "storage_system_password": {"required": True, "type": "str", "no_log": True},
        "host_name": {"type": "str"},
        "host_domain": {"type": "str"},
        "host_new_name": {"type": "str"},
        "host_fc_wwns": {"type": "list"},
        "host_iscsi_names": {"type": "list"},
        "host_persona": {
            "required": False,
            "type": "str",
            "choices": [
                "GENERIC_ALUA",
                "VMWARE",
                "HPUX",
                "WINDOWS_SERVER",
                "AIX",
                "SOLARIS"
            ]
        },
        "force_path_removal": {"type": "bool"},
        "chap_name": {"type": "str"},
        "chap_secret": {"type": "str"},
        "chap_secret_hex": {"type": "bool"}
    }

    # =========================================================================
    # Test: Module Arguments Specification
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_module_args(self, mock_module, mock_client):
        """
        alletramp host - test module arguments specification
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (True, True, "Created host 'testhost' successfully", {})
        
        host.main()
        
        mock_module.assert_called_with(argument_spec=self.fields)

    # =========================================================================
    # Test: Create Host Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_success_without_issue(self, mock_module, mock_client):
        """
        alletramp host - test create host success without issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'testhost' successfully", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Created host 'testhost' successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_success_with_issue(self, mock_module, mock_client):
        """
        alletramp host - test create host success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'testhost' successfully", 
            {"warning": "Some paths not added"}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Created host 'testhost' successfully", 
            issue={"warning": "Some paths not added"}
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_already_exists(self, mock_module, mock_client):
        """
        alletramp host - test create host idempotency (host already exists)
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, False, "Host 'testhost' already exists", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host 'testhost' already exists"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_failure(self, mock_module, mock_client):
        """
        alletramp host - test create host failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            False, False, "Create host 'testhost' failed | Connection error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Create host 'testhost' failed | Connection error"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_minimal_params(self, mock_module, mock_client):
        """
        alletramp host - test create host with minimal parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST_MINIMAL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'testhost' successfully", {}
        )

        host.main()

        mock_flowkit_client.create_host.assert_called_with(
            name='testhost',
            iscsiNames=None,
            FCWwns=None,
            host_domain=None,
            host_persona=None
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Created host 'testhost' successfully"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_with_all_personas(self, mock_module, mock_client):
        """
        alletramp host - test create host with different persona values
        """
        personas = ['GENERIC_ALUA', 'VMWARE', 'HPUX', 'WINDOWS_SERVER', 'AIX', 'SOLARIS']
        
        for persona in personas:
            with self.subTest(persona=persona):
                params = self.PARAMS_FOR_CREATE_HOST.copy()
                params['host_persona'] = persona
                mock_module.params = params
                mock_module.return_value = mock_module
                instance = mock_module.return_value

                mock_flowkit_client = MagicMock()
                mock_client.return_value = mock_flowkit_client
                mock_flowkit_client.create_host.return_value = (
                    True, True, f"Created host 'testhost' successfully", {}
                )

                host.main()

                instance.exit_json.assert_called()

    # =========================================================================
    # Test: Delete Host Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_delete_host_success(self, mock_module, mock_client):
        """
        alletramp host - test delete host success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_host.return_value = (
            True, True, "Deleted host 'testhost' successfully", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Deleted host 'testhost' successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_delete_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test delete host idempotency (host does not exist)
        """
        mock_module.params = self.PARAMS_FOR_DELETE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_host.return_value = (
            True, False, "Host 'testhost' not present", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host 'testhost' not present"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_delete_host_failure(self, mock_module, mock_client):
        """
        alletramp host - test delete host failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_host.return_value = (
            False, False, "Delete host 'testhost' failed | Host has active VLUNs", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Delete host 'testhost' failed | Host has active VLUNs"
        )

    # =========================================================================
    # Test: Modify Host Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_modify_host_success(self, mock_module, mock_client):
        """
        alletramp host - test modify host success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_host.return_value = (
            True, True, "Modified host 'testhost' successfully", {}
        )

        host.main()

        mock_flowkit_client.modify_host.assert_called_with(
            'testhost', 'newhostname', persona='VMWARE'
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Modified host 'testhost' successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_modify_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test modify host when host does not exist
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_host.return_value = (
            False, False, "Host 'testhost' not present", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Host 'testhost' not present")

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_modify_host_failure(self, mock_module, mock_client):
        """
        alletramp host - test modify host failure
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_host.return_value = (
            False, False, "Modify host 'testhost' failed | Invalid persona value", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Modify host 'testhost' failed | Invalid persona value"
        )

    # =========================================================================
    # Test: Add Initiator CHAP Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_initiator_chap_success(self, mock_module, mock_client):
        """
        alletramp host - test add initiator CHAP success
        """
        mock_module.params = self.PARAMS_FOR_ADD_INITIATOR_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_initiator_chap.return_value = (
            True, True, "Added initiator CHAP to host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.add_initiator_chap.assert_called_with(
            'testhost', 'chapuser', 'secretsecret', False
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Added initiator CHAP to host 'testhost'"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_initiator_chap_hex_success(self, mock_module, mock_client):
        """
        alletramp host - test add initiator CHAP with hex secret success
        """
        mock_module.params = self.PARAMS_FOR_ADD_INITIATOR_CHAP_HEX
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_initiator_chap.return_value = (
            True, True, "Added initiator CHAP to host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.add_initiator_chap.assert_called_with(
            'testhost', 'chapuser', '0123456789abcdef0123456789abcdef', True
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Added initiator CHAP to host 'testhost'"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_initiator_chap_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test add initiator CHAP when host does not exist
        """
        mock_module.params = self.PARAMS_FOR_ADD_INITIATOR_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_initiator_chap.return_value = (
            False, False, "Host 'testhost' not present", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Host 'testhost' not present")

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_initiator_chap_invalid_secret_length(self, mock_module, mock_client):
        """
        alletramp host - test add initiator CHAP with invalid secret length
        """
        params = self.PARAMS_FOR_ADD_INITIATOR_CHAP.copy()
        params['chap_secret'] = 'short'  # Less than 12 characters
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_initiator_chap.return_value = (
            False, False, "Add initiator CHAP failed for host testhost | Chap secret must be 12 to 16 characters", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called()

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_initiator_chap_failure(self, mock_module, mock_client):
        """
        alletramp host - test add initiator CHAP failure
        """
        mock_module.params = self.PARAMS_FOR_ADD_INITIATOR_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_initiator_chap.return_value = (
            False, False, "Add initiator CHAP failed for host testhost | API error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Add initiator CHAP failed for host testhost | API error"
        )

    # =========================================================================
    # Test: Remove Initiator CHAP Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_initiator_chap_success(self, mock_module, mock_client):
        """
        alletramp host - test remove initiator CHAP success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_INITIATOR_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_initiator_chap.return_value = (
            True, True, "Removed initiator CHAP from host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.remove_initiator_chap.assert_called_with('testhost')
        instance.exit_json.assert_called_with(
            changed=True, msg="Removed initiator CHAP from host 'testhost'"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_initiator_chap_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test remove initiator CHAP when host does not exist (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_INITIATOR_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_initiator_chap.return_value = (
            True, False, "Host 'testhost' not present (treat as removed)", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host 'testhost' not present (treat as removed)"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_initiator_chap_failure(self, mock_module, mock_client):
        """
        alletramp host - test remove initiator CHAP failure
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_INITIATOR_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_initiator_chap.return_value = (
            False, False, "Remove initiator CHAP failed | API error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Remove initiator CHAP failed | API error")

    # =========================================================================
    # Test: Add Target CHAP Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_target_chap_success(self, mock_module, mock_client):
        """
        alletramp host - test add target CHAP success
        """
        mock_module.params = self.PARAMS_FOR_ADD_TARGET_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_target_chap.return_value = (
            True, True, "Added target CHAP to host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.add_target_chap.assert_called_with(
            'testhost', 'targetchapuser', 'targetsecret12', False
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Added target CHAP to host 'testhost'"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_target_chap_initiator_not_exists(self, mock_module, mock_client):
        """
        alletramp host - test add target CHAP when initiator CHAP does not exist
        """
        mock_module.params = self.PARAMS_FOR_ADD_TARGET_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_target_chap.return_value = (
            True, False, "Initiator CHAP must exist before adding target CHAP on host 'testhost'", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, 
            msg="Initiator CHAP must exist before adding target CHAP on host 'testhost'"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_target_chap_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test add target CHAP when host does not exist
        """
        mock_module.params = self.PARAMS_FOR_ADD_TARGET_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_target_chap.return_value = (
            True, False, "Host 'testhost' not present", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host 'testhost' not present"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_target_chap_failure(self, mock_module, mock_client):
        """
        alletramp host - test add target CHAP failure
        """
        mock_module.params = self.PARAMS_FOR_ADD_TARGET_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_target_chap.return_value = (
            False, False, "Adding target CHAP failed for host testhost| API error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Adding target CHAP failed for host testhost| API error"
        )

    # =========================================================================
    # Test: Remove Target CHAP Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_target_chap_success(self, mock_module, mock_client):
        """
        alletramp host - test remove target CHAP success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_TARGET_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_target_chap.return_value = (
            True, True, "Removed target CHAP from host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.remove_target_chap.assert_called_with('testhost')
        instance.exit_json.assert_called_with(
            changed=True, msg="Removed target CHAP from host 'testhost'"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_target_chap_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test remove target CHAP when host does not exist (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_TARGET_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_target_chap.return_value = (
            True, False, "Host 'testhost' not present (treat as removed)", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host 'testhost' not present (treat as removed)"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_target_chap_failure(self, mock_module, mock_client):
        """
        alletramp host - test remove target CHAP failure
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_TARGET_CHAP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_target_chap.return_value = (
            False, False, "Remove target CHAP failed | API error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Remove target CHAP failed | API error")

    # =========================================================================
    # Test: Add FC Path Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_fc_path_success(self, mock_module, mock_client):
        """
        alletramp host - test add FC path success
        """
        mock_module.params = self.PARAMS_FOR_ADD_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_fc_path_to_host.return_value = (
            True, True, 
            "Added FC path(s) 2000000000000001, 2000000000000002 to host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.add_fc_path_to_host.assert_called_with(
            'testhost', 
            ['20:00:00:00:00:00:00:01', '20:00:00:00:00:00:00:02']
        )
        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Added FC path(s) 2000000000000001, 2000000000000002 to host 'testhost'"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_fc_path_already_assigned_same_host(self, mock_module, mock_client):
        """
        alletramp host - test add FC path when already assigned to same host (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_ADD_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_fc_path_to_host.return_value = (
            True, False, 
            "FC path(s) 2000000000000001, 2000000000000002 already assigned to this host", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, 
            msg="FC path(s) 2000000000000001, 2000000000000002 already assigned to this host"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_fc_path_assigned_other_host(self, mock_module, mock_client):
        """
        alletramp host - test add FC path when already assigned to other host
        """
        mock_module.params = self.PARAMS_FOR_ADD_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_fc_path_to_host.return_value = (
            False, False, 
            "FC path(s) 2000000000000001 already assigned to other host", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="FC path(s) 2000000000000001 already assigned to other host"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_fc_path_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test add FC path when host does not exist
        """
        mock_module.params = self.PARAMS_FOR_ADD_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_fc_path_to_host.return_value = (
            True, False, "Host 'testhost' not present", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host 'testhost' not present"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_fc_path_no_wwns_provided(self, mock_module, mock_client):
        """
        alletramp host - test add FC path with no WWNs provided
        """
        params = self.PARAMS_FOR_ADD_FC_PATH.copy()
        params['host_fc_wwns'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_fc_path_to_host.return_value = (
            True, False, "No FC WWNs provided", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="No FC WWNs provided"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_fc_path_failure(self, mock_module, mock_client):
        """
        alletramp host - test add FC path failure
        """
        mock_module.params = self.PARAMS_FOR_ADD_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_fc_path_to_host.return_value = (
            False, False, "Add FC paths failed | Connection error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Add FC paths failed | Connection error")

    # =========================================================================
    # Test: Remove FC Path Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_fc_path_success(self, mock_module, mock_client):
        """
        alletramp host - test remove FC path success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_fc_path_from_host.return_value = (
            True, True, "Removed FC path(s) 2000000000000001 from host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.remove_fc_path_from_host.assert_called_with(
            'testhost', 
            ['20:00:00:00:00:00:00:01'],
            force_path_removal=False
        )
        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Removed FC path(s) 2000000000000001 from host 'testhost'"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_fc_path_force_success(self, mock_module, mock_client):
        """
        alletramp host - test remove FC path with force option success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_FC_PATH_FORCE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_fc_path_from_host.return_value = (
            True, True, "Removed FC path(s) 2000000000000001 from host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.remove_fc_path_from_host.assert_called_with(
            'testhost', 
            ['20:00:00:00:00:00:00:01'],
            force_path_removal=True
        )
        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Removed FC path(s) 2000000000000001 from host 'testhost'"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_fc_path_already_removed(self, mock_module, mock_client):
        """
        alletramp host - test remove FC path when already removed (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_fc_path_from_host.return_value = (
            True, False, "Seems FC path(s) 2000000000000001 not present/already removed on system", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, 
            msg="Seems FC path(s) 2000000000000001 not present/already removed on system"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_fc_path_assigned_other_host(self, mock_module, mock_client):
        """
        alletramp host - test remove FC path when assigned to other host
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_fc_path_from_host.return_value = (
            False, False, "FC path(s) 2000000000000001 assigned to other host", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="FC path(s) 2000000000000001 assigned to other host"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_fc_path_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test remove FC path when host does not exist (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_fc_path_from_host.return_value = (
            True, False, "Host 'testhost' not present (treat as removed)", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host 'testhost' not present (treat as removed)"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_fc_path_failure(self, mock_module, mock_client):
        """
        alletramp host - test remove FC path failure
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_FC_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_fc_path_from_host.return_value = (
            False, False, "Remove FC paths failed | Connection error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Remove FC paths failed | Connection error")

    # =========================================================================
    # Test: Add iSCSI Path Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_iscsi_path_success(self, mock_module, mock_client):
        """
        alletramp host - test add iSCSI path success
        """
        mock_module.params = self.PARAMS_FOR_ADD_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_iscsi_path_to_host.return_value = (
            True, True, 
            "Added iSCSI name(s) iqn.2020-01.com.example:storage.target1, iqn.2020-01.com.example:storage.target2 to host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.add_iscsi_path_to_host.assert_called_with(
            'testhost', 
            ['iqn.2020-01.com.example:storage.target1', 'iqn.2020-01.com.example:storage.target2']
        )
        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Added iSCSI name(s) iqn.2020-01.com.example:storage.target1, iqn.2020-01.com.example:storage.target2 to host 'testhost'"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_iscsi_path_already_assigned_same_host(self, mock_module, mock_client):
        """
        alletramp host - test add iSCSI path when already assigned to same host (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_ADD_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_iscsi_path_to_host.return_value = (
            True, False, 
            "iSCSI name(s) iqn.2020-01.com.example:storage.target1 already assigned to this host", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, 
            msg="iSCSI name(s) iqn.2020-01.com.example:storage.target1 already assigned to this host"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_iscsi_path_assigned_other_host(self, mock_module, mock_client):
        """
        alletramp host - test add iSCSI path when already assigned to other host
        """
        mock_module.params = self.PARAMS_FOR_ADD_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_iscsi_path_to_host.return_value = (
            False, False, 
            "iSCSI name(s) iqn.2020-01.com.example:storage.target1 already assigned to other host", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="iSCSI name(s) iqn.2020-01.com.example:storage.target1 already assigned to other host"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_iscsi_path_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test add iSCSI path when host does not exist
        """
        mock_module.params = self.PARAMS_FOR_ADD_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_iscsi_path_to_host.return_value = (
            False, False, "Host 'testhost' not present", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Host 'testhost' not present")

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_iscsi_path_no_names_provided(self, mock_module, mock_client):
        """
        alletramp host - test add iSCSI path with no names provided
        """
        params = self.PARAMS_FOR_ADD_ISCSI_PATH.copy()
        params['host_iscsi_names'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_iscsi_path_to_host.return_value = (
            True, False, "No iSCSI names provided", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="No iSCSI names provided"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_iscsi_path_failure(self, mock_module, mock_client):
        """
        alletramp host - test add iSCSI path failure
        """
        mock_module.params = self.PARAMS_FOR_ADD_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_iscsi_path_to_host.return_value = (
            False, False, "Add iSCSI paths failed | Connection error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Add iSCSI paths failed | Connection error")

    # =========================================================================
    # Test: Remove iSCSI Path Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_iscsi_path_success(self, mock_module, mock_client):
        """
        alletramp host - test remove iSCSI path success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_iscsi_path_from_host.return_value = (
            True, True, "Removed iSCSI name(s) iqn.2020-01.com.example:storage.target1 from host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.remove_iscsi_path_from_host.assert_called_with(
            'testhost', 
            ['iqn.2020-01.com.example:storage.target1'],
            force_path_removal=False
        )
        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Removed iSCSI name(s) iqn.2020-01.com.example:storage.target1 from host 'testhost'"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_iscsi_path_force_success(self, mock_module, mock_client):
        """
        alletramp host - test remove iSCSI path with force option success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_ISCSI_PATH_FORCE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_iscsi_path_from_host.return_value = (
            True, True, "Removed iSCSI name(s) iqn.2020-01.com.example:storage.target1 from host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.remove_iscsi_path_from_host.assert_called_with(
            'testhost', 
            ['iqn.2020-01.com.example:storage.target1'],
            force_path_removal=True
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_iscsi_path_already_removed(self, mock_module, mock_client):
        """
        alletramp host - test remove iSCSI path when already removed (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_iscsi_path_from_host.return_value = (
            True, False, "iSCSI name(s) iqn.2020-01.com.example:storage.target1 already removed/not present on system", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, 
            msg="iSCSI name(s) iqn.2020-01.com.example:storage.target1 already removed/not present on system"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_iscsi_path_assigned_other_host(self, mock_module, mock_client):
        """
        alletramp host - test remove iSCSI path when assigned to other host
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_iscsi_path_from_host.return_value = (
            False, False, "iSCSI name(s) iqn.2020-01.com.example:storage.target1 assigned to other host", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="iSCSI name(s) iqn.2020-01.com.example:storage.target1 assigned to other host"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_iscsi_path_host_not_present(self, mock_module, mock_client):
        """
        alletramp host - test remove iSCSI path when host does not exist (idempotent)
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_iscsi_path_from_host.return_value = (
            True, False, "Host 'testhost' not present (treat as removed)", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Host 'testhost' not present (treat as removed)"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_remove_iscsi_path_failure(self, mock_module, mock_client):
        """
        alletramp host - test remove iSCSI path failure
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_ISCSI_PATH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_iscsi_path_from_host.return_value = (
            False, False, "Remove iSCSI paths failed | Connection error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Remove iSCSI paths failed | Connection error")

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp host - test flowkit client is initialized with correct parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'testhost' successfully", {}
        )

        host.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp host - test flowkit client logout is called after operation
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'testhost' successfully", {}
        )

        host.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_flowkit_client_logout_on_failure(self, mock_module, mock_client):
        """
        alletramp host - test flowkit client logout is called even on operation failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            False, False, "Create host 'testhost' failed", {}
        )

        host.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_flowkit_client_logout_exception_suppressed(self, mock_module, mock_client):
        """
        alletramp host - test flowkit client logout exception is suppressed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'testhost' successfully", {}
        )
        mock_flowkit_client.logout.side_effect = Exception("Logout failed")

        # Should not raise exception
        host.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Created host 'testhost' successfully"
        )

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient', None)
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp host - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            host.main()

        instance.fail_json.assert_called_with(
            msg="Python hpe_storage_flowkit_py package is required."
        )

    # =========================================================================
    # Test: Exception Handling During Operations
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_api_exception(self, mock_module, mock_client):
        """
        alletramp host - test create host with API exception
        """
        mock_module.params = self.PARAMS_FOR_CREATE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            False, False, "Create host 'testhost' failed | HTTPError: 401 Unauthorized", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Create host 'testhost' failed | HTTPError: 401 Unauthorized"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_delete_host_api_exception(self, mock_module, mock_client):
        """
        alletramp host - test delete host with API exception
        """
        mock_module.params = self.PARAMS_FOR_DELETE_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_host.return_value = (
            False, False, "Delete host 'testhost' failed | Connection timeout", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Delete host 'testhost' failed | Connection timeout"
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_modify_host_api_exception(self, mock_module, mock_client):
        """
        alletramp host - test modify host with API exception
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_host.return_value = (
            False, False, "Modify host 'testhost' failed | SSL Certificate error", {}
        )

        host.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(
            msg="Modify host 'testhost' failed | SSL Certificate error"
        )

    # =========================================================================
    # Test: Parameter Validation Edge Cases
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_empty_wwns_list(self, mock_module, mock_client):
        """
        alletramp host - test create host with empty WWNs list
        """
        params = self.PARAMS_FOR_CREATE_HOST.copy()
        params['host_fc_wwns'] = []
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'testhost' successfully", {}
        )

        host.main()

        mock_flowkit_client.create_host.assert_called_with(
            name='testhost',
            iscsiNames=['iqn.2020-01.com.example:storage.target1'],
            FCWwns=[],
            host_domain='testdomain',
            host_persona='GENERIC_ALUA'
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_empty_iscsi_list(self, mock_module, mock_client):
        """
        alletramp host - test create host with empty iSCSI names list
        """
        params = self.PARAMS_FOR_CREATE_HOST.copy()
        params['host_iscsi_names'] = []
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'testhost' successfully", {}
        )

        host.main()

        mock_flowkit_client.create_host.assert_called_with(
            name='testhost',
            iscsiNames=[],
            FCWwns=['20:00:00:00:00:00:00:01', '20:00:00:00:00:00:00:02'],
            host_domain='testdomain',
            host_persona='GENERIC_ALUA'
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_modify_host_name_only(self, mock_module, mock_client):
        """
        alletramp host - test modify host with new name only (no persona change)
        """
        params = self.PARAMS_FOR_MODIFY_HOST.copy()
        params['host_persona'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_host.return_value = (
            True, True, "Modified host 'testhost' successfully", {}
        )

        host.main()

        mock_flowkit_client.modify_host.assert_called_with(
            'testhost', 'newhostname', persona=None
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_modify_host_persona_only(self, mock_module, mock_client):
        """
        alletramp host - test modify host with persona only (no name change)
        """
        params = self.PARAMS_FOR_MODIFY_HOST.copy()
        params['host_new_name'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_host.return_value = (
            True, True, "Modified host 'testhost' successfully", {}
        )

        host.main()

        mock_flowkit_client.modify_host.assert_called_with(
            'testhost', None, persona='VMWARE'
        )

    # =========================================================================
    # Test: Special Characters in Host Names
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_create_host_with_special_chars_in_name(self, mock_module, mock_client):
        """
        alletramp host - test create host with special characters in name
        """
        params = self.PARAMS_FOR_CREATE_HOST.copy()
        params['host_name'] = 'test-host_01'
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_host.return_value = (
            True, True, "Created host 'test-host_01' successfully", {}
        )

        host.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="Created host 'test-host_01' successfully"
        )

    # =========================================================================
    # Test: Multiple WWNs / iSCSI Names
    # =========================================================================

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_multiple_fc_paths(self, mock_module, mock_client):
        """
        alletramp host - test adding multiple FC paths at once
        """
        params = self.PARAMS_FOR_ADD_FC_PATH.copy()
        params['host_fc_wwns'] = [
            '20:00:00:00:00:00:00:01',
            '20:00:00:00:00:00:00:02',
            '20:00:00:00:00:00:00:03',
            '20:00:00:00:00:00:00:04'
        ]
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_fc_path_to_host.return_value = (
            True, True, "Added FC path(s) to host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.add_fc_path_to_host.assert_called_with(
            'testhost',
            [
                '20:00:00:00:00:00:00:01',
                '20:00:00:00:00:00:00:02',
                '20:00:00:00:00:00:00:03',
                '20:00:00:00:00:00:00:04'
            ]
        )

    @mock.patch('modules.alletramp_host.AnsibleClient')
    @mock.patch('modules.alletramp_host.AnsibleModule')
    def test_add_multiple_iscsi_paths(self, mock_module, mock_client):
        """
        alletramp host - test adding multiple iSCSI paths at once
        """
        params = self.PARAMS_FOR_ADD_ISCSI_PATH.copy()
        params['host_iscsi_names'] = [
            'iqn.2020-01.com.example:storage.target1',
            'iqn.2020-01.com.example:storage.target2',
            'iqn.2020-01.com.example:storage.target3'
        ]
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_iscsi_path_to_host.return_value = (
            True, True, "Added iSCSI name(s) to host 'testhost'", {}
        )

        host.main()

        mock_flowkit_client.add_iscsi_path_to_host.assert_called_with(
            'testhost',
            [
                'iqn.2020-01.com.example:storage.target1',
                'iqn.2020-01.com.example:storage.target2',
                'iqn.2020-01.com.example:storage.target3'
            ]
        )


if __name__ == '__main__':
    unittest.main()
