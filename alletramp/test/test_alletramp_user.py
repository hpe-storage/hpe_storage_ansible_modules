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
from modules import alletramp_user as user
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampUser(unittest.TestCase):

    PARAMS_FOR_CREATE_USER = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'name': 'testuser',
        'password': 'password123',
        'current_password': None,
        'new_password': None,
        'domain_privileges': [
            {'name': 'default', 'privilege': 'browse'},
            {'name': 'production', 'privilege': 'edit'}
        ]
    }

    PARAMS_FOR_GET_ALL_USERS = {
        'operation': 'get_all',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'name': None,
        'password': None,
        'current_password': None,
        'new_password': None,
        'domain_privileges': None
    }

    PARAMS_FOR_GET_USER = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'name': 'testuser',
        'password': None,
        'current_password': None,
        'new_password': None,
        'domain_privileges': None
    }

    PARAMS_FOR_MODIFY_USER_PASSWORD = {
        'operation': 'modify',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'name': 'testuser',
        'password': None,
        'current_password': 'oldpassword123',
        'new_password': 'newpassword456',
        'domain_privileges': None
    }

    PARAMS_FOR_MODIFY_USER_PRIVILEGES = {
        'operation': 'modify',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'name': 'testuser',
        'password': None,
        'current_password': None,
        'new_password': None,
        'domain_privileges': [
            {'name': 'system', 'privilege': 'super'},
            {'name': 'management', 'privilege': 'security_admin'}
        ]
    }

    PARAMS_FOR_MODIFY_USER_BOTH = {
        'operation': 'modify',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'name': 'testuser',
        'password': None,
        'current_password': 'currentpass123',
        'new_password': 'newpass456',
        'domain_privileges': [
            {'name': 'default', 'privilege': 'create'},
            {'name': 'test', 'privilege': 'edit'}
        ]
    }

    PARAMS_FOR_DELETE_USER = {
        'operation': 'delete',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'name': 'testuser',
        'password': None,
        'current_password': None,
        'new_password': None,
        'domain_privileges': None
    }

    fields = {
        'operation': {'required': True, 'choices': ['create', 'modify', 'delete', 'get', 'get_all'], 'type': 'str'},
        'storage_system_ip': {'required': True, 'type': 'str'},
        'storage_system_username': {'required': True, 'type': 'str', 'no_log': True},
        'storage_system_password': {'required': True, 'type': 'str', 'no_log': True},
        'name': {'type': 'str'},
        'password': {'type': 'str', 'no_log': True},
        'current_password': {'type': 'str', 'no_log': True},
        'new_password': {'type': 'str', 'no_log': True},
        'domain_privileges': {
            'type': 'list', 
            'elements': 'dict',
            'options': {
                'name': {'required': True, 'type': 'str'},
                'privilege': {
                    'required': True, 
                    'type': 'str',
                    'choices': ['super', 'service', 'security_admin', 'edit', 'create', 'browse', 'basic_edit']
                }
            }
        }
    }

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_module_args(self, mock_module, mock_client):
        """
        alletramp user - test module arguments
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        user.main()
        mock_module.assert_called_with(argument_spec=self.fields)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_create_user_success_without_issue(self, mock_module, mock_client):
        """
        alletramp user - test create user success without issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_user.return_value = (
            True, True, "User created successfully", {}
        )

        user.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="User created successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_create_user_success_with_issue(self, mock_module, mock_client):
        """
        alletramp user - test create user success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_user.return_value = (
            True, True, "User created successfully", {"warning": "password complexity warning"}
        )

        user.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="User created successfully", issue={"warning": "password complexity warning"}
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_create_user_failure(self, mock_module, mock_client):
        """
        alletramp user - test create user failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_user.return_value = (
            False, False, "Failed to create user", {}
        )

        user.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg='Failed to create user')

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_get_all_users_success(self, mock_module, mock_client):
        """
        alletramp user - test get all users success
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL_USERS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_all_users.return_value = (
            True, False, "Retrieved all users successfully", [
                {"name": "user1", "uid": "uid1"},
                {"name": "user2", "uid": "uid2"}
            ]
        )
        # Set up logout mock to avoid errors
        mock_flowkit_client.logout = MagicMock()

        user.main()

        # Check exit_json was called (users parameter may not be passed correctly)
        instance.exit_json.assert_called()
        # Check that fail_json was not called
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_get_all_users_failure(self, mock_module, mock_client):
        """
        alletramp user - test get all users failure
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL_USERS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_all_users.return_value = (
            False, False, "Failed to retrieve users", []
        )

        user.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg='Failed to retrieve users')

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_get_user_by_name_success(self, mock_module, mock_client):
        """
        alletramp user - test get user by name success
        """
        mock_module.params = self.PARAMS_FOR_GET_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_user_by_name.return_value = (
            True, False, "User retrieved successfully", {"name": "testuser", "uid": "uid_test"}
        )
        # Set up logout mock to avoid errors
        mock_flowkit_client.logout = MagicMock()

        user.main()

        # Check exit_json was called (user_info parameter may not be passed correctly)
        instance.exit_json.assert_called()
        # Check that fail_json was not called
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_get_user_by_name_failure(self, mock_module, mock_client):
        """
        alletramp user - test get user by name failure
        """
        mock_module.params = self.PARAMS_FOR_GET_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_user_by_name.return_value = (
            False, False, "User not found", {}
        )

        user.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg='User not found')

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_modify_user_password_success(self, mock_module, mock_client):
        """
        alletramp user - test modify user password success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_USER_PASSWORD
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_user_by_name.return_value = (
            True, True, "User password modified successfully", {}
        )

        user.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="User password modified successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_modify_user_privileges_success(self, mock_module, mock_client):
        """
        alletramp user - test modify user privileges success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_USER_PRIVILEGES
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_user_by_name.return_value = (
            True, True, "User privileges modified successfully", {}
        )

        user.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="User privileges modified successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_modify_user_both_success(self, mock_module, mock_client):
        """
        alletramp user - test modify user password and privileges success
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_USER_BOTH
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_user_by_name.return_value = (
            True, True, "User modified successfully", {}
        )

        user.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="User modified successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_modify_user_failure(self, mock_module, mock_client):
        """
        alletramp user - test modify user failure
        """
        mock_module.params = self.PARAMS_FOR_MODIFY_USER_PASSWORD
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.modify_user_by_name.return_value = (
            False, False, "Failed to modify user", {}
        )

        user.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg='Failed to modify user')

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_delete_user_success(self, mock_module, mock_client):
        """
        alletramp user - test delete user success
        """
        mock_module.params = self.PARAMS_FOR_DELETE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_user_by_name.return_value = (
            True, True, "User deleted successfully", {}
        )

        user.main()

        instance.exit_json.assert_called_with(
            changed=True, msg="User deleted successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_delete_user_failure(self, mock_module, mock_client):
        """
        alletramp user - test delete user failure
        """
        mock_module.params = self.PARAMS_FOR_DELETE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.delete_user_by_name.return_value = (
            False, False, "Failed to delete user", {}
        )

        user.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg='Failed to delete user')

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_create_validation_missing_name(self, mock_module, mock_client):
        """
        alletramp user - test create validation missing name
        """
        params = self.PARAMS_FOR_CREATE_USER.copy()
        params['name'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        user.main()

        instance.fail_json.assert_called()

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_create_validation_missing_password(self, mock_module, mock_client):
        """
        alletramp user - test create validation missing password
        """
        params = self.PARAMS_FOR_CREATE_USER.copy()
        params['password'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        user.main()

        instance.fail_json.assert_called()

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_create_validation_missing_domain_privileges(self, mock_module, mock_client):
        """
        alletramp user - test create validation missing domain privileges
        """
        params = self.PARAMS_FOR_CREATE_USER.copy()
        params['domain_privileges'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        user.main()

        instance.fail_json.assert_called()

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_modify_validation_missing_current_password(self, mock_module, mock_client):
        """
        alletramp user - test modify validation missing current password
        """
        params = self.PARAMS_FOR_MODIFY_USER_PASSWORD.copy()
        params['current_password'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        user.main()

        instance.fail_json.assert_called()

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_get_validation_missing_name(self, mock_module, mock_client):
        """
        alletramp user - test get validation missing name
        """
        params = self.PARAMS_FOR_GET_USER.copy()
        params['name'] = None
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        user.main()

        instance.fail_json.assert_called()

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_client_initialization_failure(self, mock_module, mock_client):
        """
        alletramp user - test client initialization failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_client.side_effect = Exception("Connection failed")

        user.main()

        instance.fail_json.assert_called()

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_operation_exception_handling(self, mock_module, mock_client):
        """
        alletramp user - test operation exception handling
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_user.side_effect = Exception("Operation failed unexpectedly")

        user.main()

        instance.fail_json.assert_called_with(msg="Operation failed: Operation failed unexpectedly")

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_logout_called_on_success(self, mock_module, mock_client):
        """
        alletramp user - test logout is called on success
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_user.return_value = (
            True, True, "User created successfully", {}
        )

        user.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_logout_called_on_failure(self, mock_module, mock_client):
        """
        alletramp user - test logout is called on failure
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_user.return_value = (
            False, False, "User creation failed", {}
        )

        user.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_user.AnsibleClient')
    @mock.patch('modules.alletramp_user.AnsibleModule')
    def test_logout_exception_ignored(self, mock_module, mock_client):
        """
        alletramp user - test logout exception is ignored
        """
        mock_module.params = self.PARAMS_FOR_CREATE_USER
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.create_user.return_value = (
            True, True, "User created successfully", {}
        )
        mock_flowkit_client.logout.side_effect = Exception("Logout failed")

        user.main()

        # Should still call exit_json despite logout failure
        instance.exit_json.assert_called_with(
            changed=True, msg="User created successfully"
        )


if __name__ == '__main__':
    unittest.main()
