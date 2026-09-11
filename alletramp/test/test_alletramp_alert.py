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
from modules import alletramp_alert as alert
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampAlert(unittest.TestCase):

    PARAMS_FOR_GET_ALL = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': None,
        'severity': None,
        'alert_status': None,
        'last_days': None,
        'last_hours': None,
        'test_message': None
    }

    PARAMS_FOR_GET_FILTERED_BY_TYPE = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': 'TYPE_CUSTOMER',
        'severity': None,
        'alert_status': None,
        'last_days': None,
        'last_hours': None,
        'test_message': None
    }

    PARAMS_FOR_GET_FILTERED_BY_SEVERITY = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': None,
        'severity': 'SEVERITY_CRITICAL',
        'alert_status': None,
        'last_days': None,
        'last_hours': None,
        'test_message': None
    }

    PARAMS_FOR_GET_FILTERED_BY_STATUS = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': None,
        'severity': None,
        'alert_status': 'STATUS_NEW',
        'last_days': None,
        'last_hours': None,
        'test_message': None
    }

    PARAMS_FOR_GET_FILTERED_BY_LAST_DAYS = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': None,
        'severity': None,
        'alert_status': None,
        'last_days': 3.0,
        'last_hours': None,
        'test_message': None
    }

    PARAMS_FOR_GET_FILTERED_BY_LAST_HOURS = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': None,
        'severity': None,
        'alert_status': None,
        'last_days': None,
        'last_hours': 12.0,
        'test_message': None
    }

    PARAMS_FOR_GET_FILTERED_COMBINED = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': 'TYPE_CUSTOMER',
        'severity': 'SEVERITY_CRITICAL',
        'alert_status': 'STATUS_NEW',
        'last_days': 2.0,
        'last_hours': None,
        'test_message': None
    }

    PARAMS_FOR_TEST_ALERT = {
        'operation': 'test_alert',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': None,
        'severity': None,
        'alert_status': None,
        'last_days': None,
        'last_hours': None,
        'test_message': 'Test alert from Ansible'
    }

    PARAMS_FOR_TEST_ALERT_NO_MESSAGE = {
        'operation': 'test_alert',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': None,
        'severity': None,
        'alert_status': None,
        'last_days': None,
        'last_hours': None,
        'test_message': None
    }

    fields = {
        'operation': {
            'required': True,
            'choices': ['get', 'test_alert'],
            'type': 'str'
        },
        'storage_system_ip': {'required': True, 'type': 'str'},
        'storage_system_username': {'required': True, 'type': 'str', 'no_log': True},
        'storage_system_password': {'required': True, 'type': 'str', 'no_log': True},
        'alert_type': {
            'type': 'str',
            'choices': ['TYPE_UNKNOWN', 'TYPE_CUSTOMER', 'TYPE_SERVICE', 'TYPE_APPLICATION']
        },
        'severity': {
            'type': 'str',
            'choices': [
                'SEVERITY_UNKNOWN', 'SEVERITY_FATAL', 'SEVERITY_CRITICAL',
                'SEVERITY_MAJOR', 'SEVERITY_MINOR', 'SEVERITY_DEGRADED',
                'SEVERITY_INFO', 'SEVERITY_DEBUG'
            ]
        },
        'alert_status': {
            'type': 'str',
            'choices': [
                'STATUS_UNKNOWN', 'STATUS_NEW', 'STATUS_ACKNOWLEDGED',
                'STATUS_FIXED', 'STATUS_REMOVED', 'STATUS_AUTOFIXED'
            ]
        },
        'last_days': {'type': 'float'},
        'last_hours': {'type': 'float'},
        'test_message': {'type': 'str'}
    }

    # ---- Module arguments test ----

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_module_args(self, mock_module, mock_client):
        """
        alletramp alert - test module arguments
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        alert.main()
        mock_module.assert_called_with(
            argument_spec=self.fields,
            mutually_exclusive=[['last_days', 'last_hours']]
        )

    # ---- get_all operation tests ----

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_all_success_without_issue_dict(self, mock_module, mock_client):
        """
        alletramp alert - get_all success without issue dict
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "All alerts retrieved successfully", {}
        )

        alert.main()

        mock_flowkit_client.get_alerts.assert_called_once_with(
            alert_type=None,
            severity=None,
            status=None,
            last_days=None,
            last_hours=None
        )
        instance.exit_json.assert_called_with(
            changed=False, msg="All alerts retrieved successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_all_success_with_issue_dict(self, mock_module, mock_client):
        """
        alletramp alert - get_all success with issue dict
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "All alerts retrieved successfully",
            {"response": [{"uid": "a1", "status": "STATUS_NEW"}]}
        )

        alert.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="All alerts retrieved successfully",
            issue={"response": [{"uid": "a1", "status": "STATUS_NEW"}]}
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_all_fail(self, mock_module, mock_client):
        """
        alletramp alert - get_all failure
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            False, False, "Failed to get all alerts | 500 Error", {}
        )

        alert.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Failed to get all alerts | 500 Error")

    # ---- get_filtered operation tests ----

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_by_type_success(self, mock_module, mock_client):
        """
        alletramp alert - get_filtered by type success
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_BY_TYPE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "Filtered alerts retrieved successfully (3 matches)", {}
        )

        alert.main()

        mock_flowkit_client.get_alerts.assert_called_once_with(
            alert_type='TYPE_CUSTOMER',
            severity=None,
            status=None,
            last_days=None,
            last_hours=None
        )
        instance.exit_json.assert_called_with(
            changed=False, msg="Filtered alerts retrieved successfully (3 matches)"
        )

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_by_severity_success(self, mock_module, mock_client):
        """
        alletramp alert - get_filtered by severity success
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_BY_SEVERITY
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "Filtered alerts retrieved successfully (2 matches)", {}
        )

        alert.main()

        mock_flowkit_client.get_alerts.assert_called_once_with(
            alert_type=None,
            severity='SEVERITY_CRITICAL',
            status=None,
            last_days=None,
            last_hours=None
        )

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_by_status_success(self, mock_module, mock_client):
        """
        alletramp alert - get_filtered by status success
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_BY_STATUS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "Filtered alerts retrieved successfully (5 matches)", {}
        )

        alert.main()

        mock_flowkit_client.get_alerts.assert_called_once_with(
            alert_type=None,
            severity=None,
            status='STATUS_NEW',
            last_days=None,
            last_hours=None
        )

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_by_last_days_success(self, mock_module, mock_client):
        """
        alletramp alert - get_filtered by last_days success
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_BY_LAST_DAYS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "Filtered alerts retrieved successfully (4 matches)", {}
        )

        alert.main()

        mock_flowkit_client.get_alerts.assert_called_once_with(
            alert_type=None,
            severity=None,
            status=None,
            last_days=3.0,
            last_hours=None
        )

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_by_last_hours_success(self, mock_module, mock_client):
        """
        alletramp alert - get_filtered by last_hours success
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_BY_LAST_HOURS
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "Filtered alerts retrieved successfully (1 matches)", {}
        )

        alert.main()

        mock_flowkit_client.get_alerts.assert_called_once_with(
            alert_type=None,
            severity=None,
            status=None,
            last_days=None,
            last_hours=12.0
        )

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_combined_filters_success(self, mock_module, mock_client):
        """
        alletramp alert - get_filtered with combined filters success
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_COMBINED
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "Filtered alerts retrieved successfully (1 matches)", {}
        )

        alert.main()

        mock_flowkit_client.get_alerts.assert_called_once_with(
            alert_type='TYPE_CUSTOMER',
            severity='SEVERITY_CRITICAL',
            status='STATUS_NEW',
            last_days=2.0,
            last_hours=None
        )

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_fail(self, mock_module, mock_client):
        """
        alletramp alert - get_filtered failure
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_BY_TYPE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            False, False, "Failed to get filtered alerts | 500 Error", {}
        )

        alert.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Failed to get filtered alerts | 500 Error")

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_with_issue_dict(self, mock_module, mock_client):
        """
        alletramp alert - get_filtered success with issue dict (response data)
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_BY_TYPE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        response_data = {"response": [{"uid": "a1", "type": "TYPE_CUSTOMER"}]}
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "Filtered alerts retrieved successfully (1 matches)", response_data
        )

        alert.main()

        instance.exit_json.assert_called_with(
            changed=False,
            msg="Filtered alerts retrieved successfully (1 matches)",
            issue=response_data
        )

    # ---- test_alert operation tests ----

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_test_alert_success_with_message(self, mock_module, mock_client):
        """
        alletramp alert - test_alert success with message
        """
        mock_module.params = self.PARAMS_FOR_TEST_ALERT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.test_alert.return_value = (
            True, True, "Test alert generated successfully", {}
        )

        alert.main()

        mock_flowkit_client.test_alert.assert_called_once_with(
            message='Test alert from Ansible'
        )
        instance.exit_json.assert_called_with(
            changed=True, msg="Test alert generated successfully"
        )
        self.assertEqual(instance.fail_json.call_count, 0)

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_test_alert_success_without_message(self, mock_module, mock_client):
        """
        alletramp alert - test_alert success without message
        """
        mock_module.params = self.PARAMS_FOR_TEST_ALERT_NO_MESSAGE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.test_alert.return_value = (
            True, True, "Test alert generated successfully", {}
        )

        alert.main()

        mock_flowkit_client.test_alert.assert_called_once_with(message=None)

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_test_alert_fail(self, mock_module, mock_client):
        """
        alletramp alert - test_alert failure
        """
        mock_module.params = self.PARAMS_FOR_TEST_ALERT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.test_alert.return_value = (
            False, False, "Test alert generation failed | API error", {}
        )

        alert.main()

        self.assertEqual(instance.exit_json.call_count, 0)
        instance.fail_json.assert_called_with(msg="Test alert generation failed | API error")

    # ---- Flowkit import failure test ----

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_flowkit_import_failure(self, mock_module, mock_client):
        """
        alletramp alert - test flowkit import failure
        """
        with mock.patch('modules.alletramp_alert.AnsibleClient', None):
            mock_module.params = self.PARAMS_FOR_GET_ALL
            mock_module.return_value = mock_module
            instance = mock_module.return_value
            # Make fail_json raise SystemExit to stop execution like real Ansible
            instance.fail_json.side_effect = SystemExit(1)

            with self.assertRaises(SystemExit):
                alert.main()

            instance.fail_json.assert_called_with(
                msg='Python hpe_storage_flowkit_py package is required.'
            )

    # ---- Client initialization exception test ----

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_client_initialization_exception(self, mock_module, mock_client):
        """
        alletramp alert - test client initialization exception
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        # Make fail_json raise SystemExit to stop execution like real Ansible
        instance.fail_json.side_effect = SystemExit(1)

        mock_client.side_effect = Exception("Failed to initialize client")

        with self.assertRaises(SystemExit):
            alert.main()

        instance.fail_json.assert_called_with(msg="Failed to initialize client")

    # ---- Operation exception test ----

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_all_operation_exception(self, mock_module, mock_client):
        """
        alletramp alert - test get_all operation exception
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.side_effect = Exception("API call failed")

        alert.main()

        instance.fail_json.assert_called_with(msg="Operation failed: API call failed")

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_get_filtered_operation_exception(self, mock_module, mock_client):
        """
        alletramp alert - test get_filtered operation exception
        """
        mock_module.params = self.PARAMS_FOR_GET_FILTERED_BY_TYPE
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.side_effect = Exception("Filter failed")

        alert.main()

        instance.fail_json.assert_called_with(msg="Operation failed: Filter failed")

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_test_alert_operation_exception(self, mock_module, mock_client):
        """
        alletramp alert - test test_alert operation exception
        """
        mock_module.params = self.PARAMS_FOR_TEST_ALERT
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.test_alert.side_effect = Exception("Test alert API error")

        alert.main()

        instance.fail_json.assert_called_with(msg="Operation failed: Test alert API error")

    # ---- Logout tests ----

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_logout_called_on_success(self, mock_module, mock_client):
        """
        alletramp alert - test that logout is called on successful execution
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "All alerts retrieved successfully", {}
        )

        alert.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_logout_called_on_failure(self, mock_module, mock_client):
        """
        alletramp alert - test that logout is called even on failure
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            False, False, "Failed to get alerts", {}
        )

        alert.main()

        mock_flowkit_client.logout.assert_called_once()

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_logout_exception_ignored(self, mock_module, mock_client):
        """
        alletramp alert - test that logout exceptions are ignored
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value

        mock_flowkit_client = MagicMock()
        mock_client.return_value = mock_flowkit_client
        mock_flowkit_client.get_alerts.return_value = (
            True, False, "All alerts retrieved successfully", {}
        )
        mock_flowkit_client.logout.side_effect = Exception("Logout failed")

        alert.main()

        instance.exit_json.assert_called_with(
            changed=False, msg="All alerts retrieved successfully"
        )

    @mock.patch('modules.alletramp_alert.AnsibleClient')
    @mock.patch('modules.alletramp_alert.AnsibleModule')
    def test_logout_not_called_when_client_initialization_fails(self, mock_module, mock_client):
        """
        alletramp alert - test that logout is skipped when client initialization fails
        """
        mock_module.params = self.PARAMS_FOR_GET_ALL
        mock_module.return_value = mock_module
        instance = mock_module.return_value
        instance.fail_json.side_effect = SystemExit(1)

        mock_client.side_effect = Exception("Failed to initialize client")

        with self.assertRaises(SystemExit):
            alert.main()

        self.assertEqual(mock_client.return_value.logout.call_count, 0)


if __name__ == '__main__':
    unittest.main()
