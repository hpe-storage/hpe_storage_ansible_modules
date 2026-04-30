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
from ansible.module_utils.basic import AnsibleModule
try:
    from ansible_service import AnsibleClient
except ImportError:
    AnsibleClient = None


def main():
    fields = {
        "operation": {
            "required": True,
            "choices": [
                "export_volume_to_host",
                "unexport_volume_from_host",
                "export_volumeset_to_host",
                "unexport_volumeset_from_host",
                "export_volume_to_hostset",
                "unexport_volume_from_hostset",
                "export_volumeset_to_hostset",
                "unexport_volumeset_from_hostset",
            ],
            "type": "str",
        },
        "storage_system_ip": {"required": True, "type": "str"},
        "storage_system_username": {"required": True, "type": "str", "no_log": True},
        "storage_system_password": {"required": True, "type": "str", "no_log": True},
        "volume_name": {"required": False, "type": "str"},
        "volume_set_name": {"required": False, "type": "str"},
        "lun": {"type": "int"},
        "autolun": {"type": "bool", "default": False},
        "host_name": {"type": "str"},
        "host_set_name": {"required": False, "type": "str"},
        "node_val": {"type": "int"},
        "slot": {"type": "int"},
        "card_port": {"type": "int"},
    }

    module = AnsibleModule(argument_spec=fields)

    if AnsibleClient is None:
        module.fail_json(msg="Failed to import AnsibleClient from ansible_service.")

    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]

    volume_name = module.params["volume_name"]
    volume_set_name = module.params["volume_set_name"]
    lun = module.params["lun"]
    host_name = module.params["host_name"]
    host_set_name = module.params["host_set_name"]
    node_val = module.params["node_val"]
    slot = module.params["slot"]
    card_port = module.params["card_port"]
    autolun = module.params["autolun"]

    ansible_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)

    try:
        operation = module.params["operation"]
        if operation == "export_volume_to_host":
            return_status, changed, msg, issue_attr_dict = ansible_client.export_volume_to_host(
                volume_name, host_name, lun, node_val, slot, card_port, autolun
            )
        elif operation == "unexport_volume_from_host":
            return_status, changed, msg, issue_attr_dict = ansible_client.unexport_volume_from_host(
                volume_name, host_name, lun, node_val, slot, card_port
            )
        elif operation == "export_volume_to_hostset":
            return_status, changed, msg, issue_attr_dict = ansible_client.export_volume_to_hostset(
                volume_name, host_set_name, lun, node_val, slot, card_port, autolun
            )
        elif operation == "unexport_volume_from_hostset":
            return_status, changed, msg, issue_attr_dict = ansible_client.unexport_volume_from_hostset(
                volume_name, host_set_name, lun, node_val, slot, card_port
            )
        elif operation == "export_volumeset_to_host":
            return_status, changed, msg, issue_attr_dict = ansible_client.export_volumeset_to_host(
                volume_set_name, host_name, lun, node_val, slot, card_port, autolun
            )
        elif operation == "unexport_volumeset_from_host":
            return_status, changed, msg, issue_attr_dict = ansible_client.unexport_volumeset_from_host(
                volume_set_name, host_name, lun, node_val, slot, card_port
            )
        elif operation == "export_volumeset_to_hostset":
            return_status, changed, msg, issue_attr_dict = ansible_client.export_volumeset_to_hostset(
                volume_set_name, host_set_name, lun, node_val, slot, card_port, autolun
            )
        elif operation == "unexport_volumeset_from_hostset":
            return_status, changed, msg, issue_attr_dict = ansible_client.unexport_volumeset_from_hostset(
                volume_set_name, host_set_name, lun, node_val, slot, card_port
            )

        if return_status:
            if issue_attr_dict:
                module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
            else:
                module.exit_json(changed=changed, msg=msg)
        else:
            module.fail_json(msg=msg)
    finally:
        try:
            ansible_client.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()
