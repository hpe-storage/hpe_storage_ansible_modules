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
from modules import alletramp_vlun as vlun
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampVlun(unittest.TestCase):
    """
    Test suite for the alletramp_vlun Ansible module.
    
    Tests cover VLUN operations:
    - export_volume_to_host
    - unexport_volume_from_host
    - export_volumeset_to_host
    - unexport_volumeset_from_host
    - export_volume_to_hostset
    - unexport_volume_from_hostset
    - export_volumeset_to_hostset
    - unexport_volumeset_from_hostset
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_EXPORT_VOLUME_TO_HOST = {
        'operation': 'export_volume_to_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'volume_set_name': None,
        'host_name': 'test_host',
        'host_set_name': None,
        'lun': 1,
        'autolun': False,
        'node_val': 0,
        'slot': 1,
        'card_port': 2
    }

    PARAMS_FOR_EXPORT_VOLUME_TO_HOST_AUTOLUN = {
        'operation': 'export_volume_to_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'volume_set_name': None,
        'host_name': 'test_host',
        'host_set_name': None,
        'lun': None,
        'autolun': True,
        'node_val': None,
        'slot': None,
        'card_port': None
    }

    PARAMS_FOR_UNEXPORT_VOLUME_FROM_HOST = {
        'operation': 'unexport_volume_from_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'volume_set_name': None,
        'host_name': 'test_host',
        'host_set_name': None,
        'lun': 1,
        'autolun': False,
        'node_val': 0,
        'slot': 1,
        'card_port': 2
    }

    PARAMS_FOR_EXPORT_VOLUMESET_TO_HOST = {
        'operation': 'export_volumeset_to_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': None,
        'volume_set_name': 'test_volumeset',
        'host_name': 'test_host',
        'host_set_name': None,
        'lun': 10,
        'autolun': False,
        'node_val': 1,
        'slot': 2,
        'card_port': 3
    }

    PARAMS_FOR_UNEXPORT_VOLUMESET_FROM_HOST = {
        'operation': 'unexport_volumeset_from_host',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': None,
        'volume_set_name': 'test_volumeset',
        'host_name': 'test_host',
        'host_set_name': None,
        'lun': 10,
        'autolun': False,
        'node_val': 1,
        'slot': 2,
        'card_port': 3
    }

    PARAMS_FOR_EXPORT_VOLUME_TO_HOSTSET = {
        'operation': 'export_volume_to_hostset',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'volume_set_name': None,
        'host_name': None,
        'host_set_name': 'test_hostset',
        'lun': 5,
        'autolun': False,
        'node_val': 0,
        'slot': 0,
        'card_port': 1
    }

    PARAMS_FOR_UNEXPORT_VOLUME_FROM_HOSTSET = {
        'operation': 'unexport_volume_from_hostset',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': 'test_volume',
        'volume_set_name': None,
        'host_name': None,
        'host_set_name': 'test_hostset',
        'lun': 5,
        'autolun': False,
        'node_val': 0,
        'slot': 0,
        'card_port': 1
    }

    PARAMS_FOR_EXPORT_VOLUMESET_TO_HOSTSET = {
        'operation': 'export_volumeset_to_hostset',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': None,
        'volume_set_name': 'test_volumeset',
        'host_name': None,
        'host_set_name': 'test_hostset',
        'lun': 20,
        'autolun': True,
        'node_val': None,
        'slot': None,
        'card_port': None
    }

    PARAMS_FOR_UNEXPORT_VOLUMESET_FROM_HOSTSET = {
        'operation': 'unexport_volumeset_from_hostset',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'volume_name': None,
        'volume_set_name': 'test_volumeset',
        'host_name': None,
        'host_set_name': 'test_hostset',
        'lun': 20,
        'autolun': False,
        'node_val': None,
        'slot': None,
        'card_port': None
    }

    # =========================================================================
    # Test: Export Volume to Host Operations
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volume_to_host_success(self, mock_module, mock_client):
        """
        alletramp vlun - test export volume to host success
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_host.return_value = (
            True, True, "Volume exported to host successfully", {}
        )

        vlun.main()

        mock_flowkit_client.export_volume_to_host.assert_called_with(
            'test_volume', 'test_host', 1, 0, 1, 2, False
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume exported to host successfully"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volume_to_host_with_autolun(self, mock_module, mock_client):
        """
        alletramp vlun - test export volume to host with autolun
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOST_AUTOLUN
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_host.return_value = (
            True, True, "Volume exported with autolun", {}
        )

        vlun.main()

        mock_flowkit_client.export_volume_to_host.assert_called_with(
            'test_volume', 'test_host', None, None, None, None, True
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume exported with autolun"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volume_to_host_success_with_issue(self, mock_module, mock_client):
        """
        alletramp vlun - test export volume to host success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_host.return_value = (
            True, True, "Volume exported", 
            {"lun_assigned": 1}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Volume exported", 
            issue={"lun_assigned": 1}
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volume_to_host_already_exists(self, mock_module, mock_client):
        """
        alletramp vlun - test export volume to host idempotency
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_host.return_value = (
            True, False, "VLUN already exists", {}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="VLUN already exists"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volume_to_host_failure(self, mock_module, mock_client):
        """
        alletramp vlun - test export volume to host failure
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_host.return_value = (
            False, False, "Export failed | Volume not found", {}
        )

        vlun.main()

        instance.fail_json.assert_called_with(
            msg="Export failed | Volume not found"
        )

    # =========================================================================
    # Test: Unexport Volume from Host Operations
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volume_from_host_success(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volume from host success
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUME_FROM_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volume_from_host.return_value = (
            True, True, "Volume unexported from host successfully", {}
        )

        vlun.main()

        mock_flowkit_client.unexport_volume_from_host.assert_called_with(
            'test_volume', 'test_host', 1, 0, 1, 2
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume unexported from host successfully"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volume_from_host_not_exported(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volume from host idempotency
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUME_FROM_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volume_from_host.return_value = (
            True, False, "VLUN does not exist", {}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="VLUN does not exist"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volume_from_host_failure(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volume from host failure
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUME_FROM_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volume_from_host.return_value = (
            False, False, "Unexport failed | Volume in use", {}
        )

        vlun.main()

        instance.fail_json.assert_called_with(
            msg="Unexport failed | Volume in use"
        )

    # =========================================================================
    # Test: Export Volumeset to Host Operations
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volumeset_to_host_success(self, mock_module, mock_client):
        """
        alletramp vlun - test export volumeset to host success
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUMESET_TO_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volumeset_to_host.return_value = (
            True, True, "Volume set exported to host successfully", {}
        )

        vlun.main()

        mock_flowkit_client.export_volumeset_to_host.assert_called_with(
            'test_volumeset', 'test_host', 10, 1, 2, 3, False
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume set exported to host successfully"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volumeset_to_host_already_exists(self, mock_module, mock_client):
        """
        alletramp vlun - test export volumeset to host idempotency
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUMESET_TO_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volumeset_to_host.return_value = (
            True, False, "VLUN already exists", {}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="VLUN already exists"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volumeset_to_host_failure(self, mock_module, mock_client):
        """
        alletramp vlun - test export volumeset to host failure
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUMESET_TO_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volumeset_to_host.return_value = (
            False, False, "Export failed | Volume set not found", {}
        )

        vlun.main()

        instance.fail_json.assert_called_with(
            msg="Export failed | Volume set not found"
        )

    # =========================================================================
    # Test: Unexport Volumeset from Host Operations
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volumeset_from_host_success(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volumeset from host success
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUMESET_FROM_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volumeset_from_host.return_value = (
            True, True, "Volume set unexported from host successfully", {}
        )

        vlun.main()

        mock_flowkit_client.unexport_volumeset_from_host.assert_called_with(
            'test_volumeset', 'test_host', 10, 1, 2, 3
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume set unexported from host successfully"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volumeset_from_host_not_exported(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volumeset from host idempotency
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUMESET_FROM_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volumeset_from_host.return_value = (
            True, False, "VLUN does not exist", {}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="VLUN does not exist"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volumeset_from_host_failure(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volumeset from host failure
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUMESET_FROM_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volumeset_from_host.return_value = (
            False, False, "Unexport failed", {}
        )

        vlun.main()

        instance.fail_json.assert_called_with(msg="Unexport failed")

    # =========================================================================
    # Test: Export Volume to Hostset Operations
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volume_to_hostset_success(self, mock_module, mock_client):
        """
        alletramp vlun - test export volume to hostset success
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_hostset.return_value = (
            True, True, "Volume exported to hostset successfully", {}
        )

        vlun.main()

        mock_flowkit_client.export_volume_to_hostset.assert_called_with(
            'test_volume', 'test_hostset', 5, 0, 0, 1, False
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume exported to hostset successfully"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volume_to_hostset_already_exists(self, mock_module, mock_client):
        """
        alletramp vlun - test export volume to hostset idempotency
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_hostset.return_value = (
            True, False, "VLUN already exists", {}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="VLUN already exists"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volume_to_hostset_failure(self, mock_module, mock_client):
        """
        alletramp vlun - test export volume to hostset failure
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_hostset.return_value = (
            False, False, "Export failed | Hostset not found", {}
        )

        vlun.main()

        instance.fail_json.assert_called_with(
            msg="Export failed | Hostset not found"
        )

    # =========================================================================
    # Test: Unexport Volume from Hostset Operations
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volume_from_hostset_success(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volume from hostset success
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUME_FROM_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volume_from_hostset.return_value = (
            True, True, "Volume unexported from hostset successfully", {}
        )

        vlun.main()

        mock_flowkit_client.unexport_volume_from_hostset.assert_called_with(
            'test_volume', 'test_hostset', 5, 0, 0, 1
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume unexported from hostset successfully"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volume_from_hostset_not_exported(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volume from hostset idempotency
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUME_FROM_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volume_from_hostset.return_value = (
            True, False, "VLUN does not exist", {}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="VLUN does not exist"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volume_from_hostset_failure(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volume from hostset failure
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUME_FROM_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volume_from_hostset.return_value = (
            False, False, "Unexport failed", {}
        )

        vlun.main()

        instance.fail_json.assert_called_with(msg="Unexport failed")

    # =========================================================================
    # Test: Export Volumeset to Hostset Operations
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volumeset_to_hostset_success(self, mock_module, mock_client):
        """
        alletramp vlun - test export volumeset to hostset success
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUMESET_TO_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volumeset_to_hostset.return_value = (
            True, True, "Volume set exported to hostset successfully", {}
        )

        vlun.main()

        mock_flowkit_client.export_volumeset_to_hostset.assert_called_with(
            'test_volumeset', 'test_hostset', 20, None, None, None, True
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume set exported to hostset successfully"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volumeset_to_hostset_already_exists(self, mock_module, mock_client):
        """
        alletramp vlun - test export volumeset to hostset idempotency
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUMESET_TO_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volumeset_to_hostset.return_value = (
            True, False, "VLUN already exists", {}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="VLUN already exists"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_export_volumeset_to_hostset_failure(self, mock_module, mock_client):
        """
        alletramp vlun - test export volumeset to hostset failure
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUMESET_TO_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volumeset_to_hostset.return_value = (
            False, False, "Export failed | Invalid parameters", {}
        )

        vlun.main()

        instance.fail_json.assert_called_with(
            msg="Export failed | Invalid parameters"
        )

    # =========================================================================
    # Test: Unexport Volumeset from Hostset Operations
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volumeset_from_hostset_success(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volumeset from hostset success
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUMESET_FROM_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volumeset_from_hostset.return_value = (
            True, True, "Volume set unexported from hostset successfully", {}
        )

        vlun.main()

        mock_flowkit_client.unexport_volumeset_from_hostset.assert_called_with(
            'test_volumeset', 'test_hostset', 20, None, None, None
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume set unexported from hostset successfully"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volumeset_from_hostset_not_exported(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volumeset from hostset idempotency
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUMESET_FROM_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volumeset_from_hostset.return_value = (
            True, False, "VLUN does not exist", {}
        )

        vlun.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="VLUN does not exist"
        )

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_unexport_volumeset_from_hostset_failure(self, mock_module, mock_client):
        """
        alletramp vlun - test unexport volumeset from hostset failure
        """
        mock_module.params = self.PARAMS_FOR_UNEXPORT_VOLUMESET_FROM_HOSTSET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.unexport_volumeset_from_hostset.return_value = (
            False, False, "Unexport failed", {}
        )

        vlun.main()

        instance.fail_json.assert_called_with(msg="Unexport failed")

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp vlun - test flowkit client initialization
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOST
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_host.return_value = (True, True, "Done", {})

        vlun.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_vlun.AnsibleClient')
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp vlun - test flowkit client logout called
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOST
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.export_volume_to_host.return_value = (True, True, "Done", {})

        vlun.main()

        mock_flowkit_client.logout.assert_called_once()

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_vlun.AnsibleClient', None)
    @mock.patch('modules.alletramp_vlun.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp vlun - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_EXPORT_VOLUME_TO_HOST
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            vlun.main()

        instance.fail_json.assert_called_with(
            msg='Python hpe_storage_flowkit_py package is required.'
        )


if __name__ == '__main__':
    unittest.main()
