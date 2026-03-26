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
description: "On HPE Alletra MP  - Create Volume - Delete Volume - Modify
 Volume - Grow Volume -  Tune Volume - "
module: alletramp_volume
options:
  count:
    description:
      - "Count of volumes to be created."
      - "Used for creating multiple volumes with similar configuration."
    required: false
    type: int
  comments:
    description:
      - "Additional comments for the volume."
    required: false
    type: str
  count:
    description:
      - "Count of volumes to be created."
      - "Used for creating multiple volumes with similar configuration."
    required: false
    type: int
  cpg:
    description:
      - "Specifies the name of the CPG from which the volume user space will be
       allocated"
    required: false
    type: str
  dataReduction:
    description:
      - "Data reduction setting of the volume to be created."
      - "Enables or disables data reduction for the volume."
    required: false
    type: bool
  expiration_time:
    description:
      - "Remaining time, before the volume expires."
      - "Time value used with expiration_unit."
    required: false
    type: int
  expiration_unit:
    description:
      - "Unit for expiration_time."
    default: hours
    required: false
    type: str
  growth_size_mib:
    description:
      - "Amount by which to grow the volume in MiB."
      - "Used with grow operation."
    required: false
    type: int
  keyValuePairs:
    description:
      - "Key value pairs assigned to the object."
      - "Available since v2.6.0"
      - "Dictionary of key-value pairs for custom metadata."
    required: false
    type: dict
  new_name:
    description:
      - "Specifies the new name for the volume."
      - "Used with modify operation to rename a volume."
    required: false
    type: str
  ransomWare:
    description:
      - "Enable/disable the ransomware policy for the volume."
      - "When enabled, provides protection against ransomware attacks."
    required: false
    type: bool
  reduce:
    description:
      - "Indicates that the volume should use both dedup and compression technologies."
    required: false
    type: bool
  retention_time:
    description:
      - "Sets the time to retain the volume."
      - "Time value used with retention_unit."
    required: false
    type: int
  retention_unit:
    description:
      - "Unit for retention_time."
    default: hours
    required: false
    type: str
  saveToNewName:
    description:
      - "Name of the new volume when tuning a volume."
      - "Used with tune operation to save the tuned volume with a new name."
    required: false
    type: str
  size:
    description:
      - "Specifies the size of the volume"
    required: false
    type: int
  size_unit:
    choices:
      - MiB
      - GiB
      - TiB
    default: MiB
    description:
      - "Specifies the unit of the volume size"
    required: false
    type: str
  operation:
    choices:
      - create
      - delete
      - modify
      - grow
      - tune
    description:
      - "The operation to perform on the volume."
      - "create: Create a new volume"
      - "delete: Delete an existing volume"
      - "modify: Modify volume properties"
      - "grow: Grow the volume size"
      - "tune: Tune the volume (convert type)"
    required: true
    type: str
  type:
    choices:
      - CONVERSIONTYPE_THIN
      - CONVERSIONTYPE_V1
      - CONVERSIONTYPE_V2
    default: CONVERSIONTYPE_V1
    description:
      - "Specifies the conversion type of the volume for tune operation."
      - "CONVERSIONTYPE_THIN: Thin provisioned volume"
      - "CONVERSIONTYPE_V1: Fully provisioned volume with V1 layout"
      - "CONVERSIONTYPE_V2: Fully provisioned volume with V2 layout"
    required: false
    type: str
  userAllocWarning:
    description:
      - "User allocation warning threshold percentage."
      - "Generates warning when volume allocation reaches this percentage."
    required: false
    type: int
  volume_name:
    description:
      - "Name of the Virtual Volume."
    required: true
    type: str
  wwn:
    description:
      - "World Wide Name (WWN) of the volume."
      - "Used with modify operation."
    required: false
    type: str
  storage_system_ip:
    description:
      - "The storage system IP address."
    required: true
    type: str
  storage_system_password:
    description:
      - "The storage system password."
    required: true
    type: str
  storage_system_username:
    description:
      - "The storage system user name."
    required: true
    type: str

requirements:
  - "Alletra MP OS - 10.5.x"
  - "Ansible - 2.9 | 2.10 | 2.11"
  - "hpe_storage_alletramp_ansible"
  - "WSAPI service should be enabled on the HPE Alletra MP."
short_description: "Manage HPE Alletra MP Volume"
'''

EXAMPLES = r'''
    - name: Create Volume "{{ volume_name }}"
      alletramp_volume:
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:create
        volume_name:"{{ volume_name }}"
        cpg:"{{ cpg }}"
        size:"{{ size }}"
    
    - name: Create Volume with data reduction and ransomware protection
      alletramp_volume:
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:create
        volume_name:"{{ volume_name }}"
        cpg:"{{ cpg }}"
        size:"{{ size }}"
        dataReduction: true
        ransomWare: true
 
    - name: Tune Volume "{{ volume_name }} "
      alletramp_volume: 
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:tune 
        volume_name:"{{ volume_name }}"
        type:"CONVERSIONTYPE_V2"
        cpg:"{{ cpg }}"

    - name: Grow Volume "{{ volume_name }}"
      alletramp_volume: 
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:grow 
        volume_name:"{{ volume_name }}"
        growth_size_mib:18000

    - name: Rename Volume "{{ volume_name }} to {{ new_name }}"
      alletramp_volume:
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:modify
        volume_name:"{{ volume_name }}"
        new_name:"{{ new_name }}"

    - name: Delete Volume "{{ volume_name }}"
      alletramp_volume:
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:delete
        volume_name:"{{ new_name }}"
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
            "choices": ['create',
                        'delete',
                        'modify',
                        'grow',
                        'tune'
                        ],
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
        "volume_name": {
            "required": True,
            "type": "str"
        },
        "cpg": {
            "type": "str",
            "default": None
        },
        "size": {
            "type": "int",
            "default": None
        },
        "size_unit": {
            "choices": ['MiB', 'GiB', 'TiB'],
            "type": 'str',
            "default": 'MiB'
        },
        "new_name": { #use for changing name of vol
            "type": "str",
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
        "userAllocWarning":{
           "type":"int"
        },
        "type": {
            "choices": [ "CONVERSIONTYPE_THIN","CONVERSIONTYPE_V1","CONVERSIONTYPE_V2"],
            "type": "str",
            "default": "CONVERSIONTYPE_V1"
        },
        "reduce":{
            "type":"bool"
        },
        "comments":{
           "type":"str"
        },
        "count": {
            "type": "int",
            "default": None
        },
        "dataReduction": {
            "type": "bool",
            "default": None
        },
        "keyValuePairs": {
            "type": "dict",
            "default": None
        },
        "ransomWare": {
            "type": "bool",
            "default": None
        },
        "growth_size_mib":{
           "type":"int"
        },
        "wwn":{
           "type":"str"
        },
        "saveToNewName":{
           "type":"str"
        }
        
    }

    module = AnsibleModule(argument_spec=fields)

    if AnsibleClient is None:
      module.fail_json(msg="Python hpe_storage_flowkit_py package is required.")

    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    
    # Extract all parameters
    volume_name = module.params["volume_name"]
    size = module.params["size"]
    size_unit = module.params["size_unit"]
    cpg = module.params["cpg"]
    new_name = module.params["new_name"]
    expiration_time = module.params["expiration_time"]
    expiration_unit = module.params["expiration_unit"]
    retention_time = module.params["retention_time"]
    retention_unit = module.params["retention_unit"]
    type = module.params["type"]
    comments = module.params["comments"]
    count = module.params["count"]
    dataReduction = module.params["dataReduction"]
    keyValuePairs = module.params["keyValuePairs"]
    ransomWare = module.params["ransomWare"]
    userAllocWarning = module.params["userAllocWarning"]
    growth_size_mib=module.params["growth_size_mib"]
    wwn=module.params["wwn"]
    saveToNewName=module.params["saveToNewName"]

    # operations
    try:
      if module.params["operation"] == "create":
          # Build payload with filtering - use loop approach
          payload = {
              "size_unit": size_unit,
              "comments":comments,
              "count":count,
              "dataReduction":dataReduction,
              "expiration_time":expiration_time,
              "expiration_unit":expiration_unit,
              "retention_time":retention_time,
              "retention_unit":retention_unit,
              "keyValuePairs":keyValuePairs,
              "ransomWare":ransomWare,
              "userAllocWarning":userAllocWarning

          }
          # Filter out None values from payload
          payload = {k: v for k, v in payload.items() if v is not None}
          # Remove unit if corresponding time value is not in payload
          if "expiration_time" not in payload and "expiration_unit" in payload:
            del payload["expiration_unit"]
          if "retention_time" not in payload and "retention_unit" in payload:
            del payload["retention_unit"]
          return_status, changed, msg, issue_attr_dict = flowkit_client.create_volume(volume_name, cpg, size, **payload)  

      elif module.params["operation"] == "delete":
          return_status,changed,msg,issue_attr_dict= flowkit_client.delete_volume(name=volume_name)

      elif module.params["operation"] == "grow":
          return_status,changed,msg,issue_attr_dict=flowkit_client.grow_volume(volume_name,growth_size_mib)

      elif module.params["operation"] == "tune":
        params = {
              "conversionType": type,
              "saveToNewName":saveToNewName
          }
        params = {k: v for k, v in params.items() if v is not None}
        return_status,changed,msg,issue_attr_dict=flowkit_client.tune_volume(volume_name,cpg,**params)
        
      elif module.params["operation"] == "modify":
          # Build volume_mods with filtering
          payload = {
             "name":new_name,
             "comments":comments,
             "expiration_time":expiration_time,
             "expiration_unit":expiration_unit,
             "retention_time":retention_time,
             "retention_unit":retention_unit,
             "keyValuePairs":keyValuePairs,
             "ransomWare":ransomWare,
             "userAllocWarning":userAllocWarning,
             "wwn":wwn
          }
          # Filter out None values from payload
          payload = {k: v for k, v in payload.items() if v is not None}
          if "expiration_time" not in payload and "expiration_unit" in payload:
            del payload["expiration_unit"]
          if "retention_time" not in payload and "retention_unit" in payload:
            del payload["retention_unit"]          
          return_status,changed,msg,issue_attr_dict=flowkit_client.modify_volume(volume_name,**payload)

      else:
        module.fail_json(msg="Invalid Operation")
      
      if return_status:
            if issue_attr_dict:
                module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
            module.exit_json(changed=changed,msg=msg)
      else:
        module.fail_json(changed=changed,msg=msg)
    except Exception as e:
        module.fail_json(changed=False,msg=f"Exception occured :{str(e)}")
    finally:
        # Always clean up the session
        try:
            flowkit_client.logout()
        except Exception as e:
            pass  # Ignore session cleanup errors

if __name__ == '__main__':
    main()
