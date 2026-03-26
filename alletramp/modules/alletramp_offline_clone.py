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
description: "On HPE Alletra MP - Create Offline Clone - Delete Clone
 - Resync Clone - Stop Cloning"
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
  dest_cpg:
    description:
      - "Specifies the destination CPG for an online copy."
    required: false
  addToSet:
    description:
      - "Adds the volume copies to the specified volume set."
      - "The set will be created if it does not exist and will inherit attributes from the parent set unless specifically overridden."
      - "Can only be used with online option."
    required: false
    type: str
  appSetBusinessUnit:
    description:
      - "Business unit for an application that is using this set."
    required: false
    type: str
  appSetComments:
    description:
      - "Free-form comments about virtual volume set."
    required: false
    type: str
  appSetExcludeAIQoS:
    description:
      - "Indicates if to exclude the virtual volume set from aiqos or not."
    choices:
      - yes
      - no
    required: false
    type: str
  appSetImportance:
    description:
      - "Virtual volume set importance."
    required: false
    type: str
  appSetType:
    description:
      - "Type of the application using this set."
    required: false
    type: str
  bulkvv:
    description:
      - "Make the new created target volume VMware specific."
    required: false
    type: bool
  enableResync:
    description:
      - "Specifies that the destination volume be re-synchronized with its parent volume using a saved snapshot so that only the changes need to be copied."
    required: false
    type: bool
  online:
    description:
      - "With this option the destination can be immediately exported and is automatically created."
      - "This option requires the destinationCpg parameter."
    required: false
    type: bool
  priority:
    choices:
      - PRIORITYTYPE_HIGH
      - PRIORITYTYPE_MED
      - PRIORITYTYPE_LOW
    default: PRIORITYTYPE_MED
    description:
      - "Specifies the priority of the copy operation when it is started."
    required: false
  reduce:
    description:
      - "Indicates that the volume the online copy creates should be a volume using both the dedup and compression technologies."
      - "Without this option a thinly provisioned volume is created."
    required: false
    type: bool
  selectionType:
    description:
      - "Specifies how volumes are selected from destination virtual volume set."
      - "This is applicable only for non-online virtual volume set clones where destination is a set."
    choices:
      - PARENTVV_INDEX
      - PARENTVV_PREFIX
    required: false
    type: str
  skip_zero:
    description:
      - "Enables (true) or disables (false) copying only allocated portions of
       the source VV from a thin provisioned source."
    required: false
    type: bool
  operation:
    choices:
      - create
      - delete
      - resync
      - stop
    description:
      - "Whether the specified Clone should exist or not. operation also provides
       actions to resync and stop clone\n"
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
short_description: "Manage HPE Alletra MP Offline Clone"
'''

EXAMPLES = r'''
    - name: Create Clone clone_volume_ansible
      alletramp_offline_clone:
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:create
        clone_name:"clone_volume_ansible"
        base_volume_name:"{{ volume_name }}"
        dest_cpg:"{{ cpg }}"
        priority:"PRIORITYTYPE_MED"

    - name: Stop Clone clone_volume_ansible
      alletramp_offline_clone:
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:stop
        clone_name:"clone_volume_ansible"
        base_volume_name:"{{ volume_name }}"

    - name: Delete clone "clone_volume_ansible"
      alletramp_offline_clone:
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
except:
    AnsibleClient = None

def main():

    fields = {
        "operation": {
            "required": True,
            "choices": ['create', 'delete', 'resync', 'stop'],
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
        "priority": {
            "required": False,
            "type": "str",
            "choices": ['PRIORITYTYPE_HIGH', 'PRIORITYTYPE_MED', 'PRIORITYTYPE_LOW'],
            "default": "PRIORITYTYPE_MED"
        },
        "skip_zero": {
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
        "enableResync": {
            "type": "bool",
            "default": None
        },
        "reduce": {
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
    priority = module.params["priority"]
    skip_zero = module.params["skip_zero"]
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
    enableResync = module.params["enableResync"]
    reduce = module.params["reduce"]
    selectionType = module.params["selectionType"]

    # operations
    try:
      if module.params["operation"] == "create":
        if not flowkit_client.offline_phy_copy_exist(base_volume_name,clone_name) and not flowkit_client.online_phy_copy_exist(base_volume_name,clone_name):
          optional = {
            'online': False,
            'priority': priority}
              
              # Add skipZero if True
        if skip_zero:
          optional['skipZero'] = skip_zero
              
            # Other parameters - include if not None
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
                'enableResync': enableResync,
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
            
              if flowkit_client.is_volume_exists(clone_name) and not flowkit_client.online_phy_copy_exist(base_volume_name,clone_name) and not flowkit_client.offline_phy_copy_exist(base_volume_name, clone_name):
                return_status,changed,msg,issue_attr_dict= flowkit_client.delete_volume(clone_name) 
              else:
                  module.exit_json(changed=False,msg="Clone/Volume is busy. Cannot be deleted")

      elif module.params["operation"] == "stop":
        
              if flowkit_client.is_volume_exists(name=clone_name) and  flowkit_client.offline_phy_copy_exist(base_volume_name,clone_name):
                return_status,changed,msg,issue_attr_dict= flowkit_client.stop_physical_copy(clone_name)
             
              else:
                  module.exit_json(changed=False,msg= "Offline Cloning not in progress")
      
      elif module.params["operation"] == "resync":
        return_status,changed,msg,issue_attr_dict=flowkit_client.resync_physical_copy(clone_name)
      
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