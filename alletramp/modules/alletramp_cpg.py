#!/usr/bin/python

# (C) Copyright 2025 Hewlett Packard Enterprise Development LP
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 3 of the GNU General Public License as
# published by the Free Software Foundation.  Alternatively, at your
# choice, you may also redistribute it and/or modify it under the terms
# of the Apache License, version 2.0, available at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r'''
---
author: "Hewlett Packard Enterprise"
description:
  - "Create and delete CPG on HPE Alletra MP."
module: alletramp_cpg
options:
  cpg_name:
    description:
      - "Name of the CPG."
    required: true
  domain:
    description:
      - "Specifies the name of the domain in which the object will reside."
    required: false
  growth_increment:
    default: -1.0
    description:
      - "Specifies the growth increment the amount of logical disk storage
       created on each auto-grow operation.\n"
    required: false
  growth_increment_unit:
    choices:
      - MiB
      - GiB
      - TiB
    default: GiB
    description:
      - "Unit of growth increment."
    required: false
  growth_limit:
    default: -1.0
    description:
      - "Specifies that the autogrow operation is limited to the specified
       storage amount that sets the growth limit.\n"
    required: false
  growth_limit_unit:
    choices:
      - MiB
      - GiB
      - TiB
    default: GiB
    description:
      - "Unit of growth limit."
    required: false
  growth_warning:
    default: -1.0
    description:
      - "Specifies that the threshold of used logical disk space when exceeded
       results in a warning alert.\n"
    required: false
  growth_warning_unit:
    choices:
      - MiB
      - GiB
      - TiB
    default: GiB
    description:
      - "Unit of growth warning."
    required: false
  high_availability:
    choices:
      - HAJBOD_JBOD
      - HAJBOD_DISK
    description:
      - "Specifies the requested High Availability setting.\n"
      - "HAJBOD_JBOD: High availability with JBOD configuration.\n"
      - "HAJBOD_DISK: High availability with disk-based configuration.\n"
    required: false
  cage:
    description:
      - "Cage number that the CPG is allowed to use."
      - "Options: all|cage_num[,cage_num][-cage_num]"
      - "Available since v2.6.0"
    required: false
  position:
    description:
      - "Position number that the CPG is allowed to use."
      - "Options: all|position[,position][-position]"
      - "Available since v2.6.0"
    required: false
  keyValuePairs:
    description:
      - "Key value pairs assigned to the object."
      - "Available since v2.6.0"
      - "Dictionary of key-value pairs for custom metadata."
      Key must start with one of these prefixes: v3_, dp_, dscc_
    required: false
    type: dict
    description:
      - "Specifies the RAID type for the logical disk."
    required: false
  operation:
    choices:
      - create
      - delete
    description:
      - "Whether the specified CPG should exist or not."
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
short_description: "Manage HPE Alletra MP CPG"
'''


EXAMPLES = r'''
    - name: Create CPG "{{ cpg_name }}"
      alletramp_cpg:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=create
        cpg_name="{{ cpg_name }}"
        domain="{{ domain }}"
        growth_increment="{{ growth_increment }}"
        growth_increment_unit="{{ growth_increment_unit }}"
        growth_limit="{{ growth_limit }}"
        growth_limit_unit="{{ growth_limit_unit }}"
        growth_warning="{{ growth_warning }}"
        growth_warning_unit="{{ growth_warning_unit }}"
        high_availability="{{ high_availability }}"
        cage="{{ cage }}"
        position="{{ position }}"
        keyValuePairs="{{ keyValuePairs }}"

    - name: Delete CPG "{{ cpg_name }}"
      alletramp_cpg:
        storage_system_ip="{{ storage_system_ip }}"
        storage_system_username="{{ storage_system_username }}"
        storage_system_password="{{ storage_system_password }}"
        operation=delete
        cpg_name="{{ cpg_name }}"
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from hpe_storage_flowkit_py.services.src.ansible_service import AnsibleClient
except:
    AnsibleClient = None

def main():

    fields = {
        "operation": {
            "required": True,
            "choices": ['create', 'delete'],
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
        "cpg_name": {
            "required": True,
            "type": "str"
        },
        "domain": {
            "type": "str"
        },
        "growth_increment": {
            "type": "float",
            "default": -1.0
        },
        "growth_increment_unit": {
            "type": "str",
            "choices": ['TiB', 'GiB', 'MiB'],
            "default": 'GiB'
        },
        "growth_limit": {
            "type": "float",
            "default": -1.0
        },
        "growth_limit_unit": {
            "type": "str",
            "choices": ['TiB', 'GiB', 'MiB'],
            "default": 'GiB'
        },
        "growth_warning": {
            "type": "float",
            "default": -1.0
        },
        "growth_warning_unit": {
            "type": "str",
            "choices": ['TiB', 'GiB', 'MiB'],
            "default": 'GiB'
        },
        "high_availability": {
            "type": "str",
            "choices": ['HAJBOD_JBOD', 'HAJBOD_DISK'],
        },
        "cage": {
            "type": "str",
            "required": False
        },
        "position": {
            "type": "str",
            "required": False
        },
        "keyValuePairs": {
            "type": "dict",
            "default": None
        }
    }

    module = AnsibleModule(argument_spec=fields)


    if AnsibleClient is None:
      module.fail_json(msg="Python hpe_storage_flowkit_py package is required.")

    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    cpg_name = module.params["cpg_name"]
    
    # Filter CPG parameters and exclude None values and -1.0 growth values
    cpg_params = {}
    
    # Growth parameters with their units - exclude if value is -1.0
    growth_params = [
        ("growth_increment", "growth_increment_unit"),
        ("growth_limit", "growth_limit_unit"),
        ("growth_warning", "growth_warning_unit")
    ]
    
    for param, unit in growth_params:
        value = module.params.get(param)
        if value is not None and value != -1.0:
            cpg_params[param] = value
            unit_value = module.params.get(unit)
            if unit_value is not None:
                cpg_params[unit] = unit_value
    
    # Other parameters - include if not None
    other_params = {
        "domain": "domain",
        "high_availability": "ha",
        "cage": "cage",
        "position": "position",
        "keyValuePairs": "keyValuePairs"
    }
    
    for ansible_param, api_param in other_params.items():
        value = module.params.get(ansible_param)
        if value is not None:
            cpg_params[api_param] = value
    
    # operations
    try:  
      if module.params["operation"] == "create":
          return_status,changed,msg,issue_attr_dict = flowkit_client.create_cpg(cpg_name,**cpg_params)

      elif module.params["operation"] == "delete":
          return_status,changed,msg,issue_attr_dict = flowkit_client.delete_cpg(name=cpg_name)
      else:
          module.fail_json(msg=f"invalid Operaion")
      if return_status:
          if issue_attr_dict:
              module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
          module.exit_json(changed=changed,msg=msg)
      else:
          module.fail_json(changed=changed,msg=msg)
    except Exception as e:
        module.fail_json(changed=False,msg=f"Exception occured : {str(e)}")
    finally:
        # Always clean up the session
        try:
            flowkit_client.logout()
        except Exception as e:
            pass  # Ignore session cleanup errors
if __name__ == '__main__':
    main()
