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
description: "On HPE Alletra MP - Create snapshot  - Delete snapshot 
 - Modify snapshot  -  Create Schedule - Modify Schedule - Suspend Schedule
 - Resume Schedule - Delete Schedule"
module: alletramp_snapshot 
options:
  allow_remote_copy_parent:
    description:
      - "Allows the promote operation to proceed even if the RW parent volume
       is currently in a Remote Copy volume group, if that group has not been
       started. If the Remote Copy group has been started, this command
       fails.\n"
    required: false
    type: bool
  base_volume_name:
    description:
      - "Specifies the source volume.\nRequired with action create\n"
    required: false
  expiration_time:
    description:
      - "Specifies the relative time from the current time that the volume
       expires. Value is a positive integer and in the range of 1 to 43,800
       hours, or 1825 days.\n"
    required: false
  expiration_unit:
    choices:
      - hours
      - days
    default: hours
    description:
      - "Unit of Expiration Time."
    required: false
  new_name:
    description:
      - "New name of the volume."
    required: false
  priority:
    choices:
      - PRIORITYTYPE_HIGH
      - PRIORITYTYPE_MED
      - PRIORITYTYPE_LOW
    description:
      - "Does not apply to online promote operation or to stop promote
       operation."
    required: false
  read_only:
    description:
      - "Specifies that the copied volume is read-only. false(default) The
       volume is read/write.\n"
    required: false
    type: bool
  retention_time:
    description:
      - "Specifies the relative time from the current time that the volume will
       expire. Value is a positive integer and in the range of 1 to 43,800
       hours, or 1825 days.\n"
    required: false
  retention_unit:
    choices:
      - hours
      - days
    default: hours
    description:
      - "Unit of Retention Time."
    required: false
  snapshot_name:
    description:
      - "Specifies a snapshot  volume name."
    required: true
  addToSet:
    description:
      - "Specifies the volume set name to which the created snapshot  will be added.
       Used with create_schedule operation.\n"
    required: false
    type: str
  comment:
    description:
      - "Specifies any additional information for the snapshot ."
    required: false
    type: str
  dayofmonth:
    description:
      - "Day of the month to run the schedule. Default is * (every day).
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: str
    default: "*"
  dayofweek:
    description:
      - "Day of the week to run the schedule. Default is * (every day).
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: str
    default: "*"
  hour:
    description:
      - "Hour to run the schedule. Default is * (every hour).
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: str
    default: "*"
  interval:
    description:
      - "Interval between schedule runs.
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: str
  minute:
    description:
      - "Minute to run the schedule. Default is * (every minute).
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: str
    default: "*"
  month:
    description:
      - "Month to run the schedule. Default is * (every month).
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: str
    default: "*"
  new_schedule_name:
    description:
      - "New name for the schedule when modifying.
       Used with modify_schedule operation.\n"
    required: false
    type: str
  noalert:
    description:
      - "Specifies whether to suppress alerts for the schedule.
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: bool
  norebalance:
    description:
      - "Do not rebalance this schedule when norebalance is true.
       This option is not allowed with schedules using the interval option.
       Available since v2.6.0.
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: bool
  rcopy:
    description:
      - "Specifies whether to enable remote copy for the snapshot .
       Used with create_schedule operation.\n"
    required: false
    type: bool
  runonce:
    description:
      - "Specifies whether the schedule should run only once.
       Used with create_schedule operation.\n"
    required: false
    type: bool
  schedule_name:
    description:
      - "Specifies the name of the snapshot  schedule.
       Required with create_schedule, modify_schedule, suspend_schedule, resume_schedule, and delete_schedule operations.\n"
    required: false
    type: str
  year:
    description:
      - "Year to run the schedule.
       Used with create_schedule and modify_schedule operations.\n"
    required: false
    type: str
  operation:
    choices:
      - create
      - delete
      - modify
      - restore_offline
      - restore_online
      - create_schedule
      - suspend_schedule
      - resume_schedule
      - delete_schedule
      - modify_schedule
    description:
      - "Whether the specified snapshot  should exist or not. operation also
       provides actions to modify, restore snapshot s, and manage snapshot  schedules.\n"
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
short_description: "Manage HPE Alletra MP snapshot "
'''

EXAMPLES = r'''
    - name: Create Volume snapshot my_ansible_snapshot 
      alletramp_snapshot : 
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:create
        snapshot_name:"my_ansible_snapshot "
        base_volume_name:"my_ansible_volume_check"
        read_only:False

    - name: Restore offline Volume snapshot my_ansible_snapshot 
      alletramp_snapshot : 
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:restore_offline
        snapshot_name:"my_ansible_snapshot "
        priority:"PRIORITYTYPE_MED"
        
    - name: Restore online Volume snapshot my_ansible_snapshot 
      alletramp_snapshot : 
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:restore_online
        snapshot_name:"my_ansible_snapshot "


    - name: Modify/rename snapshot my_ansible_snapshot  to my_ansible_snapshot_renamed
      alletramp_snapshot : 
        storage_system_ip:"{{ storage_system_ip }}"
        storage_system_username:"{{ storage_system_username }}"
        storage_system_password:"{{ storage_system_password }}"
        operation:modify
        snapshot_name:"my_ansible_snapshot "
        new_name:"my_ansible_snapshot_renamed"
        

        
    - name: Delete snapshot my_ansible_snapshot_renamed
      alletramp_snapshot : 
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: delete
        snapshot_name: "my_ansible_snapshot_renamed"

    - name: Create snapshot  schedule
      alletramp_snapshot :
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: create_schedule
        schedule_name: "daily_snapshot_schedule"
        base_volume_name: "my_ansible_volume"
        hour: "2"
        minute: "0"
        read_only: False
        retention_time: 7
        retention_unit: "days"

    - name: Modify snapshot  schedule
      alletramp_snapshot :
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: modify_schedule
        schedule_name: "daily_snapshot_schedule"
        new_schedule_name: "nightly_snapshot_schedule"
        hour: "0"
        minute: "30"

    - name: Suspend snapshot  schedule
      alletramp_snapshot :
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: suspend_schedule
        schedule_name: "nightly_snapshot_schedule"

    - name: Resume snapshot  schedule
      alletramp_snapshot :
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: resume_schedule
        schedule_name: "nightly_snapshot_schedule"

    - name: Delete snapshot  schedule
      alletramp_snapshot :
        storage_system_ip: "{{ storage_system_ip }}"
        storage_system_username: "{{ storage_system_username }}"
        storage_system_password: "{{ storage_system_password }}"
        operation: delete_schedule
        schedule_name: "nightly_snapshot_schedule"
'''

RETURN = r'''
'''


from ansible.module_utils.basic import AnsibleModule
try:
    from ansible_service import AnsibleClient
except ImportError:
    AnsibleClient = None

def main():
    fields = {
        "operation": {
            "required": True,
            "choices": ['create', 'delete','modify', 'restore_offline',
                        'restore_online','create_schedule','suspend_schedule', 
                        'resume_schedule', 'delete_schedule', 'modify_schedule'],
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
        "snapshot_name": {
            "type": "str"
        },
        "base_volume_name": {
            "type": "str"
        },
        "read_only": {
            "type": "bool"
        },
        "expiration_time": {
            "type": "int",
            "default":None
        },
        "retention_time": {
            "type": "int",
            "default":None
        },
        "expiration_unit": {
            "type": "str",
            "choices": ['seconds','minutes','hours', 'days'],
            "default": 'hours'
        },
        "retention_unit": {
            "type": "str",
            "choices": ['seconds','minutes','hours', 'days'],
            "default": 'hours'
        },
        "priority": {
            "type": "str",
            "choices": ['PRIORITYTYPE_HIGH', 'PRIORITYTYPE_MED', 'PRIORITYTYPE_LOW'],
        },
        "allow_remote_copy_parent": {
            "type": "bool"
        },
        "new_name": {
            "type": "str"
        },
        "comment":{
             "type":"str"
        },
        "addToSet":{
            "type":"str",
        },
        "rcopy":{
            "type":"bool"
        },
        "schedule_name": {
            "type": "str"
        },
        "dayofmonth": {
            "type": "str",
            "default":"*"
        },
        "dayofweek": {
            "type": "str",
            "default":"*"
        },
        "hour": {
            "type": "str",
            "default":"*"
        },
        "interval": {
            "type": "str"
        },
        "minute": {
            "type": "str",
            "default":"*"
        },
        "month": {
            "type": "str",
            "default":"*"
        },
        "noalert": {
            "type": "bool"
        },
        "norebalance": {
            "type": "bool"
        },
        "runonce": {
            "type": "bool"
        },
        "year": {
            "type": "str"
        },
        "new_schedule_name":{
            "type":"str"
        }

    }

    module = AnsibleModule(argument_spec=fields)

    if AnsibleClient is None:
        module.fail_json(msg='Failed to import AnsibleClient from ansible_service.')

    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    snapshot_name = module.params["snapshot_name"]
    base_volume_name = module.params["base_volume_name"]
    readOnly = module.params["read_only"]
    expiration_time = module.params["expiration_time"]
    retention_time = module.params["retention_time"]
    expiration_unit = module.params["expiration_unit"]
    retention_unit = module.params["retention_unit"]
    priority = module.params["priority"]
    rcp = module.params["allow_remote_copy_parent"]
    new_name = module.params["new_name"]
    comment=module.params["comment"]
    addToSet = module.params["addToSet"]
    rcopy = module.params["rcopy"]
    schedule_name = module.params["schedule_name"]
    dayofmonth = module.params["dayofmonth"]
    dayofweek = module.params["dayofweek"]
    hour = module.params["hour"]
    interval = module.params["interval"]
    minute = module.params["minute"]
    month = module.params["month"]
    noalert = module.params["noalert"]
    norebalance = module.params["norebalance"]
    runonce = module.params["runonce"]
    year = module.params["year"]
    new_schedule_name = module.params["new_schedule_name"]
    # operations
    changed = False  # Initialize changed variable
    try:
      if module.params["operation"] == "create":
          
              payload = {
                  "readOnly": readOnly,
                  "comment":comment,
                  "expiration_time": expiration_time,
                  "retention_time": retention_time,
                  "expiration_unit": expiration_unit,
                  "retention_unit": retention_unit
              }
              payload = {k: v for k, v in payload.items() if v is not None}
              if 'expiration_time' not in payload and 'expiration_unit' in payload:
                payload.pop('expiration_unit')
              if 'retention_time' not in payload and 'retention_unit' in payload:
                payload.pop('retention_unit')
              return_status,changed,msg,issue_attr_dict=flowkit_client.create_snapshot(base_volume_name,snapshot_name,**payload)
  
          
      elif module.params["operation"] == "modify":
          payload = {
                  "comment":comment,
                  "expiration_time": expiration_time,
                  "retention_time": retention_time,
                  "expiration_unit": expiration_unit,
                  "retention_unit": retention_unit,
                  "name":new_name
              }
          payload = {k: v for k, v in payload.items() if v is not None}
          if 'expiration_time' not in payload and 'expiration_unit' in payload:
              payload.pop('expiration_unit')
          if 'retention_time' not in payload and 'retention_unit' in payload:
              payload.pop('retention_unit')
          return_status,changed,msg,issue_attr_dict=flowkit_client.modify_volume(snapshot_name,**payload)


      elif module.params["operation"] == "delete":
          
          return_status,changed,msg,issue_attr_dict=flowkit_client.delete_snapshot(snapshot_name)
      
      elif module.params["operation"] == "restore_offline":
          
              payload = {
              "online":False,
              "priority": priority, 
              "rcp": rcp
              }
              payload = {k: v for k, v in payload.items() if v is not None}
              return_status,changed,msg,issue_attr_dict=flowkit_client.promote_snapshot_volume(snapshot_name,**payload)

      elif module.params["operation"] == "restore_online":

              payload = {
              "online":True,
              "rcp": rcp,
              "priority":priority
              }
              payload = {k: v for k, v in payload.items() if v is not None}
              return_status,changed,msg,issue_attr_dict=flowkit_client.promote_snapshot_volume(snapshot_name,**payload)

      elif module.params["operation"]== "create_schedule":
    
            payload= {
                "month": month,
                "minute": minute,
                "hour": hour,
                "dayofmonth": dayofmonth,
                "dayofweek": dayofweek,
                "interval":interval,
                "noalert":noalert,
                "runonce":runonce,
                "year":year,
                "norebalance":norebalance,

                "createsv": {
                  "readOnly": readOnly,
                  "namePattern": "CUSTOM",
                  "customName": schedule_name,
                  "vvOrVvset": base_volume_name,
                  "addToSet":addToSet,
                  "rcopy":rcopy,
                  "expiration_time":expiration_time,
                  "retention_time":retention_time,
                  "expiration_unit":expiration_unit,
                  "retention_unit":retention_unit,
                }
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            if payload.get("createsv"):
              payload["createsv"] = {k: v for k, v in payload["createsv"].items() if v is not None}
            return_status,changed,msg,issue_attr_dict=flowkit_client.create_schedule(schedule_name,**payload)
      
      elif module.params["operation"]=="modify_schedule":
          payload={
              "dayofmonth":dayofmonth,
              "dayofweek":dayofweek,
              "hour":hour,
              "interval":interval,
              "minute":minute,
              "month":month,
              "name":new_schedule_name,
              "noalert":noalert,
              "norebalance":norebalance,
              "year" :year
          }
          payload = {k: v for k, v in payload.items() if v is not None}
          return_status,changed,msg,issue_attr_dict=flowkit_client.modify_schedule(schedule_name,**payload)
      elif module.params["operation"]=="suspend_schedule":
          return_status,changed,msg,issue_attr_dict=flowkit_client.suspend_schedule(schedule_name)
      elif module.params["operation"]=="resume_schedule":
          return_status,changed,msg,issue_attr_dict=flowkit_client.resume_schedule(schedule_name)
      elif module.params["operation"]=="delete_schedule":
          return_status,changed,msg,issue_attr_dict=flowkit_client.delete_schedule(schedule_name)
      else:
          module.fail_json(changed=False, msg=f"Invalid Operation")

      if return_status:
        if issue_attr_dict:
          module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
        module.exit_json(changed=changed,msg=msg)
      else:
        module.fail_json(changed=changed,msg=msg)
    except Exception as e:
        module.fail_json(changed=changed, msg=f"Exception occurred: {str(e)}")
    finally:
        # Always clean up the session
        try:
            flowkit_client.logout()
        except Exception as e:
            pass  # Ignore session cleanup errors
if __name__ == '__main__':
    main()
