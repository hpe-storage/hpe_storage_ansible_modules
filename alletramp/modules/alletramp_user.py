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
module: alletramp_user
description:
    - Create, modify or delete user accounts on HPE Alletra MP storage systems
    - Manage user accounts and domain privileges using user names
    - Uses the /api/v3/users endpoint for user management operations
    - Automatically resolves user names to UIDs internally
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
        choices: ['create', 'modify', 'delete', 'get', 'get_all']
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
    name:
        description: The name of the user account (required for all operations)
        required: true
        type: str
    password:
        description: Password for the local user (required for creation)
        required: false
        type: str
        no_log: true
    current_password:
        description: Current password when changing password
        required: false
        type: str
        no_log: true
    new_password:
        description: New password when changing password
        required: false
        type: str
        no_log: true
    domain_privileges:
        description: List of domains and associated privileges for the user
        required: false
        type: list
        elements: dict
        suboptions:
            name:
                description: Name of the domain
                required: true
                type: str
            privilege:
                description: The privilege assigned in the domain
                required: true
                type: str
                choices: ['super', 'service', 'security_admin', 'edit', 'create', 'browse', 'basic_edit']
'''

EXAMPLES = '''
- name: Get all users
  alletramp_user:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get_all

- name: Get user by name
  alletramp_user:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get
    name: "ansible_user"
  register: user_info

- name: Create new user with domain privileges
  alletramp_user:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: create
    name: "ansible_user"
    password: "securepassword123"
    domain_privileges:
      - name: "system"
        privilege: "edit"
      - name: "default"
        privilege: "browse"

- name: Modify user domain privileges
  alletramp_user:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: modify
    name: "ansible_user"
    domain_privileges:
      - name: "system"
        privilege: "create"
      - name: "management"
        privilege: "security_admin"

- name: Change user password
  alletramp_user:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: modify
    name: "ansible_user"
    current_password: "securepassword123"
    new_password: "newsecurepassword456"

- name: Delete user
  alletramp_user:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: delete
    name: "ansible_user"
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
user_info:
    description: User information when operation is 'get'
    returned: when operation is 'get'
    type: dict
    contains:
        name:
            description: User name
            type: str
        domain_privileges:
            description: List of domain privileges
            type: list
issue:
    description: Any issues encountered during operation
    returned: when issues exist
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from ansible_service import AnsibleClient
except ImportError:
    AnsibleClient = None


def main():
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
    
    module = AnsibleModule(argument_spec=fields)

    if AnsibleClient is None:
        module.fail_json(msg='Failed to import AnsibleClient from ansible_service.')

    # Get module parameters
    operation = module.params['operation']
    storage_system_ip = module.params['storage_system_ip']
    storage_system_username = module.params['storage_system_username']
    storage_system_password = module.params['storage_system_password']
    name = module.params['name']
    password = module.params['password']
    current_password = module.params['current_password']
    new_password = module.params['new_password']
    domain_privileges = module.params['domain_privileges']

    flowkit_client = None
    issue_attr_dict = {}  # Initialize to avoid UnboundLocalError

    try:
        flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    except Exception as e:
        module.fail_json(msg=str(e))
   
    try:
        if operation == 'get_all':
            return_status, changed, msg, issue_attr_dict = flowkit_client.get_all_users()
                
        elif operation == 'get':
            return_status, changed, msg, issue_attr_dict = flowkit_client.get_user_by_name(name)
                
        elif operation == 'create':
            return_status, changed, msg, issue_attr_dict = flowkit_client.create_user(
                name=name,
                password=password,
                domain_privileges=domain_privileges
            )
            
        elif operation == 'modify':
            return_status, changed, msg, issue_attr_dict = flowkit_client.modify_user_by_name(
                name=name,
                current_password=current_password,
                new_password=new_password,
                    domain_privileges=domain_privileges
                )
                
        elif operation == 'delete':
            return_status, changed, msg, issue_attr_dict = flowkit_client.delete_user_by_name(name)
        
        
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
