import mock
from modules import alletramp_certs as certs
from mock import MagicMock
from ansible.module_utils.basic import AnsibleModule as ansible
import unittest


class TestAlletrampCerts(unittest.TestCase):

    PARAMS_FOR_CREATE_SELFSIGNED_CERT = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'uid': None,
        'service': 'unified-server',
        'cert_type': 'selfsigned',
        'key_length': 2048,
        'common_name': 'TestArray',
        'subject_alt': 'DNS:TestArray,IP:10.1.1.10',
        'organization_unit': 'Unit',
        'organization': 'My Company',
        'days': 1095,
        'locality': 'My City',
        'province': 'Colorado',
        'country': 'US',
        'certificate': None,
        'authority_chain': None
    }

    PARAMS_FOR_CREATE_CSR_CERT = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'uid': None,
        'service': 'wsapi',
        'cert_type': 'csr',
        'key_length': 2048,
        'common_name': 'CSRTestArray',
        'country': 'US',
        'subject_alt': None,
        'organization_unit': None,
        'organization': None,
        'days': None,
        'locality': None,
        'province': None,
        'certificate': None,
        'authority_chain': None
    }

    PARAMS_FOR_IMPORT_CERT = {
        'operation': 'create',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'uid': None,
        'service': 'wsapi',
        'cert_type': 'import',
        'certificate': '-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKoK/OvD/XDTMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV\n...(sample certificate)...\n-----END CERTIFICATE-----',
        'authority_chain': '-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKoK/OvD/XDTMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV\n...(sample authority chain)...\n-----END CERTIFICATE-----',
        'key_length': None,
        'common_name': None,
        'subject_alt': None,
        'organization_unit': None,
        'organization': None,
        'days': None,
        'locality': None,
        'province': None,
        'country': None
    }

    PARAMS_FOR_GET_ALL_CERTS = {
        'operation': 'get_all',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'uid': None,
        'service': None,
        'cert_type': None,
        'key_length': None,
        'common_name': None,
        'subject_alt': None,
        'organization_unit': None,
        'organization': None,
        'days': None,
        'locality': None,
        'province': None,
        'country': None,
        'certificate': None,
        'authority_chain': None
    }

    PARAMS_FOR_GET_CERT = {
        'operation': 'get',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'service': 'unified-server',
        'cert_name': 'TestArray',
        'uid': None,
        'cert_type': None,
        'key_length': None,
        'common_name': None,
        'subject_alt': None,
        'organization_unit': None,
        'organization': None,
        'days': None,
        'locality': None,
        'province': None,
        'country': None,
        'certificate': None,
        'authority_chain': None
    }

    PARAMS_FOR_DELETE_CERT = {
        'operation': 'delete',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'service': 'wsapi',
        'cert_name': 'TestArray',
        'uid': None,
        'cert_type': None,
        'key_length': None,
        'common_name': None,
        'subject_alt': None,
        'organization_unit': None,
        'organization': None,
        'days': None,
        'locality': None,
        'province': None,
        'country': None,
        'certificate': None,
        'authority_chain': None
    }

    PARAMS_FOR_PATCH_CERT = {
        'operation': 'patch',
        'storage_system_ip': '192.168.0.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'service': 'ekm-client',
        'cert_name': 'TestArray',
        'certificate': '-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKoK/OvD/XDTMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV\n...(signed certificate)...\n-----END CERTIFICATE-----',
        'authority_chain': '-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKoK/OvD/XDTMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV\n...(CA chain)...\n-----END CERTIFICATE-----',
        'uid': None,
        'cert_type': None,
        'key_length': None,
        'common_name': None,
        'subject_alt': None,
        'organization_unit': None,
        'organization': None,
        'days': None,
        'locality': None,
        'province': None,
        'country': None
    }

    def _mock_module(self, mock_module, params):
        mock_module.params = params
        mock_module.return_value = mock_module
        return mock_module.return_value

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_create_selfsigned_certificate_success(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_CREATE_SELFSIGNED_CERT)
        mock_flowkit_client.return_value.create_certificate.return_value = (True, True, "Certificate created successfully", {})

        certs.main()

        instance.exit_json.assert_called_with(changed=True, msg="Certificate created successfully")

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_create_csr_certificate_success(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_CREATE_CSR_CERT)
        mock_flowkit_client.return_value.create_certificate.return_value = (True, True, "CSR created successfully", {})

        certs.main()

        instance.exit_json.assert_called_with(changed=True, msg="CSR created successfully")

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_import_certificate_success(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_IMPORT_CERT)
        mock_flowkit_client.return_value.create_certificate.return_value = (True, True, "Certificate imported successfully", {})

        certs.main()

        instance.exit_json.assert_called_with(changed=True, msg="Certificate imported successfully")

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_get_all_certificates_success(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_GET_ALL_CERTS)
        mock_flowkit_client.return_value.get_all_certificates.return_value = (True, False, "All certificates retrieved successfully", {"response": []})

        certs.main()

        instance.exit_json.assert_called_with(changed=False, msg="All certificates retrieved successfully", certificates=[])

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_get_certificate_success(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_GET_CERT)
        mock_flowkit_client.return_value.get_certificate_by_name.return_value = (True, False, "Certificate retrieved successfully", {"response": {"uid": "123"}})

        certs.main()

        instance.exit_json.assert_called_with(changed=False, msg="Certificate retrieved successfully", certificate_info={"uid": "123"})

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_delete_certificate_success(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_DELETE_CERT)
        mock_flowkit_client.return_value.delete_certificate_by_name.return_value = (True, True, "Certificate deleted successfully", {})

        certs.main()

        instance.exit_json.assert_called_with(changed=True, msg="Certificate deleted successfully")

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_patch_certificate_success(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_PATCH_CERT)
        mock_flowkit_client.return_value.patch_certificate_by_name.return_value = (True, True, "Certificate patched successfully", {})

        certs.main()

        instance.exit_json.assert_called_with(changed=True, msg="Certificate patched successfully")

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_create_certificate_failure(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_CREATE_SELFSIGNED_CERT)
        mock_flowkit_client.return_value.create_certificate.return_value = (False, False, "Certificate creation failed | Error message", {})

        certs.main()

        instance.fail_json.assert_called_with(msg="Certificate creation failed | Error message")

    @mock.patch('modules.alletramp_certs.AnsibleClient')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_get_all_certificates_members_response_is_flattened(self, mock_module, mock_flowkit_client):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_GET_ALL_CERTS)
        mock_flowkit_client.return_value.get_all_certificates.return_value = (
            True,
            False,
            "All certificates retrieved successfully",
            {"response": {"members": {"cert1": {"uid": "1"}, "cert2": {"uid": "2"}}}},
        )

        certs.main()

        instance.exit_json.assert_called_with(
            changed=False,
            msg="All certificates retrieved successfully",
            certificates=[{"uid": "1"}, {"uid": "2"}],
        )

    @mock.patch('modules.alletramp_certs.AnsibleClient', None)
    @mock.patch('modules.alletramp_certs.IMPORT_ERROR_MSG',
                'Python hpe_storage_flowkit_py package is required.')
    @mock.patch('modules.alletramp_certs.AnsibleModule')
    def test_missing_flowkit_package(self, mock_module):
        instance = self._mock_module(mock_module, self.PARAMS_FOR_GET_ALL_CERTS)
        instance.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            certs.main()

        instance.fail_json.assert_called_with(msg='Python hpe_storage_flowkit_py package is required.')


if __name__ == '__main__':
    unittest.main()