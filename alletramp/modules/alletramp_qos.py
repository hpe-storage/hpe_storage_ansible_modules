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
description: "On HPE Alletra MP - create , delete , modify qos
module: alletramp_qos
options:
  operation:
    choices:
      - create_qos
      - modify_qos
      - delete_qos
      - get_qos
      - list_qos
    description:
      - "The operation to perform on the QoS rule."
    required: true
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
  allowAIQoS:
    description:
      - "Flag to force allow QoS rules even if Intelligent QoS is enabled."
    required: false
    type: bool
  bandwidthMaxLimitKiB:
    description:
      - "I/O issue bandwidth maximum limit for QoS throttling (in KiB/s)."
    required: false
    type: int
  enable:
    description:
      - "If true, the QoS config is enabled. Otherwise, it is disabled."
    required: false
    type: bool
  iopsMaxLimit:
    description:
      - "I/O issue count maximum limit for QoS throttling."
    required: false
    type: int
  targetName:
    description:
      - "Name of the QoS target."
      - "Available since v2.5.0"
      - "If provided when modifying a QoS rule, this will be ignored."
    required: false
    type: str
  targetType:
    description:
      - "QoS target type."
      - "Available since v2.5.0"
      - "Options: QOS_TGT_VV (volume), QOS_TGT_VVSET (volume set), QOS_TGT_DOMAIN (domain), or QOS_TGT_SYSTEM (system-wide)."
      - "If provided when modifying a QoS rule, this will be ignored."
    required: false
    type: str
    choices:
      - QOS_TGT_VV
      - QOS_TGT_VVSET
      - QOS_TGT_DOMAIN
      - QOS_TGT_SYSTEM
requirements:
  - "Alletra MP OS - 10.5.x"
  - "Ansible - 2.9 | 2.10 | 2.11"
  - "hpe_storage_alletramp_ansible"
  - "WSAPI service should be enabled on the HPE Alletra MP."
short_description: "Manage HPE Alletra MP QOS"
 
'''
 
 
EXAMPLES = r'''
 
    - name: Create QoS rule for volume set
      alletramp_qos:
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: create_qos
        targetName: "{{ targetName }}"
        targetType: "QOS_TGT_VVSET"
        targetName: "{{ volumeset_name }}"
        iopsMaxLimit: 50000
        bandwidthMaxLimitKiB: 512000
        enable: true
 
    - name: Modify QoS rule
      alletramp_qos:
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: modify_qos
        targetName: "{{ targetName }}"
        iopsMaxLimit: 20000
        bandwidthMaxLimitKiB: 204800
        enable: true
 
 
    - name: Get QoS rule details
      alletramp_qos:
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: get_qos
        targetName: "{{ targetName }}"
 
    - name: List all QoS rules
      alletramp_qos:
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: list_qos
 
    - name: Delete QoS rule
      alletramp_qos:
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: delete_qos
        targetName: "{{ targetName }}"
'''
 
RETURN = r'''
'''
 
from ansible.module_utils.basic import AnsibleModule
try:
    from hpe_storage_flowkit_py.services.src.ansible_service import AnsibleClient
except ImportError:
    AnsibleClient = None
import json
def main():
    fields = {
        "operation": {"required": True, "choices": ['create_qos','modify_qos','delete_qos','get_qos','list_qos'], "type": 'str'},
        "storage_system_ip": {"required": True, "type": "str"},
        "storage_system_username": {"required": True, "type": "str", "no_log": True},
        "storage_system_password": {"required": True, "type": "str", "no_log": True},
        "iopsMaxLimit": {"type": "int"},
        "bandwidthMaxLimitKiB": {"type": "int"},
        "targetType": {"type": "str", "choices": ['QOS_TGT_VV', 'QOS_TGT_VVSET', 'QOS_TGT_DOMAIN', 'QOS_TGT_SYSTEM']},
        "targetName": {"type": "str"},
        "enable": {"type": "bool"},
        "allowAIQoS": {"type": "bool"},
    }
    module = AnsibleModule(argument_spec=fields)
    if AnsibleClient is None:
        module.fail_json(msg='Python hpe_storage_flowkit_py package is required.')
    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]
    targetName = module.params["targetName"]
    qos_params = {k: v for k, v in module.params.items() if k in [
        "iopsMaxLimit",  "bandwidthMaxLimitKiB", "enable", "targetType", "targetName", "allowAIQoS"
    ] and v is not None}
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    try:
        op = module.params["operation"]
        if op == "create_qos":
            return_status, changed, msg, issue_attr_dict = flowkit_client.create_qos(targetName, qos_params)
        elif op == "modify_qos":
            return_status, changed, msg, issue_attr_dict = flowkit_client.modify_qos(targetName, **qos_params)
        elif op == "delete_qos":
            return_status, changed, msg, issue_attr_dict = flowkit_client.delete_qos(targetName)
        elif op == "get_qos":
            return_status, changed, msg, issue_attr_dict = flowkit_client.get_qos(targetName)
        elif op == "list_qos":
            return_status, changed, msg, issue_attr_dict = flowkit_client.list_qos()
        if return_status:
            if issue_attr_dict:
                module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
            else:
                module.exit_json(changed=changed, msg=msg)
        else:
            module.fail_json(msg=msg)
 
    except Exception as e:
        module.fail_json(changed=False,msg=e)
    finally:
        # Always clean up the session
        try:
            flowkit_client.logout()
        except Exception as e:
            pass  # Ignore session cleanup errors        
if __name__ == '__main__':
    main()