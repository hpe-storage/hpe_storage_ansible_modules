#!/usr/bin/python

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

from ansible.module_utils.basic import AnsibleModule
try:
    from ansible_service import AnsibleClient
except ImportError:
    AnsibleClient = None


def main():
    fields = {
        'operation': {
            'required': True, 
            'choices': ['configure_datetime'], 
            'type': 'str'
        },
        'storage_system_ip': {
            'required': True, 
            'type': 'str'
        },
        'storage_system_username': {
            'required': True, 
            'type': 'str', 
            'no_log': True
        },
        'storage_system_password': {
            'required': True, 
            'type': 'str', 
            'no_log': True
        },
        'date_time': {
            'type': 'str'
        },
        'ntp_addresses': {
            'type': 'list'
        },
        'timezone': {
            'required': True, 
            'type': 'str'
        }
    }
    
    module = AnsibleModule(argument_spec=fields)

    if AnsibleClient is None:
        module.fail_json(msg='Failed to import AnsibleClient from ansible_service.')

    storage_system_ip = module.params['storage_system_ip']
    storage_system_username = module.params['storage_system_username']
    storage_system_password = module.params['storage_system_password']
    date_time = module.params['date_time']
    ntp_addresses = module.params['ntp_addresses']
    timezone = module.params['timezone']

    flowkit_client = None

    # Validate mutual exclusivity: either dateTime OR ntpAddresses, but not both
    if date_time and ntp_addresses:
        module.fail_json(msg="Cannot specify both date_time and ntp_addresses. Provide either one or the other.")
    
    if not date_time and not ntp_addresses:
        module.fail_json(msg="Must specify either date_time or ntp_addresses (but not both).")

    try:
        flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    except Exception as e:
        module.fail_json(msg=str(e))
   
    try:
        operation = module.params['operation']
        if operation == 'configure_datetime':
            try:
                return_status, changed, msg, issue_attr_dict = flowkit_client.configure_datetime(
                    date_time, ntp_addresses, timezone
                )
            except Exception as e:
                module.fail_json(msg=str(e))
        
        if return_status:
            if issue_attr_dict:
                module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
            else:
                module.exit_json(changed=changed, msg=msg)
        else:
            module.fail_json(msg=msg)
    finally:
        try:
            flowkit_client.logout()
        except Exception:
            pass


if __name__ == '__main__':
    main()
