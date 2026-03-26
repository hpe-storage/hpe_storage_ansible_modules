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
from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r'''
---
author: "Hewlett Packard Enterprise"
description: "On HPE Alletra MP - Create Host Set - Add Hosts to
 Host Set - Remove Hosts from Host Set - Delete Host Set"
module: alletramp_hostset
options:
  domain:
    description:
      - "The domain in which the Host Set will be created."
    required: false
  hostset_name:
    description:
      - "Name of the host set to be created."
    required: true
  setmembers:
    description:
      - "The hosts to be added to the hostset.\nRequired with action
       add_hosts, remove_hosts\n"
    required: false
  operation:
    description:
      - "Operation action specifies whether the specified Host Set should be created or deleted. Also
       provides actions to add or remove hosts from host set"
    choices:
      ['create', 'delete', 'add_hosts', 'remove_hosts']
    required: true
  storage_system_ip:
    description:
      - "The storage system IP address."
    required: true
  storage_system_password:
    description:
      - "The storage system password."
    required: true
  storage_system_username:
    description:
      - "The storage system user name."
    required: true

requirements:
  - "Alletra MP OS - 10.5.x"
  - "Ansible - 2.9 | 2.10 | 2.11"
  - "hpe_storage_alletramp_ansible"
  - "WSAPI service should be enabled on the HPE Alletra MP."
short_description: "Manage HPE Alletra MP Host Set"
'''

EXAMPLES = r'''
    - name: Create hostset "{{ hostsetset_name }}"
      alletramp_hostset:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=create
        hostset_name="{{ hostset_name }}"
        setmembers="{{ add_host_setmembers }}"

    - name: Add hosts to Hostset "{{ hostsetset_name }}"
      alletramp_hostset:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=add_hosts
        hostset_name="{{ hostset_name }}"
        setmembers="{{ add_host_setmembers2 }}"

    - name: Remove hosts from Hostset "{{ hostsetset_name }}"
      alletramp_hostset:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=remove_hosts
        hostset_name="{{ hostset_name }}"
        setmembers="{{ remove_host_setmembers }}"

    - name: Delete Hostset "{{ hostset_name }}"
      alletramp_hostset:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=delete
        hostset_name="{{ hostset_name }}"
'''

RETURN = r'''
'''


from ansible.module_utils.basic import AnsibleModule

# Import HPE Storage Ansible Client for interacting with Alletra MP storage systems
try:
    from hpe_storage_flowkit_py.services.src.ansible_service import AnsibleClient
except:
    AnsibleClient = None



def main():
    # Define module parameters and their validation rules
    fields = {
        'operation': {'required': True, 'choices': ['create', 'delete', 'add_hosts', 'remove_hosts'], 'type': 'str'},
        'storage_system_ip': {'required': True, 'type': 'str'},
        'storage_system_username': {'required': True, 'type': 'str', 'no_log': True},
        'storage_system_password': {'required': True, 'type': 'str', 'no_log': True},
        'hostset_name': {'required': True, 'type': 'str'},
        'domain': {'type': 'str'},
        'setmembers': {'type': 'list'}
    }
    
    # Initialize Ansible module with parameter specifications
    module = AnsibleModule(argument_spec=fields)

    # Verify that the required HPE Storage client library is available
    if AnsibleClient is None:
        module.fail_json(msg='Python hpe_storage_flowkit_py package is required.')

    # Extract module parameters
    storage_system_ip = module.params['storage_system_ip']
    storage_system_username = module.params['storage_system_username']
    storage_system_password = module.params['storage_system_password']
    hostset_name = module.params['hostset_name']
    domain = module.params['domain']
    setmembers = module.params['setmembers']

    # Initialize the HPE Storage client with connection credentials
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
   
    try:
        # Execute the requested operation based on the 'operation' parameter
        # Each operation returns: (success_status, changed_flag, message, issue_details)
        operation = module.params['operation']
        
        if operation == 'create':
            # Create a new host set with specified domain and initial members
            return_status, changed, msg, issue_attr_dict = flowkit_client.create_hostset(hostset_name, domain = domain, setmembers = setmembers)
        elif operation == 'delete':
            # Delete the specified host set
            return_status, changed, msg, issue_attr_dict = flowkit_client.delete_hostset(hostset_name)
        elif operation == 'add_hosts':
            # Add hosts to an existing host set
            return_status, changed, msg, issue_attr_dict = flowkit_client.add_hosts_to_hostset(hostset_name, setmembers)
        elif operation == 'remove_hosts':
            # Remove hosts from an existing host set
            return_status, changed, msg, issue_attr_dict = flowkit_client.remove_hosts_from_hostset(hostset_name, setmembers)
        # Handle operation result and return appropriate response to Ansible
        if return_status:
            # Operation succeeded - include issue details if any warnings exist
            if issue_attr_dict:
                module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
            else:
                module.exit_json(changed=changed, msg=msg)
        else:
            # Operation failed - return error message
            module.fail_json(msg=msg)
    finally:
        # Always attempt to logout and clean up the session
        # Suppress any logout errors to avoid masking the actual operation result
        try:
            flowkit_client.logout()
        except Exception:
            pass


if __name__ == '__main__':
    main()
