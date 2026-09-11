#!/usr/bin/python

# -*- coding: utf-8 -*-

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
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: alletramp_alert
description:
    - Query and manage alerts on HPE Alletra MP storage systems
    - Supports getting all alerts, getting filtered alerts, and generating test alerts
    - Uses the /api/v3/alerts endpoint for alert management operations
    - Filtering supports type, severity, status, and time-based filters
author:
    - HPE Storage Team
requirements:
    - "Alletra MP OS - 10.5.x"
    - "Ansible - 2.9 | 2.10 | 2.11"
    - "hpe_storage_alletramp_ansible"
    - "WSAPI service should be enabled on the HPE Alletra MP."
options:
    operation:
        description: The operation to perform
        required: true
        type: str
        choices: ['get', 'test_alert']
    storage_system_ip:
        description: IP address of the storage system
        required: true
        type: str
    storage_system_username:
        description: Username for storage system authentication
        required: true
        type: str
    storage_system_password:
        description: Password for storage system authentication
        required: true
        type: str
        no_log: true
    alert_type:
        description:
            - Filter alerts by type (for get operation)
        required: false
        type: str
        choices: ['TYPE_UNKNOWN', 'TYPE_CUSTOMER', 'TYPE_SERVICE', 'TYPE_APPLICATION']
    severity:
        description:
            - Filter alerts by event severity (for get operation)
        required: false
        type: str
        choices: ['SEVERITY_UNKNOWN', 'SEVERITY_FATAL', 'SEVERITY_CRITICAL',
                  'SEVERITY_MAJOR', 'SEVERITY_MINOR', 'SEVERITY_DEGRADED',
                  'SEVERITY_INFO', 'SEVERITY_DEBUG']
    alert_status:
        description:
            - Filter alerts by status (for get operation)
        required: false
        type: str
        choices: ['STATUS_UNKNOWN', 'STATUS_NEW', 'STATUS_ACKNOWLEDGED',
                  'STATUS_FIXED', 'STATUS_REMOVED', 'STATUS_AUTOFIXED']
    last_days:
        description:
            - Show alerts from the last N days (for get operation)
            - Cannot be used together with last_hours
        required: false
        type: float
    last_hours:
        description:
            - Show alerts from the last N hours (for get operation)
            - Cannot be used together with last_days
        required: false
        type: float
    test_message:
        description: Test message to include in the test alert (for test_alert operation)
        required: false
        type: str
'''

EXAMPLES = '''
- name: Get all alerts
  alletramp_alert:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get

- name: Get alerts filtered by type
  alletramp_alert:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get
    alert_type: "TYPE_CUSTOMER"

- name: Get alerts filtered by severity
  alletramp_alert:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get
    severity: "SEVERITY_CRITICAL"

- name: Get alerts filtered by status
  alletramp_alert:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get
    alert_status: "STATUS_NEW"

- name: Get alerts from last 3 days
  alletramp_alert:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get
    last_days: 3

- name: Get alerts from last 12 hours
  alletramp_alert:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get
    last_hours: 12

- name: Get critical customer alerts from last 2 days
  alletramp_alert:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get
    alert_type: "TYPE_CUSTOMER"
    severity: "SEVERITY_CRITICAL"
    last_days: 2

- name: Generate test alert
  alletramp_alert:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: test_alert
    test_message: "Test alert from Ansible"
'''

RETURN = '''
msg:
    description: Success/failure message
    returned: always
    type: str
changed:
    description: Whether the operation changed the system state
    returned: always
    type: bool
issue:
    description: Any issues encountered during operation
    returned: when issues exist
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from hpe_storage_flowkit_py.v3.src.utils.constants import (
    ALERT_SEVERITIES,
    ALERT_STATUSES,
    ALERT_TYPES,
)
try:
    from ansible_service import AnsibleClient
except ImportError:
    AnsibleClient = None


def main():
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
            'choices': list(ALERT_TYPES)
        },
        'severity': {
            'type': 'str',
            'choices': list(ALERT_SEVERITIES)
        },
        'alert_status': {
            'type': 'str',
            'choices': list(ALERT_STATUSES)
        },
        'last_days': {'type': 'float'},
        'last_hours': {'type': 'float'},
        'test_message': {'type': 'str'}
    }

    module = AnsibleModule(
        argument_spec=fields,
        mutually_exclusive=[['last_days', 'last_hours']]
    )

    if AnsibleClient is None:
        module.fail_json(msg='Failed to import AnsibleClient from ansible_service.')

    # Get module parameters
    operation = module.params['operation']
    storage_system_ip = module.params['storage_system_ip']
    storage_system_username = module.params['storage_system_username']
    storage_system_password = module.params['storage_system_password']
    alert_type = module.params['alert_type']
    severity = module.params['severity']
    alert_status = module.params['alert_status']
    last_days = module.params['last_days']
    last_hours = module.params['last_hours']
    test_message = module.params['test_message']

    flowkit_client = None
    issue_attr_dict = {}

    try:
        flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    except Exception as e:
        module.fail_json(msg=str(e))

    try:
        if operation == 'get':
            return_status, changed, msg, issue_attr_dict = flowkit_client.get_alerts(
                alert_type=alert_type,
                severity=severity,
                status=alert_status,
                last_days=last_days,
                last_hours=last_hours
            )

        elif operation == 'test_alert':
            return_status, changed, msg, issue_attr_dict = flowkit_client.test_alert(
                message=test_message
            )

        if return_status:
            if issue_attr_dict:
                module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
            else:
                module.exit_json(changed=changed, msg=msg)
        else:
            module.fail_json(msg=msg)

    except Exception as e:
        module.fail_json(msg=f"Operation failed: {str(e)}")

    finally:
        try:
            flowkit_client.logout()
        except Exception:
            pass


if __name__ == '__main__':
    main()
