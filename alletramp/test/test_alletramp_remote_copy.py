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
from modules import alletramp_remote_copy as remote_copy
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampRemoteCopy(unittest.TestCase):
    """
    Test suite for the alletramp_remote_copy Ansible module.
    
    Tests cover Remote Copy operations:
    - create
    - delete
    - modify
    - add_volume
    - remove_volume
    - start
    - stop
    - synchronize
    - admit_link
    - dismiss_link
    - admit_target
    - dismiss_target
    - start_rcopy
    - remote_copy_status
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    BASE_PARAMS = {
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'remote_copy_group_name': 'test_rcg',
        'domain': None,
        'remote_copy_targets': None,
        'modify_targets': None,
        'admit_volume_targets': None,
        'local_user_cpg': None,
        'local_snap_cpg': None,
        'keep_snap': False,
        'unset_user_cpg': False,
        'unset_snap_cpg': False,
        'snapshot_name': None,
        'volume_auto_creation': False,
        'skip_initial_sync': False,
        'different_secondary_wwn': False,
        'remove_secondary_volume': False,
        'target_name': None,
        'starting_snapshots': None,
        'no_snapshot': False,
        'no_resync_snapshot': False,
        'full_sync': False,
        'stop_groups': False,
        'volume_name': None,
        'source_port': None,
        'target_port_wwn_or_ip': None,
        'target_mode': None,
        'local_remote_volume_pair_list': []
    }

    PARAMS_FOR_CREATE = {
        **BASE_PARAMS,
        'operation': 'create',
        'domain': 'test_domain',
        'remote_copy_targets': [
            {'target_name': 'target1', 'target_mode': 'sync', 'user_cpg': 'cpg1', 'snap_cpg': 'cpg2'}
        ],
        'local_user_cpg': 'local_cpg',
        'local_snap_cpg': 'local_snap_cpg'
    }

    PARAMS_FOR_DELETE = {
        **BASE_PARAMS,
        'operation': 'delete',
        'keep_snap': True
    }

    PARAMS_FOR_MODIFY = {
        **BASE_PARAMS,
        'operation': 'modify',
        'local_user_cpg': 'new_cpg',
        'local_snap_cpg': 'new_snap_cpg',
        'modify_targets': [
            {'target_name': 'target1', 'sync_period': 300}
        ],
        'unset_user_cpg': False,
        'unset_snap_cpg': False
    }

    PARAMS_FOR_ADD_VOLUME = {
        **BASE_PARAMS,
        'operation': 'add_volume',
        'volume_name': 'test_volume',
        'admit_volume_targets': [
            {'target_name': 'target1', 'sec_volume_name': 'sec_vol1'}
        ],
        'snapshot_name': None,
        'volume_auto_creation': True,
        'skip_initial_sync': False,
        'different_secondary_wwn': False
    }

    PARAMS_FOR_REMOVE_VOLUME = {
        **BASE_PARAMS,
        'operation': 'remove_volume',
        'volume_name': 'test_volume',
        'keep_snap': True,
        'remove_secondary_volume': False
    }

    PARAMS_FOR_START = {
        **BASE_PARAMS,
        'operation': 'start',
        'skip_initial_sync': True,
        'target_name': 'target1',
        'starting_snapshots': ['snap1', 'snap2']
    }

    PARAMS_FOR_STOP = {
        **BASE_PARAMS,
        'operation': 'stop',
        'no_snapshot': True,
        'target_name': 'target1'
    }

    PARAMS_FOR_SYNCHRONIZE = {
        **BASE_PARAMS,
        'operation': 'synchronize',
        'no_resync_snapshot': False,
        'target_name': 'target1',
        'full_sync': True
    }

    PARAMS_FOR_ADMIT_LINK = {
        **BASE_PARAMS,
        'operation': 'admit_link',
        'target_name': 'target1',
        'source_port': '0:1:2',
        'target_port_wwn_or_ip': '192.168.1.100'
    }

    PARAMS_FOR_DISMISS_LINK = {
        **BASE_PARAMS,
        'operation': 'dismiss_link',
        'target_name': 'target1',
        'source_port': '0:1:2',
        'target_port_wwn_or_ip': '192.168.1.100'
    }

    PARAMS_FOR_ADMIT_TARGET = {
        **BASE_PARAMS,
        'operation': 'admit_target',
        'target_name': 'target1',
        'target_mode': 'sync',
        'local_remote_volume_pair_list': [
            {'sourceVolumeName': 'vol1', 'targetVolumeName': 'sec_vol1'}
        ]
    }

    PARAMS_FOR_DISMISS_TARGET = {
        **BASE_PARAMS,
        'operation': 'dismiss_target',
        'target_name': 'target1'
    }

    PARAMS_FOR_START_RCOPY = {
        **BASE_PARAMS,
        'operation': 'start_rcopy'
    }

    PARAMS_FOR_REMOTE_COPY_STATUS = {
        **BASE_PARAMS,
        'operation': 'remote_copy_status'
    }

    # =========================================================================
    # Test: Create Remote Copy Group Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_create_rcg_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test create remote copy group success
        """
        mock_module.params = self.PARAMS_FOR_CREATE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_remote_copy_group.return_value = (
            True, True, "Remote Copy group test_rcg created successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.create_remote_copy_group.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy group test_rcg created successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_create_rcg_success_with_output(self, mock_module, mock_client):
        """
        alletramp remote copy - test create rcg success with output data
        """
        mock_module.params = self.PARAMS_FOR_CREATE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        output_data = {"groupId": 12345}
        mock_flowkit_client.create_remote_copy_group.return_value = (
            True, True, "RCG created", output_data
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="RCG created", output=output_data
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_create_rcg_already_exists(self, mock_module, mock_client):
        """
        alletramp remote copy - test create rcg idempotency
        """
        mock_module.params = self.PARAMS_FOR_CREATE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_remote_copy_group.return_value = (
            True, False, "Remote Copy group already exists", {}
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Remote Copy group already exists"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_create_rcg_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test create rcg failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_remote_copy_group.return_value = (
            False, False, "Create RCG failed | Target not reachable", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Create RCG failed | Target not reachable"
        )

    # =========================================================================
    # Test: Delete Remote Copy Group Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_delete_rcg_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test delete rcg success
        """
        mock_module.params = self.PARAMS_FOR_DELETE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_remote_copy_group.return_value = (
            True, True, "Remote Copy group deleted successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.delete_remote_copy_group.assert_called_with('test_rcg', True)
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy group deleted successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_delete_rcg_not_exists(self, mock_module, mock_client):
        """
        alletramp remote copy - test delete rcg idempotency
        """
        mock_module.params = self.PARAMS_FOR_DELETE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_remote_copy_group.return_value = (
            True, False, "RCG does not exist", {}
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="RCG does not exist"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_delete_rcg_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test delete rcg failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_remote_copy_group.return_value = (
            False, False, "Delete RCG failed | Group is active", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Delete RCG failed | Group is active"
        )

    # =========================================================================
    # Test: Modify Remote Copy Group Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_modify_rcg_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test modify rcg success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_remote_copy_group.return_value = (
            True, True, "Remote Copy group modified successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.modify_remote_copy_group.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy group modified successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_modify_rcg_no_change(self, mock_module, mock_client):
        """
        alletramp remote copy - test modify rcg idempotency
        """
        mock_module.params = self.PARAMS_FOR_MODIFY
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_remote_copy_group.return_value = (
            True, False, "No changes required", {}
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="No changes required"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_modify_rcg_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test modify rcg failure
        """
        mock_module.params = self.PARAMS_FOR_MODIFY
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_remote_copy_group.return_value = (
            False, False, "Modify RCG failed | Invalid parameters", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Modify RCG failed | Invalid parameters"
        )

    # =========================================================================
    # Test: Add Volume to Remote Copy Group Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_add_volume_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test add volume success
        """
        mock_module.params = self.PARAMS_FOR_ADD_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_volume_to_remote_copy_group.return_value = (
            True, True, "Volume added to RCG successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.add_volume_to_remote_copy_group.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume added to RCG successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_add_volume_already_in_group(self, mock_module, mock_client):
        """
        alletramp remote copy - test add volume idempotency
        """
        mock_module.params = self.PARAMS_FOR_ADD_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_volume_to_remote_copy_group.return_value = (
            True, False, "Volume already in group", {}
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Volume already in group"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_add_volume_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test add volume failure
        """
        mock_module.params = self.PARAMS_FOR_ADD_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.add_volume_to_remote_copy_group.return_value = (
            False, False, "Add volume failed | Volume not found", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Add volume failed | Volume not found"
        )

    # =========================================================================
    # Test: Remove Volume from Remote Copy Group Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_remove_volume_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test remove volume success
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_volume_from_remote_copy_group.return_value = (
            True, True, "Volume removed from RCG successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.remove_volume_from_remote_copy_group.assert_called_with(
            'test_rcg', 'test_volume', True, False
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Volume removed from RCG successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_remove_volume_not_in_group(self, mock_module, mock_client):
        """
        alletramp remote copy - test remove volume idempotency
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_volume_from_remote_copy_group.return_value = (
            True, False, "Volume not in group", {}
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Volume not in group"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_remove_volume_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test remove volume failure
        """
        mock_module.params = self.PARAMS_FOR_REMOVE_VOLUME
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remove_volume_from_remote_copy_group.return_value = (
            False, False, "Remove volume failed", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(msg="Remove volume failed")

    # =========================================================================
    # Test: Start Remote Copy Group Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_start_rcg_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test start rcg success
        """
        mock_module.params = self.PARAMS_FOR_START
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.start_remote_copy_group.return_value = (
            True, True, "Remote Copy group started successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.start_remote_copy_group.assert_called_with(
            'test_rcg', True, 'target1', ['snap1', 'snap2']
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy group started successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_start_rcg_already_running(self, mock_module, mock_client):
        """
        alletramp remote copy - test start rcg idempotency
        """
        mock_module.params = self.PARAMS_FOR_START
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.start_remote_copy_group.return_value = (
            True, False, "RCG already running", {}
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="RCG already running"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_start_rcg_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test start rcg failure
        """
        mock_module.params = self.PARAMS_FOR_START
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.start_remote_copy_group.return_value = (
            False, False, "Start RCG failed | Target unreachable", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Start RCG failed | Target unreachable"
        )

    # =========================================================================
    # Test: Stop Remote Copy Group Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_stop_rcg_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test stop rcg success
        """
        mock_module.params = self.PARAMS_FOR_STOP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.stop_remote_copy_group.return_value = (
            True, True, "Remote Copy group stopped successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.stop_remote_copy_group.assert_called_with(
            'test_rcg', True, 'target1'
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy group stopped successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_stop_rcg_already_stopped(self, mock_module, mock_client):
        """
        alletramp remote copy - test stop rcg idempotency
        """
        mock_module.params = self.PARAMS_FOR_STOP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.stop_remote_copy_group.return_value = (
            True, False, "RCG already stopped", {}
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="RCG already stopped"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_stop_rcg_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test stop rcg failure
        """
        mock_module.params = self.PARAMS_FOR_STOP
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.stop_remote_copy_group.return_value = (
            False, False, "Stop RCG failed", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(msg="Stop RCG failed")

    # =========================================================================
    # Test: Synchronize Remote Copy Group Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_synchronize_rcg_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test synchronize rcg success
        """
        mock_module.params = self.PARAMS_FOR_SYNCHRONIZE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.synchronize_remote_copy_group.return_value = (
            True, True, "Remote Copy group synchronized successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.synchronize_remote_copy_group.assert_called_with(
            'test_rcg', False, 'target1', True
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy group synchronized successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_synchronize_rcg_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test synchronize rcg failure
        """
        mock_module.params = self.PARAMS_FOR_SYNCHRONIZE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.synchronize_remote_copy_group.return_value = (
            False, False, "Synchronize RCG failed | Group not started", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Synchronize RCG failed | Group not started"
        )

    # =========================================================================
    # Test: Admit Link Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_admit_link_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test admit link success
        """
        mock_module.params = self.PARAMS_FOR_ADMIT_LINK
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.admit_remote_copy_links.return_value = (
            True, True, "Remote Copy link admitted successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.admit_remote_copy_links.assert_called_with(
            'target1', '0:1:2', '192.168.1.100'
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy link admitted successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_admit_link_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test admit link failure
        """
        mock_module.params = self.PARAMS_FOR_ADMIT_LINK
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.admit_remote_copy_links.return_value = (
            False, False, "Admit link failed | Port not found", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Admit link failed | Port not found"
        )

    # =========================================================================
    # Test: Dismiss Link Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_dismiss_link_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test dismiss link success
        """
        mock_module.params = self.PARAMS_FOR_DISMISS_LINK
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.dismiss_remote_copy_links.return_value = (
            True, True, "Remote Copy link dismissed successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.dismiss_remote_copy_links.assert_called_with(
            'target1', '0:1:2', '192.168.1.100'
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy link dismissed successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_dismiss_link_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test dismiss link failure
        """
        mock_module.params = self.PARAMS_FOR_DISMISS_LINK
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.dismiss_remote_copy_links.return_value = (
            False, False, "Dismiss link failed", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(msg="Dismiss link failed")

    # =========================================================================
    # Test: Admit Target Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_admit_target_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test admit target success
        """
        mock_module.params = self.PARAMS_FOR_ADMIT_TARGET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.admit_remote_copy_target.return_value = (
            True, True, "Remote Copy target admitted successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.admit_remote_copy_target.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy target admitted successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_admit_target_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test admit target failure
        """
        mock_module.params = self.PARAMS_FOR_ADMIT_TARGET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.admit_remote_copy_target.return_value = (
            False, False, "Admit target failed | Target not configured", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Admit target failed | Target not configured"
        )

    # =========================================================================
    # Test: Dismiss Target Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_dismiss_target_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test dismiss target success
        """
        mock_module.params = self.PARAMS_FOR_DISMISS_TARGET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.dismiss_remote_copy_target.return_value = (
            True, True, "Remote Copy target dismissed successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.dismiss_remote_copy_target.assert_called_with(
            'test_rcg', 'target1'
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy target dismissed successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_dismiss_target_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test dismiss target failure
        """
        mock_module.params = self.PARAMS_FOR_DISMISS_TARGET
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.dismiss_remote_copy_target.return_value = (
            False, False, "Dismiss target failed", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(msg="Dismiss target failed")

    # =========================================================================
    # Test: Start Remote Copy Service Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_start_rcopy_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test start rcopy service success
        """
        mock_module.params = self.PARAMS_FOR_START_RCOPY
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.start_remote_copy_service.return_value = (
            True, True, "Remote Copy service started successfully", {}
        )

        remote_copy.main()

        mock_flowkit_client.start_remote_copy_service.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Remote Copy service started successfully"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_start_rcopy_already_running(self, mock_module, mock_client):
        """
        alletramp remote copy - test start rcopy service idempotency
        """
        mock_module.params = self.PARAMS_FOR_START_RCOPY
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.start_remote_copy_service.return_value = (
            True, False, "Remote Copy service already running", {}
        )

        remote_copy.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Remote Copy service already running"
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_start_rcopy_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test start rcopy service failure
        """
        mock_module.params = self.PARAMS_FOR_START_RCOPY
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.start_remote_copy_service.return_value = (
            False, False, "Start rcopy service failed", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(msg="Start rcopy service failed")

    # =========================================================================
    # Test: Remote Copy Status Operations
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_remote_copy_status_success(self, mock_module, mock_client):
        """
        alletramp remote copy - test remote copy status success
        """
        mock_module.params = self.PARAMS_FOR_REMOTE_COPY_STATUS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        status_info = {"state": "started", "syncStatus": "synced"}
        mock_flowkit_client.remote_copy_group_status_check.return_value = (
            True, False, "Remote Copy group status retrieved", status_info
        )

        remote_copy.main()

        mock_flowkit_client.remote_copy_group_status_check.assert_called_with('test_rcg')
        instance.exit_json.assert_called_with(
            changed=False, 
            msg="Remote Copy group status retrieved",
            output=status_info
        )

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_remote_copy_status_failure(self, mock_module, mock_client):
        """
        alletramp remote copy - test remote copy status failure
        """
        mock_module.params = self.PARAMS_FOR_REMOTE_COPY_STATUS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.remote_copy_group_status_check.return_value = (
            False, False, "Status check failed | Group not found", {}
        )

        remote_copy.main()

        instance.fail_json.assert_called_with(
            msg="Status check failed | Group not found"
        )

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp remote copy - test flowkit client initialization
        """
        mock_module.params = self.PARAMS_FOR_CREATE
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_remote_copy_group.return_value = (True, True, "Done", {})

        remote_copy.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient')
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp remote copy - test flowkit client logout called
        """
        mock_module.params = self.PARAMS_FOR_CREATE
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_remote_copy_group.return_value = (True, True, "Done", {})

        remote_copy.main()

        mock_flowkit_client.logout.assert_called_once()

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_remote_copy.AnsibleClient', None)
    @mock.patch('modules.alletramp_remote_copy.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp remote copy - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            remote_copy.main()

        instance.fail_json.assert_called_with(
            msg='Python hpe_storage_flowkit_py package is required.'
        )


if __name__ == '__main__':
    unittest.main()
