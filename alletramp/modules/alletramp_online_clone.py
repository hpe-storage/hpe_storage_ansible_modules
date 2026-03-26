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
description: "On HPE Alletra MP - Create Online Clone - Delete Clone
module: alletramp_offline_clone
options:
  base_volume_name:
    description:
      - "Specifies the source volume.\nRequired with action create, delete,
       stop\n"
    required: false
  clone_name:
    description:
      - "Specifies the destination volume."
    required: true
  compression:
    description:
      - "Enables (true) or disables (false) compression of the created volume.
       Only tpvv or tdvv are compressed."
    required: false
    type: bool
  dest_cpg:
    description:
      - "Specifies the destination CPG for an online copy."
    required: false
  snap_cpg:
    description:
      - "Specifies the snapshot CPG for an online copy."
    required: false
  operation:
    choices:
      - create
      - delete
    description:
      - "Whether the specified Clone should exist or not.
    required: true
  reduce:
    description:
      - "Enables (true) or disables (false) whether the online copy is a TDVV."
    required: false
    type: bool
  tpvv:
    description:
      - "Enables (true) or disables (false) whether the online copy is a TPVV."
    required: false
    type: bool
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
short_description: "Manage HPE Alletra MP Online Clone"
'''

EXAMPLES = r'''
    - name: Create Volume "{{ volume_name }}"
      alletramp_volume: 
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: create 
        volume_name: "{{ volume_name }}"
        cpg: "{{ cpg }}"
        size: "{{ size }}"

    - name: Create Clone clone_volume_ansible
      alletramp_online_clone:
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: create
        clone_name: "clone_volume_ansible"
        base_volume_name: "{{ volume_name }}"
        dest_cpg: "{{ cpg }}"
        reduce: True

    - name: Delete clone "clone_volume_ansible"
      alletramp_online_clone: 
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:delete 
        clone_name:"clone_volume_ansible"
        base_volume_name:"{{ volume_name }}"

    - name: Delete volume "{{ volume_name }}"
      alletramp_volume: 
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:delete 
        volume_name:"{{ volume_name }}"
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from hpe_storage_flowkit_py.services.src.ansible_service import AnsibleClient
except ImportError:
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
        "clone_name": {
            "required": True,
            "type": "str"
        },
        "base_volume_name": {
            "required": False,
            "type": "str"
        },
        "dest_cpg": {
            "required": False,
            "type": "str",
        },
        "reduce": {
            "required": False,
            "type": "bool",
        },
        "expiration_time": {
            "type": "int",
            "default": None
        },
        "retention_time": {
            "type": "int",
            "default": None
        },
        "expiration_unit":{
           "type":"str",
           "default":"hours"
        },
        "retention_unit":{
           "type":"str",
           "default":"hours"
        },
          "addToSet": {
            "type": "str",
            "default": None
        },
        "appSetBusinessUnit": {
            "type": "str",
            "default": None
        },
        "appSetComments": {
            "type": "str",
            "default": None
        },
        "appSetExcludeAIQoS": {
            "type": "str",
            "choices": ['yes', 'no'],
            "default": None
        },
        "appSetImportance": {
            "type": "str",
            "default": None
        },
        "appSetType": {
            "type": "str",
            "default": None
        },
        "bulkvv": {
            "type": "bool",
            "default": None
        },
        "selectionType": {
            "type": "str",
            "choices": ['PARENTVV_INDEX', 'PARENTVV_PREFIX'],
            "default": None
        }
    }

    module = AnsibleModule(argument_spec=fields)

    if AnsibleClient is None:
        module.fail_json(msg='Python hpe_storage_flowkit_py package is required.')

    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    clone_name = module.params["clone_name"]
    base_volume_name = module.params["base_volume_name"]
    dest_cpg = module.params["dest_cpg"]
    expiration_time=module.params['expiration_time']
    retention_time=module.params['retention_time']
    expiration_unit=module.params['expiration_unit']
    retention_unit=module.params['retention_unit']
    addToSet = module.params["addToSet"]
    appSetBusinessUnit = module.params["appSetBusinessUnit"]
    appSetComments = module.params["appSetComments"]
    appSetExcludeAIQoS = module.params["appSetExcludeAIQoS"]
    appSetImportance = module.params["appSetImportance"]
    appSetType = module.params["appSetType"]
    bulkvv = module.params["bulkvv"]
    reduce = module.params["reduce"]
    selectionType = module.params["selectionType"]

    # operations
    try:
      if module.params["operation"] == "create":
          optional = {
              'online': True,
              'destinationCpg':dest_cpg
          }
          if reduce:
            optional['reduce'] = reduce
          other_params = {
                'expiration_time':expiration_time,
                'retention_time':retention_time,
                'expiration_unit':expiration_unit,
                'retention_unit':retention_unit,
                'addToSet': addToSet,
                'appSetBusinessUnit': appSetBusinessUnit,
                'appSetComments': appSetComments,
                'appSetExcludeAIQoS': appSetExcludeAIQoS,
                'appSetImportance': appSetImportance,
                'appSetType': appSetType,
                'bulkvv': bulkvv,
                'reduce': reduce,
                'selectionType': selectionType
            }
          for param_name, param_value in other_params.items():
                if param_value is not None:
                    optional[param_name] = param_value
          if 'expiration_time' not in optional and 'expiration_unit' in optional:
            optional.pop('expiration_unit')
          if 'retention_time' not in optional and 'retention_unit' in optional:
            optional.pop('retention_unit')          
          return_status,changed,msg,issue_attr_dict=flowkit_client.copy_volume(base_volume_name,clone_name,**optional)
 

      elif module.params["operation"] == "delete":
          
              if flowkit_client.is_volume_exists(name=clone_name) and not flowkit_client.online_phy_copy_exist(base_volume_name,clone_name) and not flowkit_client.offline_phy_copy_exist(base_volume_name, clone_name):
                return_status,changed,msg,issue_attr_dict= flowkit_client.delete_volume(clone_name)
              else:
                  module.exit_json(changed=False,msg="Clone/Volume is busy. Cannot be deleted")
   
      else:
          module.fail_json(msg=f"Invalid Operation")
      if return_status:
          if issue_attr_dict:
            module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
          module.exit_json(changed=changed,msg=msg)
      else:
          module.fail_json(changed=changed,msg=msg)
    except Exception as e:
        module.fail_json(changed,msg=f"Exception occured : {str(e)}")
    finally:
        # Always clean up the session
        try:
            flowkit_client.logout()
        except Exception as e:
            pass  # Ignore session cleanup errors
if __name__ == '__main__':
    main()