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
description: "On HPE Alletra MP - Create Volume Set - Add Volumes to Volume Set - Remove Volumes from Volume Set"
 Set - Remove Volumes from Volume Set - Delete Volume Set"
module: alletramp_volumeset
options:
  domain:
    description:
      - "The domain in which the VV set will be created."
    required: false
  setmembers:
    description:
      - "The virtual volumes to be added to the set.\nRequired with action
       add_volumes, remove_volumes\n"
    required: false
  operation:
    choices:
      - create
      - delete
      - add_volumes
      - remove_volumes
    description:
      - "Whether the specified Volume Set should be created or deleted. Also
       provides actions to add or remove volumes from volume set\n"
    required: true
  volumeset_name:
    description:
      - "Name of the volume set to be created."
    required: true
  volumeset_type:
    description:
      - "The type of Volume Set to be created. Required with create operation."
    required: false
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
short_description: "Manage HPE Alletra MP Volume Set"
'''

EXAMPLES = r'''
    - name: Create volume set "{{ volumeset_name }}"
      alletramp_volumeset:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=create
        volumeset_name="{{ volumeset_name }}"
        setmembers="{{ add_vol_setmembers }}"

    - name: Add volumes to Volumeset "{{ volumeset_name }}"
      alletramp_volumeset:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=add_volumes
        volumeset_name="{{ volumeset_name }}"
        setmembers="{{ add_vol_setmembers2 }}"

    - name: Remove volumes from Volumeset "{{ volumeset_name }}"
      alletramp_volumeset:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=remove_volumes
        volumeset_name="{{ volumeset_name }}"
        setmembers="{{ remove_vol_setmembers }}"

    - name: Delete Volumeset "{{ volumeset_name }}"
      alletramp_volumeset:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=delete
        volumeset_name="{{ volumeset_name }}"
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule

# Import HPE Storage Ansible Client for interacting with Alletra MP storage systems
try:
    from ansible_service import AnsibleClient
except ImportError:
    AnsibleClient = None



def main():
    # Define module parameters and their validation rules
    fields = {
        "operation": {
            "required": True,
            "choices": ['create', 'delete', 'add_volumes', 'remove_volumes'],
            "type": 'str'
        },
        "storage_system_ip": {
            "required": True,
            "type": "str"
        },
        "storage_system_username": {
            "required": True,
            "type": "str",
            "no_log": True
        },
        "storage_system_password": {
            "required": True,
            "type": "str",
            "no_log": True
        },
        "volumeset_name": {
            "required": True,
            "type": "str"
        },
        "domain": {
            "type": "str"
        },
        "setmembers": {
            "type": "list"
        },
        "volumeset_type": {
            "required": False,
            "type": "str"
        }
    }
    # Initialize Ansible module with parameter specifications
    # Enforce that 'volumeset_type' is required when operation is 'create'
    module = AnsibleModule(
        argument_spec=fields,
        required_if=[
            ('operation', 'create', ['volumeset_type'])
        ]
    )

    # Verify that the required HPE Storage client library is available
    if AnsibleClient is None:
        module.fail_json(msg='Failed to import AnsibleClient from ansible_service.')

    # Extract module parameters
    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]
    volumeset_name = module.params["volumeset_name"]
    volumeset_type = module.params["volumeset_type"]
    domain = module.params["domain"]
    setmembers = module.params["setmembers"]

    # Initialize the HPE Storage client with connection credentials
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)

    try:
        # Execute the requested operation based on the 'operation' parameter
        # Each operation returns: (success_status, changed_flag, message, issue_details)
        
        if module.params["operation"] == "create":
            # Create a new volume set with specified type, domain, and initial members
            return_status, changed, msg, issue_attr_dict = flowkit_client.create_volumeset(
                volumeset_name, volumeset_type, domain=domain, setmembers=setmembers)
        elif module.params["operation"] == "delete":
            # Delete the specified volume set
            return_status, changed, msg, issue_attr_dict = flowkit_client.delete_volumeset(volumeset_name)
        elif module.params["operation"] == "add_volumes":
            # Add volumes to an existing volume set
            return_status, changed, msg, issue_attr_dict = flowkit_client.add_volumes_to_volumeset(
                volumeset_name, setmembers)
        elif module.params["operation"] == "remove_volumes":
            # Remove volumes from an existing volume set
            return_status, changed, msg, issue_attr_dict = flowkit_client.remove_volumes_from_volumeset(
                volumeset_name, setmembers)

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
