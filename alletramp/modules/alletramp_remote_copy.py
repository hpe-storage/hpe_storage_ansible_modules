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
description: "Manage HPE Alletra MP Remote Copy groups. This module enables creation,
 modification, and deletion of Remote Copy groups. It supports volume management
 (add/remove), group operations (start/stop/synchronize), link management
 (admit/dismiss), target management (admit/dismiss), and service control."
module: alletramp_remote_copy
options:
  remote_copy_group_name:
    description:
      - "Name of the Remote Copy group."
      - "Required for operations: create, delete, modify, add_volume,
         remove_volume, start, stop, synchronize, admit_target,
         dismiss_target, remote_copy_status"
  domain:
    description:
      - "Specifies the domain in which to create the Remote Copy group.\n
       Used with operation - create"
  remote_copy_targets:
    description:
      - "List of target attributes for the Remote Copy group."
      - "Each target includes: target_name, target_mode, user_cpg, snap_cpg."
      - "Used with operation: create"
  admit_volume_targets:
    description:
      - "List of volume admission targets."
      - "Each entry must include: target_name and sec_volume_name."
      - "At least one target pair is required."
      - "Used with operation: add_volume"
  modify_targets:
    description:
      - "List of target attributes to modify for the Remote Copy group."
      - "Available attributes: target_name, remote_user_cpg, remote_snap_cpg,
         sync_period, rm_sync_period, target_mode, snap_frequency,
         rm_snap_frequency, policies."
      - "Used with operation: modify"
  local_user_cpg:
    description:
      - "Local user CPG (Common Provisioning Group) for auto-created volumes."
      - "Used with operations: create, modify"
  local_snap_cpg:
    description:
      - "Local snapshot CPG for auto-created volumes."
      - "Used with operations: create, modify"
  keep_snap:
    default: false
    description:
      - "When set to true, retains the local volume resynchronization snapshot."
      - "When set to false, the resynchronization snapshot is deleted."
      - "Used with operations: delete, remove_volume"
    type: bool
  unset_user_cpg:
    default: false
    description:
      - "When set to true, unsets the localUserCPG and remoteUserCPG settings."
      - "Used with operation: modify"
    type: bool
  unset_snap_cpg:
    default: false
    description:
      - "When set to true, unsets the localSnapCPG and remoteSnapCPG settings."
      - "Used with operation: modify"
    type: bool
  snapshot_name:
    description:
      - "Optional read-only snapshot name to use as the starting point."
      - "Allows group startup without full resynchronization."
      - "For synchronized groups: synchronizes deltas between this snapshot and the base volume."
      - "For periodic groups: synchronizes deltas between this snapshot and a base snapshot."
      - "Used with operation: add_volume"
  volume_auto_creation:
    default: false
    description:
      - "When set to true, automatically creates secondary volumes on the target."
      - "Uses the CPG associated with the Remote Copy group on the target system."
      - "Cannot be set to true if snapshot_name is specified."
      - "Used with operation: add_volume"
    type: bool
  skip_initial_sync:
    default: false
    description:
      - "When set to true, skips the initial synchronization."
      - "Use this for volumes that have already been presynced with the target."
      - "Cannot be set to true if snapshot_name is specified."
      - "Used with operations: add_volume, start"
    type: bool
  different_secondary_wwn:
    default: false
    description:
      - "When set to true, ensures the secondary volume uses a different WWN."
      - "Only applicable when volume_auto_creation is enabled."
      - "Used with operation: add_volume"
    type: bool
  remove_secondary_volume:
    default: false
    description:
      - "When set to true, deletes the remote volume on the secondary array."
      - "Cannot be used simultaneously with keep_snap."
      - "Used with operation: remove_volume"
    type: bool
  target_name:
    description:
      - "Name of the target system associated with the Remote Copy group."
      - "Used with operations: start, stop, synchronize, admit_link,
         dismiss_link, admit_target, dismiss_target"
  starting_snapshots:
    description:
      - "List of starting snapshots for volume resynchronization."
      - "When specified, must include all volumes in the group."
      - "The starting snapshot for each volume pair is optional."
      - "When omitted, the system performs a full resynchronization."
      - "Used with operation: start"
  no_snapshot:
    default: false
    description:
      - "When set to true, disables snapshot creation in synchronous and periodic modes."
      - "Also deletes existing synchronization snapshots."
      - "Used with operation: stop"
    type: bool
  no_resync_snapshot:
    default: false
    description:
      - "When set to true, prevents saving the resynchronization snapshot."
      - "Only applicable to Remote Copy groups in asynchronous periodic mode."
      - "Used with operation: synchronize"
    type: bool
  full_sync:
    default: false
    description:
      - "When set to true, forces a full synchronization of the Remote Copy group."
      - "Synchronizes even if volumes are already synchronized."
      - "Only applies to groups in synchronous mode."
      - "Useful for resynchronizing volumes that have become inconsistent."
      - "Used with operation: synchronize"
    type: bool
  volume_name:
    description:
      - "Name of the existing virtual volume to add or remove."
      - "Used with operations: add_volume, remove_volume"
  source_port:
    description:
      - "Source port identifier in the format 'node:slot:port'."
      - "Specifies the Ethernet port on the local system."
      - "Used with operations: admit_link, dismiss_link"
  target_port_wwn_or_ip:
    description:
      - "IP address or WWN of the peer port on the target system."
      - "Used with operations: admit_link, dismiss_link"
  target_mode:
    choices:
      - sync
      - periodic
      - async
    description:
      - "Replication mode for the target system."
      - "sync: Synchronous replication."
      - "periodic: Asynchronous periodic replication."
      - "async: Asynchronous streaming replication."
      - "Used with operation: admit_target"
  local_remote_volume_pair_list:
    description:
      - "List of volume pairs for replication."
      - "Each entry is a dictionary with sourceVolumeName and targetVolumeName."
      - "Example: [{'sourceVolumeName':'vol1', 'targetVolumeName':'vol2'}, ...]"
      - "Used with operation: admit_target"
  state:
    choices:
      - present
      - absent
      - modify
      - add_volume
      - remove_volume
      - start
      - stop
      - synchronize
      - admit_link
      - dismiss_link
      - admit_target
      - dismiss_target
      - start_rcopy
      - remote_copy_status
    description:
      - "Desired state or operation for the Remote Copy group."
      - "create: Create a new Remote Copy group."
      - "delete: Delete an existing Remote Copy group."
      - "modify: Modify Remote Copy group settings."
      - "add_volume: Add a volume to the Remote Copy group."
      - "remove_volume: Remove a volume from the Remote Copy group."
      - "start: Start the Remote Copy group."
      - "stop: Stop the Remote Copy group."
      - "synchronize: Synchronize the Remote Copy group."
      - "admit_link: Admit a Remote Copy link."
      - "dismiss_link: Dismiss a Remote Copy link."
      - "admit_target: Admit a Remote Copy target."
      - "dismiss_target: Dismiss a Remote Copy target."
      - "start_rcopy: Start the Remote Copy service."
      - "remote_copy_status: Check Remote Copy group status."
    required: true
  storage_system_ip:
    description:
      - "The storage system IP address.\n"
    required: true
  storage_system_password:
    description:
      - "The storage system password.\n"
    required: true
  storage_system_username:
    description:
      - "The storage system user name.\n"
    required: true

requirements:
  - "HPE Alletra MP OS - 10.5.x "
  - "Ansible 2.9 | 2.10 | 2.11"
  - "hpe_storage_alletramp_ansible"
  - "WSAPI service must be enabled on the storage system"
short_description: "Manage HPE Alletra MP Remote Copy groups"
'''


from ansible.module_utils.basic import AnsibleModule

# Import HPE Storage Ansible Client for interacting with Alletra MP storage systems
try:
    from hpe_storage_flowkit_py.services.src.ansible_service import AnsibleClient
except:
    AnsibleClient = None


def main():
    # Define module parameters and their validation rules for Remote Copy operations
    # Remote Copy supports various operations: create, delete, modify, volume management,
    # group control (start/stop/sync), link management, target management, and service control
    fields = {
        "operation": {
            "required": True,
            "choices": ['create', 'delete', 'modify', 'add_volume', 'remove_volume', 'start', 'stop', 'synchronize', 'admit_link', 
            'dismiss_link','admit_target','dismiss_target', 'start_rcopy', 'remote_copy_status'],
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
        "remote_copy_group_name": {
            "type": "str"
        },
        "domain": {
            "type": "str"
        },
        "remote_copy_targets": {
            "type": "list"
        },
        "modify_targets": {
            "type": "list"
        },
        "admit_volume_targets": {
            "type": "list"
        },
        "local_user_cpg": {
            "type": "str"
        },
        "local_snap_cpg": {
            "type": "str"
        },
        "keep_snap": {
            "type": "bool",
            "default": False
        },
        "unset_user_cpg": {
            "type": "bool",
            "default": False
        },
        "unset_snap_cpg": {
            "type": "bool",
            "default": False
        },
        "snapshot_name": {
            "type": "str"
        },
        "volume_auto_creation": {
            "type": "bool",
            "default": False
        },
        "skip_initial_sync": {
            "type": "bool",
            "default": False
        },
        "different_secondary_wwn": {
            "type": "bool",
            "default": False
        },
        "remove_secondary_volume": {
            "type": "bool",
            "default": False
        },
        "target_name": {
            "type": "str"
        },
        "starting_snapshots": {
            "type": "list"
        },
        "no_snapshot": {
            "type": "bool",
            "default": False
        },
        "no_resync_snapshot": {
            "type": "bool",
            "default": False
        },
        "full_sync": {
            "type": "bool",
            "default": False
        },
        "stop_groups": {
            "type": "bool",
            "default": False
        },
        "volume_name": {
            "type": "str"
        },
        "source_port": {
            "type": "str"
        },
        "target_port_wwn_or_ip": {
            "type": "str"
        },
        "target_mode": {
            "choices": ['sync', 'periodic', 'async'],
            "type": 'str'
        },
        "local_remote_volume_pair_list": {
            "type": "list",
            "default": []
        }
    }
    
    # Initialize Ansible module with parameter specifications
    module = AnsibleModule(argument_spec=fields)

    # Verify that the required HPE Storage client library is available
    if AnsibleClient is None:
        module.fail_json(msg='Python hpe_storage_flowkit_py package is required.')

    # Extract module parameters for Remote Copy operations
    # These parameters control various aspects of Remote Copy group management,
    # including replication configuration, volume management, and synchronization settings
    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]
    remote_copy_group_name = module.params["remote_copy_group_name"]
    domain = module.params["domain"]
    remote_copy_targets = module.params["remote_copy_targets"]
    modify_targets = module.params["modify_targets"]
    admit_volume_targets = module.params["admit_volume_targets"]
    local_user_cpg = module.params["local_user_cpg"]
    local_snap_cpg = module.params["local_snap_cpg"]
    keep_snap = module.params["keep_snap"]
    unset_user_cpg = module.params["unset_user_cpg"]
    unset_snap_cpg = module.params["unset_snap_cpg"]
    snapshot_name = module.params["snapshot_name"]
    volume_auto_creation = module.params["volume_auto_creation"]
    skip_initial_sync = module.params["skip_initial_sync"]
    different_secondary_wwn = module.params["different_secondary_wwn"]
    remove_secondary_volume = module.params["remove_secondary_volume"]
    target_name = module.params["target_name"]
    source_port = module.params["source_port"]
    target_port_wwn_or_ip = module.params["target_port_wwn_or_ip"]
    starting_snapshots = module.params["starting_snapshots"]
    no_snapshot = module.params["no_snapshot"]
    no_resync_snapshot = module.params["no_resync_snapshot"]
    full_sync = module.params["full_sync"]
    volume_name = module.params["volume_name"]
    local_remote_volume_pair_list = module.params["local_remote_volume_pair_list"]
    target_mode = module.params["target_mode"]

    # Initialize the HPE Storage client with connection credentials
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)

    try:
        # Execute the requested Remote Copy operation based on the 'operation' parameter
        # Each operation returns: (success_status, changed_flag, message, issue_details)
        
        # Remote Copy Group Lifecycle Operations
        if module.params["operation"] == "create":
            # Create a new Remote Copy group with specified targets and CPG configuration
            return_status, changed, msg, issue_attr_dict = flowkit_client.create_remote_copy_group(
                remote_copy_group_name,
                domain,
                remote_copy_targets,
                local_user_cpg,
                local_snap_cpg
            )
        elif module.params["operation"] == "delete":
            # Delete an existing Remote Copy group, optionally keeping synchronization snapshots
            return_status, changed, msg, issue_attr_dict = flowkit_client.delete_remote_copy_group(
                remote_copy_group_name,
                keep_snap
            )
        elif module.params["operation"] == "modify":
            # Modify Remote Copy group settings including CPG configuration and target properties
            return_status, changed, msg, issue_attr_dict = flowkit_client.modify_remote_copy_group(
                remote_copy_group_name,
                local_user_cpg,
                local_snap_cpg,
                modify_targets,
                unset_user_cpg,
                unset_snap_cpg
            )
        
        # Volume Management Operations
        elif module.params["operation"] == "add_volume":
            # Add a volume to the Remote Copy group with replication configuration
            return_status, changed, msg, issue_attr_dict = flowkit_client.add_volume_to_remote_copy_group(
                remote_copy_group_name,
                volume_name,
                admit_volume_targets,
                snapshot_name,
                volume_auto_creation,
                skip_initial_sync,
                different_secondary_wwn
            )
        elif module.params["operation"] == "remove_volume":
            # Remove a volume from the Remote Copy group
            # Can optionally keep snapshots or remove the secondary volume
            return_status, changed, msg, issue_attr_dict = flowkit_client.remove_volume_from_remote_copy_group(
                remote_copy_group_name,
                volume_name,
                keep_snap,
                remove_secondary_volume
            )
        # Remote Copy Group Control Operations
        elif module.params["operation"] == "start":
            # Start the Remote Copy group to begin replication
            return_status, changed, msg, issue_attr_dict = flowkit_client.start_remote_copy_group(
                remote_copy_group_name,
                skip_initial_sync,
                target_name,
                starting_snapshots
            )
        elif module.params["operation"] == "stop":
            # Stop the Remote Copy group to halt replication
            return_status, changed, msg, issue_attr_dict = flowkit_client.stop_remote_copy_group(
                remote_copy_group_name,
                no_snapshot,
                target_name
            )
        elif module.params["operation"] == "synchronize":
            # Manually synchronize the Remote Copy group
            return_status, changed, msg, issue_attr_dict = flowkit_client.synchronize_remote_copy_group(
                remote_copy_group_name,
                no_resync_snapshot,
                target_name,
                full_sync
            )
        elif module.params["operation"] == "admit_link":
            # Admit (establish) a Remote Copy link between source and target ports
            return_status, changed, msg, issue_attr_dict = flowkit_client.admit_remote_copy_links(
                target_name,
                source_port,
                target_port_wwn_or_ip
            )
        elif module.params["operation"] == "dismiss_link":
            # Dismiss (remove) a Remote Copy link between source and target ports
            return_status, changed, msg, issue_attr_dict = flowkit_client.dismiss_remote_copy_links(
                target_name,
                source_port,
                target_port_wwn_or_ip
            )
        
        # Remote Copy Service and Target Operations
        elif module.params["operation"] == "start_rcopy":
            # Start the Remote Copy service on the storage system
            return_status, changed, msg, issue_attr_dict = flowkit_client.start_remote_copy_service()
        elif module.params["operation"] == "admit_target":
            # Admit (add) a target system to the Remote Copy group
            return_status, changed, msg, issue_attr_dict = flowkit_client.admit_remote_copy_target(
                remote_copy_group_name,
                target_name,
                target_mode,
                local_remote_volume_pair_list
            )
        elif module.params["operation"] == "dismiss_target":
            # Dismiss (remove) a target system from the Remote Copy group
            return_status, changed, msg, issue_attr_dict = flowkit_client.dismiss_remote_copy_target(
                remote_copy_group_name,
                target_name
            )
        elif module.params["operation"] == "remote_copy_status":
            # Check the status of the Remote Copy group
            return_status, changed, msg, issue_attr_dict = flowkit_client.remote_copy_group_status_check(
                remote_copy_group_name
            )
        
        # Handle operation result and return appropriate response to Ansible
        if return_status:
            # Operation succeeded - include issue details or output if present
            if issue_attr_dict:
                module.exit_json(changed=changed, msg=msg, output=issue_attr_dict)
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
