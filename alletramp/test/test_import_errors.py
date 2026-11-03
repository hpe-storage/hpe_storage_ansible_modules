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

import builtins
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from unittest import mock

import pytest
from ansible.module_utils import basic


MODULES_DIR = Path(__file__).resolve().parents[1] / 'modules'
MODULE_NAMES = (
    'alletramp_alert', 'alletramp_certs', 'alletramp_cpg', 'alletramp_dns',
    'alletramp_host', 'alletramp_hostset', 'alletramp_ntp',
    'alletramp_offline_clone', 'alletramp_online_clone', 'alletramp_qos',
    'alletramp_remote_copy', 'alletramp_snapshot', 'alletramp_user',
    'alletramp_vlun', 'alletramp_volume', 'alletramp_volumeset',
)
FLOWKIT_MESSAGE = 'Python hpe_storage_flowkit_py package is required.'
SERVICE_MESSAGE = 'Failed to import AnsibleClient from ansible_service.'


def load_module(module_name, service_error=None, constants_error=None):
    """Execute a fresh module without changing cached modules or loading Flowkit."""
    service = ModuleType('ansible_service')
    service.AnsibleClient = mock.Mock()
    constants = ModuleType('hpe_storage_flowkit_py.v3.src.utils.constants')
    constants.ALERT_TYPES = ('TYPE_HARDWARE',)
    constants.ALERT_SEVERITIES = ('SEVERITY_CRITICAL',)
    constants.ALERT_STATUSES = ('STATUS_NEW',)
    original_import = builtins.__import__

    def controlled_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == 'ansible_service':
            if service_error is not None:
                raise service_error
            return service
        if name == constants.__name__:
            if constants_error is not None:
                raise constants_error
            return constants
        return original_import(name, globals, locals, fromlist, level)

    spec = importlib.util.spec_from_file_location(
        '_import_test_' + module_name, MODULES_DIR / (module_name + '.py')
    )
    module = importlib.util.module_from_spec(spec)
    with mock.patch('builtins.__import__', controlled_import):
        spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('module_name', MODULE_NAMES)
@pytest.mark.parametrize(
    'missing_name,error_text,expected_message',
    [
        pytest.param('hpe_storage_flowkit_py', '', FLOWKIT_MESSAGE, id='flowkit-root'),
        pytest.param('hpe_storage_flowkit_py.v3', '', FLOWKIT_MESSAGE, id='flowkit-v3'),
        pytest.param('hpe_storage_flowkit_py.v1', '', FLOWKIT_MESSAGE, id='flowkit-v1'),
        pytest.param(
            None, "No module named 'hpe_storage_flowkit_py.v3'",
            FLOWKIT_MESSAGE, id='flowkit-message-only',
        ),
        pytest.param('ansible_service', '', SERVICE_MESSAGE, id='ansible-service'),
        pytest.param('other_dependency', '', SERVICE_MESSAGE, id='other-dependency'),
        pytest.param(None, '', SERVICE_MESSAGE, id='unnamed-import-error'),
    ],
)
def test_import_error_classification_and_reporting(
    module_name, missing_name, error_text, expected_message
):
    module = load_module(
        module_name, service_error=ImportError(error_text, name=missing_name)
    )

    assert module.AnsibleClient is None
    assert module.IMPORT_ERROR_MSG == expected_message
    with mock.patch.object(module, 'AnsibleModule') as module_factory:
        instance = module_factory.return_value
        instance.fail_json.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            module.main()
        instance.fail_json.assert_called_once_with(msg=expected_message)
        instance.exit_json.assert_not_called()


@pytest.mark.parametrize('module_name', MODULE_NAMES)
def test_successful_import(module_name):
    module = load_module(module_name)

    assert module.AnsibleClient is not None
    assert module.IMPORT_ERROR_MSG is None


@pytest.mark.parametrize('module_name', MODULE_NAMES)
def test_non_import_error_propagates(module_name):
    error = RuntimeError('Client initialization failed during import')
    with pytest.raises(RuntimeError) as caught:
        load_module(module_name, service_error=error)
    assert caught.value is error


@pytest.mark.parametrize('module_name', MODULE_NAMES)
def test_unavailable_client_uses_generic_fallback(module_name):
    module = load_module(module_name)
    module.AnsibleClient = None

    with mock.patch.object(module, 'AnsibleModule') as module_factory:
        instance = module_factory.return_value
        instance.fail_json.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            module.main()
        instance.fail_json.assert_called_once_with(msg=SERVICE_MESSAGE)


def test_alert_constants_import_failure_reaches_import_guard(capsys):
    module = load_module(
        'alletramp_alert',
        constants_error=ImportError(name='hpe_storage_flowkit_py.v3'),
    )
    assert module.AnsibleClient is None
    assert module.IMPORT_ERROR_MSG == FLOWKIT_MESSAGE
    assert module.ALERT_TYPES == ()
    assert module.ALERT_SEVERITIES == ()
    assert module.ALERT_STATUSES == ()
    args = {
        'operation': 'get',
        'storage_system_ip': '192.0.2.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        'alert_type': 'INVALID',
        'severity': 'INVALID',
        'alert_status': 'INVALID',
    }

    # Real argument parsing must reach the dependency guard, not reject choices.
    with mock.patch.object(
        basic, '_ANSIBLE_ARGS', json.dumps({'ANSIBLE_MODULE_ARGS': args}).encode()
    ):
        with pytest.raises(SystemExit) as caught:
            module.main()
    assert caught.value.code == 1
    response = json.loads(capsys.readouterr().out)
    assert response['failed'] is True
    assert response['msg'] == FLOWKIT_MESSAGE


@pytest.mark.parametrize('field', ['alert_type', 'severity', 'alert_status'])
def test_alert_choices_still_validated_when_constants_available(field, capsys):
    module = load_module('alletramp_alert')
    args = {
        'operation': 'get',
        'storage_system_ip': '192.0.2.1',
        'storage_system_username': 'admin',
        'storage_system_password': 'password',
        field: 'INVALID',
    }

    with mock.patch.object(
        basic, '_ANSIBLE_ARGS', json.dumps({'ANSIBLE_MODULE_ARGS': args}).encode()
    ):
        with pytest.raises(SystemExit) as caught:
            module.main()
    assert caught.value.code == 1
    response = json.loads(capsys.readouterr().out)
    assert response['failed'] is True
    assert 'value of ' + field in response['msg']
    assert 'INVALID' in response['msg']
    module.AnsibleClient.assert_not_called()


def test_alert_constants_non_import_error_propagates():
    error = RuntimeError('Constants initialization failed')
    with pytest.raises(RuntimeError) as caught:
        load_module('alletramp_alert', constants_error=error)
    assert caught.value is error
