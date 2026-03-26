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
from modules import alletramp_snapshot as snapshot
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampSnapshot(unittest.TestCase):
    """
    Test suite for the alletramp_snapshot Ansible module.
    
    Tests cover Snapshot operations:
    - create
    - delete
    - modify
    - restore_offline
    - restore_online
    - create_schedule
    - modify_schedule
    - suspend_schedule
    - resume_schedule
    - delete_schedule
    """

    maxDiff = None

    # =========================================================================
    # Test Parameter Sets
    # =========================================================================

    PARAMS_FOR_CREATE_SNAPSHOT = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': 'test_snapshot',
        'base_volume_name': 'test_volume',
        'read_only': False,
        'expiration_time': 24,
        'expiration_unit': 'hours',
        'retention_time': 48,
        'retention_unit': 'hours',
        'comment': 'Test snapshot',
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': None,
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_CREATE_SNAPSHOT_MINIMAL = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': 'test_snapshot',
        'base_volume_name': 'test_volume',
        'read_only': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'comment': None,
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': None,
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_DELETE_SNAPSHOT = {
        'operation': 'delete',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': 'test_snapshot',
        'base_volume_name': None,
        'read_only': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'comment': None,
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': None,
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_MODIFY_SNAPSHOT = {
        'operation': 'modify',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': 'test_snapshot',
        'base_volume_name': None,
        'read_only': None,
        'expiration_time': 72,
        'expiration_unit': 'hours',
        'retention_time': 96,
        'retention_unit': 'hours',
        'comment': 'Modified comment',
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': 'new_snapshot_name',
        'addToSet': None,
        'rcopy': None,
        'schedule_name': None,
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_RESTORE_OFFLINE = {
        'operation': 'restore_offline',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': 'test_snapshot',
        'base_volume_name': None,
        'read_only': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'comment': None,
        'priority': 'PRIORITYTYPE_MED',
        'allow_remote_copy_parent': True,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': None,
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_RESTORE_ONLINE = {
        'operation': 'restore_online',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': 'test_snapshot',
        'base_volume_name': None,
        'read_only': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'comment': None,
        'priority': 'PRIORITYTYPE_HIGH',
        'allow_remote_copy_parent': False,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': None,
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_CREATE_SCHEDULE = {
        'operation': 'create_schedule',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': None,
        'base_volume_name': 'test_volume',
        'read_only': False,
        'expiration_time': 168,
        'expiration_unit': 'hours',
        'retention_time': 336,
        'retention_unit': 'hours',
        'comment': None,
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': None,
        'addToSet': 'snapshot_vvset',
        'rcopy': True,
        'schedule_name': 'daily_snapshot',
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '2',
        'interval': None,
        'minute': '0',
        'month': '*',
        'noalert': False,
        'norebalance': True,
        'runonce': False,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_MODIFY_SCHEDULE = {
        'operation': 'modify_schedule',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': None,
        'base_volume_name': None,
        'read_only': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'comment': None,
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': 'daily_snapshot',
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '3',
        'interval': None,
        'minute': '30',
        'month': '*',
        'noalert': True,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': 'nightly_snapshot'
    }

    PARAMS_FOR_SUSPEND_SCHEDULE = {
        'operation': 'suspend_schedule',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': None,
        'base_volume_name': None,
        'read_only': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'comment': None,
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': 'daily_snapshot',
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_RESUME_SCHEDULE = {
        'operation': 'resume_schedule',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': None,
        'base_volume_name': None,
        'read_only': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'comment': None,
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': 'daily_snapshot',
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    PARAMS_FOR_DELETE_SCHEDULE = {
        'operation': 'delete_schedule',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'snapshot_name': None,
        'base_volume_name': None,
        'read_only': None,
        'expiration_time': None,
        'expiration_unit': 'hours',
        'retention_time': None,
        'retention_unit': 'hours',
        'comment': None,
        'priority': None,
        'allow_remote_copy_parent': None,
        'new_name': None,
        'addToSet': None,
        'rcopy': None,
        'schedule_name': 'daily_snapshot',
        'dayofmonth': '*',
        'dayofweek': '*',
        'hour': '*',
        'interval': None,
        'minute': '*',
        'month': '*',
        'noalert': None,
        'norebalance': None,
        'runonce': None,
        'year': None,
        'new_schedule_name': None
    }

    # =========================================================================
    # Test: Create Snapshot Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_create_snapshot_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test create snapshot success
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_snapshot.return_value = (
            True, True, "Snapshot test_snapshot created successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.create_snapshot.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Snapshot test_snapshot created successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_create_snapshot_success_with_issue(self, mock_module, mock_client):
        """
        alletramp snapshot - test create snapshot success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.exit_json.side_effect = SystemExit(0)

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_snapshot.return_value = (
            True, True, "Snapshot created", 
            {"warning": "Snapshot created with warnings"}
        )

        with self.assertRaises(SystemExit):
            snapshot.main()

        instance.exit_json.assert_called_with(
            changed=True, 
            msg="Snapshot created", 
            issue={"warning": "Snapshot created with warnings"}
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_create_snapshot_minimal_params(self, mock_module, mock_client):
        """
        alletramp snapshot - test create snapshot with minimal parameters
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT_MINIMAL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_snapshot.return_value = (
            True, True, "Snapshot created", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(changed=True, msg="Snapshot created")

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_create_snapshot_already_exists(self, mock_module, mock_client):
        """
        alletramp snapshot - test create snapshot idempotency
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_snapshot.return_value = (
            True, False, "Snapshot already exists", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Snapshot already exists"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_create_snapshot_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test create snapshot failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_snapshot.return_value = (
            False, False, "Snapshot creation failed | Base volume not found", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Snapshot creation failed | Base volume not found"
        )

    # =========================================================================
    # Test: Delete Snapshot Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_delete_snapshot_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test delete snapshot success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_snapshot.return_value = (
            True, True, "Snapshot deleted successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.delete_snapshot.assert_called_with('test_snapshot')
        instance.exit_json.assert_called_with(
            changed=True, msg="Snapshot deleted successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_delete_snapshot_not_present(self, mock_module, mock_client):
        """
        alletramp snapshot - test delete snapshot idempotency
        """
        mock_module.params = self.PARAMS_FOR_DELETE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_snapshot.return_value = (
            True, False, "Snapshot does not exist", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Snapshot does not exist"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_delete_snapshot_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test delete snapshot failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_snapshot.return_value = (
            False, False, "Snapshot deletion failed | Snapshot in use", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Snapshot deletion failed | Snapshot in use"
        )

    # =========================================================================
    # Test: Modify Snapshot Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_modify_snapshot_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test modify snapshot success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_volume.return_value = (
            True, True, "Snapshot modified successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.modify_volume.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Snapshot modified successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_modify_snapshot_no_change(self, mock_module, mock_client):
        """
        alletramp snapshot - test modify snapshot idempotency
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_volume.return_value = (
            True, False, "No changes required", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="No changes required"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_modify_snapshot_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test modify snapshot failure
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_volume.return_value = (
            False, False, "Modify failed | Invalid parameters", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Modify failed | Invalid parameters"
        )

    # =========================================================================
    # Test: Restore Offline Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_restore_offline_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test restore offline success
        """
        mock_module.params = self.PARAMS_FOR_RESTORE_OFFLINE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.promote_snapshot_volume.return_value = (
            True, True, "Snapshot restored offline successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.promote_snapshot_volume.assert_called_once()
        # Verify online=False is passed
        call_kwargs = mock_flowkit_client.promote_snapshot_volume.call_args[1]
        self.assertEqual(call_kwargs.get('online'), False)
        instance.exit_json.assert_called_with(
            changed=True, msg="Snapshot restored offline successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_restore_offline_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test restore offline failure
        """
        mock_module.params = self.PARAMS_FOR_RESTORE_OFFLINE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.promote_snapshot_volume.return_value = (
            False, False, "Restore offline failed | Volume busy", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Restore offline failed | Volume busy"
        )

    # =========================================================================
    # Test: Restore Online Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_restore_online_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test restore online success
        """
        mock_module.params = self.PARAMS_FOR_RESTORE_ONLINE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.promote_snapshot_volume.return_value = (
            True, True, "Snapshot restored online successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.promote_snapshot_volume.assert_called_once()
        # Verify online=True is passed
        call_kwargs = mock_flowkit_client.promote_snapshot_volume.call_args[1]
        self.assertEqual(call_kwargs.get('online'), True)
        instance.exit_json.assert_called_with(
            changed=True, msg="Snapshot restored online successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_restore_online_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test restore online failure
        """
        mock_module.params = self.PARAMS_FOR_RESTORE_ONLINE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.promote_snapshot_volume.return_value = (
            False, False, "Restore online failed", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(changed=False, msg="Restore online failed")

    # =========================================================================
    # Test: Create Schedule Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_create_schedule_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test create schedule success
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_schedule.return_value = (
            True, True, "Schedule daily_snapshot created successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.create_schedule.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Schedule daily_snapshot created successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_create_schedule_already_exists(self, mock_module, mock_client):
        """
        alletramp snapshot - test create schedule idempotency
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_schedule.return_value = (
            True, False, "Schedule already exists", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Schedule already exists"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_create_schedule_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test create schedule failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_schedule.return_value = (
            False, False, "Schedule creation failed | Invalid time format", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Schedule creation failed | Invalid time format"
        )

    # =========================================================================
    # Test: Modify Schedule Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_modify_schedule_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test modify schedule success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_schedule.return_value = (
            True, True, "Schedule modified successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.modify_schedule.assert_called_once()
        instance.exit_json.assert_called_with(
            changed=True, msg="Schedule modified successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_modify_schedule_no_change(self, mock_module, mock_client):
        """
        alletramp snapshot - test modify schedule idempotency
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_schedule.return_value = (
            True, False, "No changes required", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="No changes required"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_modify_schedule_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test modify schedule failure
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_schedule.return_value = (
            False, False, "Modify schedule failed | Schedule not found", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Modify schedule failed | Schedule not found"
        )

    # =========================================================================
    # Test: Suspend Schedule Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_suspend_schedule_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test suspend schedule success
        """
        mock_module.params = self.PARAMS_FOR_SUSPEND_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.suspend_schedule.return_value = (
            True, True, "Schedule suspended successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.suspend_schedule.assert_called_with('daily_snapshot')
        instance.exit_json.assert_called_with(
            changed=True, msg="Schedule suspended successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_suspend_schedule_already_suspended(self, mock_module, mock_client):
        """
        alletramp snapshot - test suspend schedule idempotency
        """
        mock_module.params = self.PARAMS_FOR_SUSPEND_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.suspend_schedule.return_value = (
            True, False, "Schedule already suspended", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Schedule already suspended"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_suspend_schedule_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test suspend schedule failure
        """
        mock_module.params = self.PARAMS_FOR_SUSPEND_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.suspend_schedule.return_value = (
            False, False, "Suspend schedule failed | Schedule not found", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Suspend schedule failed | Schedule not found"
        )

    # =========================================================================
    # Test: Resume Schedule Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_resume_schedule_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test resume schedule success
        """
        mock_module.params = self.PARAMS_FOR_RESUME_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.resume_schedule.return_value = (
            True, True, "Schedule resumed successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.resume_schedule.assert_called_with('daily_snapshot')
        instance.exit_json.assert_called_with(
            changed=True, msg="Schedule resumed successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_resume_schedule_already_active(self, mock_module, mock_client):
        """
        alletramp snapshot - test resume schedule idempotency
        """
        mock_module.params = self.PARAMS_FOR_RESUME_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.resume_schedule.return_value = (
            True, False, "Schedule already active", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Schedule already active"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_resume_schedule_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test resume schedule failure
        """
        mock_module.params = self.PARAMS_FOR_RESUME_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.resume_schedule.return_value = (
            False, False, "Resume schedule failed", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(changed=False, msg="Resume schedule failed")

    # =========================================================================
    # Test: Delete Schedule Operations
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_delete_schedule_success(self, mock_module, mock_client):
        """
        alletramp snapshot - test delete schedule success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_schedule.return_value = (
            True, True, "Schedule deleted successfully", {}
        )

        snapshot.main()

        mock_flowkit_client.delete_schedule.assert_called_with('daily_snapshot')
        instance.exit_json.assert_called_with(
            changed=True, msg="Schedule deleted successfully"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_delete_schedule_not_found(self, mock_module, mock_client):
        """
        alletramp snapshot - test delete schedule idempotency
        """
        mock_module.params = self.PARAMS_FOR_DELETE_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_schedule.return_value = (
            True, False, "Schedule does not exist", {}
        )

        snapshot.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="Schedule does not exist"
        )

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_delete_schedule_failure(self, mock_module, mock_client):
        """
        alletramp snapshot - test delete schedule failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_SCHEDULE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_schedule.return_value = (
            False, False, "Delete schedule failed | In use", {}
        )

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Delete schedule failed | In use"
        )

    # =========================================================================
    # Test: Exception Handling
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_exception_handling(self, mock_module, mock_client):
        """
        alletramp snapshot - test exception handling
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_snapshot.side_effect = Exception("Connection error")

        snapshot.main()

        instance.fail_json.assert_called_with(
            changed=False, msg="Exception occurred: Connection error"
        )

    # =========================================================================
    # Test: Flowkit Client Initialization and Logout
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_flowkit_client_initialization(self, mock_module, mock_client):
        """
        alletramp snapshot - test flowkit client initialization
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_snapshot.return_value = (True, True, "Created", {})

        snapshot.main()

        mock_client.assert_called_with('192.168.0.1', 'admin', 'password')

    @mock.patch('modules.alletramp_snapshot.AnsibleClient')
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_flowkit_client_logout_called(self, mock_module, mock_client):
        """
        alletramp snapshot - test flowkit client logout called
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT
        mock_module.return_value = mock_module

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_snapshot.return_value = (True, True, "Created", {})

        snapshot.main()

        mock_flowkit_client.logout.assert_called_once()

    # =========================================================================
    # Test: Missing Flowkit Package
    # =========================================================================

    @mock.patch('modules.alletramp_snapshot.AnsibleClient', None)
    @mock.patch('modules.alletramp_snapshot.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        """
        alletramp snapshot - test error when flowkit package is not installed
        """
        mock_module.params = self.PARAMS_FOR_CREATE_SNAPSHOT
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            snapshot.main()

        instance.fail_json.assert_called_with(
            msg='the python hpe_storage_flowkit_py module is required'
        )


if __name__ == '__main__':
    unittest.main()
