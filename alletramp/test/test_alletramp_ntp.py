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
from modules import alletramp_ntp as ntp
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampNtp(unittest.TestCase):

    PARAMS_FOR_CONFIGURE_DATETIME = {
        'operation': 'configure_datetime', 
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin', 
        'storage_system_password': 'password',
        'date_time': '01/06/2026 10:30:00', 
        'ntp_addresses': None,
        'timezone': 'Asia/Kolkata'
    }

    PARAMS_FOR_NTP_ADDRESSES = {
        'operation': 'configure_datetime', 
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin', 
        'storage_system_password': 'password',
        'date_time': None, 
        'ntp_addresses': ['pool.ntp.org', 'time.google.com'],
        'timezone': 'Asia/Kolkata'
    }

    fields = {
        'operation': {'required': True, 'choices': ['configure_datetime'], 'type': 'str'},
        'storage_system_ip': {'required': True, 'type': 'str'},
        'storage_system_username': {'required': True, 'type': 'str', 'no_log': True},
        'storage_system_password': {'required': True, 'type': 'str', 'no_log': True},
        'date_time': {'type': 'str'},
        'ntp_addresses': {'type': 'list'},
        'timezone': {'required': True, 'type': 'str'}
    }

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_module_args(self, mock_module, mock_client):
        """
        alletramp ntp - test module arguments
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            True, True, "Success", {}
        )
        
        ntp.main()
        mock_module.assert_called_with(argument_spec=self.fields)

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_main_exit_functionality_success_without_issue_attr_dict(self, mock_module, mock_client):
        """
        alletramp ntp - success check without issue dict
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            True, True, "Successfully configured datetime settings", {}
        )
        
        ntp.main()
        
        instance.exit_json.assert_called_with(
            changed=True, msg="Successfully configured datetime settings"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_main_exit_functionality_success_with_issue_attr_dict(self, mock_module, mock_client):
        """
        alletramp ntp - success check with issue dict
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            True, True, "Successfully configured datetime settings", {"warning": "timezone changed"}
        )
        
        ntp.main()
        
        instance.exit_json.assert_called_with(
            changed=True, msg="Successfully configured datetime settings", issue={"warning": "timezone changed"}
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_main_exit_functionality_fail(self, mock_module, mock_client):
        """
        alletramp ntp - exit fail check
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            False, False, "Failed to configure datetime settings", {}
        )
        
        ntp.main()
        
        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg='Failed to configure datetime settings')

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_mutual_exclusivity_both_parameters(self, mock_module, mock_client):
        """
        alletramp ntp - test mutual exclusivity validation (both date_time and ntp_addresses)
        """
        params = self.PARAMS_FOR_CONFIGURE_DATETIME.copy()
        params['ntp_addresses'] = ['pool.ntp.org']
        
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)
        
        with self.assertRaises(SystemExit):
            ntp.main()
        
        instance.fail_json.assert_called_with(
            msg="Cannot specify both date_time and ntp_addresses. Provide either one or the other."
        )

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_mutual_exclusivity_neither_parameter(self, mock_module, mock_client):
        """
        alletramp ntp - test mutual exclusivity validation (neither date_time nor ntp_addresses)
        """
        params = self.PARAMS_FOR_CONFIGURE_DATETIME.copy()
        params['date_time'] = None
        params['ntp_addresses'] = None
        
        mock_module.params = params
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)
        
        with self.assertRaises(SystemExit):
            ntp.main()
        
        instance.fail_json.assert_called_with(
            msg="Must specify either date_time or ntp_addresses (but not both)."
        )

    @mock.patch('modules.alletramp_ntp.AnsibleClient', None)
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_flowkit_import_failure(self, mock_module):
        """
        alletramp ntp - test flowkit import failure
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)
        
        with self.assertRaises(SystemExit):
            ntp.main()
        
        instance.fail_json.assert_called_with(
            msg='Python hpe_storage_flowkit_py package is required.'
        )

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_configure_datetime_with_ntp_addresses(self, mock_module, mock_client):
        """
        alletramp ntp - test configure datetime with NTP addresses
        """
        mock_module.params = self.PARAMS_FOR_NTP_ADDRESSES
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            True, True, "Successfully configured NTP addresses", {}
        )
        
        ntp.main()
        
        mock_flowkit_client.configure_datetime.assert_called_with(
            None, ['pool.ntp.org', 'time.google.com'], 'Asia/Kolkata'
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Successfully configured NTP addresses"
        )

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_configure_datetime_with_date_time(self, mock_module, mock_client):
        """
        alletramp ntp - test configure datetime with specific date/time
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            True, True, "Successfully configured datetime", {}
        )
        
        ntp.main()
        
        mock_flowkit_client.configure_datetime.assert_called_with(
            '01/06/2026 10:30:00', None, 'Asia/Kolkata'
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Successfully configured datetime"
        )

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_client_initialization_exception(self, mock_module, mock_client):
        """
        alletramp ntp - test client initialization exception
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)
        
        mock_client.side_effect = Exception("Failed to initialize client")
        
        with self.assertRaises(SystemExit):
            ntp.main()
        
        instance.fail_json.assert_called_with(
            msg="Failed to initialize client"
        )

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_configure_datetime_exception(self, mock_module, mock_client):
        """
        alletramp ntp - test configure datetime method exception
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.side_effect = Exception("API call failed")
        
        with self.assertRaises(SystemExit):
            ntp.main()
        
        instance.fail_json.assert_called_with(msg="API call failed")

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_logout_called_on_success(self, mock_module, mock_client):
        """
        alletramp ntp - test that logout is called on successful execution
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            True, True, "Successfully configured datetime", {}
        )
        
        ntp.main()
        
        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_logout_called_on_failure(self, mock_module, mock_client):
        """
        alletramp ntp - test that logout is called even on failure
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            False, False, "Configuration failed", {}
        )
        
        ntp.main()
        
        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_ntp.AnsibleClient')
    @mock.patch('modules.alletramp_ntp.AnsibleModule')
    def test_logout_exception_ignored(self, mock_module, mock_client):
        """
        alletramp ntp - test that logout exceptions are ignored
        """
        mock_module.params = self.PARAMS_FOR_CONFIGURE_DATETIME
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        
        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.configure_datetime.return_value = (
            True, True, "Successfully configured datetime", {}
        )
        mock_flowkit_client.logout.side_effect = Exception("Logout failed")
        
        ntp.main()
        
        instance.exit_json.assert_called_with(
            changed=True, msg="Successfully configured datetime"
        )


if __name__ == '__main__':
    unittest.main(exit=False)
