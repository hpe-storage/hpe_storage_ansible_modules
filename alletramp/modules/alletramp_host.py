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
# Note: Removed GENERIC, GENERIC_LEGACY, HPUX_LEGACY, AIX_LEGACY, EGENERA, ONTAP_LEGACY and OPENVMS personas 
# as they are not supported in HPE Alletra 10.5.x version and are deprecated. 
# Only the below mentioned personas are supported.
    fields = {
        "operation": {"required": True, "choices": ['create_host','delete_host','modify_host','add_initiator_chap','remove_initiator_chap','add_target_chap','remove_target_chap','add_fc_path_to_host','remove_fc_path_from_host','add_iscsi_path_to_host','remove_iscsi_path_from_host'], "type": 'str'},
        "storage_system_ip": {"required": True, "type": "str"},
        "storage_system_username": {"required": True, "type": "str", "no_log": True},
        "storage_system_password": {"required": True, "type": "str", "no_log": True},
        "host_name": {"type": "str"},
        "host_domain": {"type": "str"},
        "host_new_name": {"type": "str"},
        "host_fc_wwns": {"type": "list"},
        "host_iscsi_names": {"type": "list"},
        "host_persona": {"required": False, "type": "str",
                         "choices": [
                "GENERIC_ALUA",
                "VMWARE",
                "HPUX",
                "WINDOWS_SERVER",
                "AIX",
                "SOLARIS"]},
        "force_path_removal": {"type": "bool"},
        "chap_name": {"type": "str"},
        "chap_secret": {"type": "str"},
        "chap_secret_hex": {"type": "bool"}
    }

    module = AnsibleModule(argument_spec=fields)

    storage_system_ip = module.params["storage_system_ip"]
    storage_system_username = module.params["storage_system_username"]
    storage_system_password = module.params["storage_system_password"]

    host_name = module.params["host_name"]
    host_new_name = module.params["host_new_name"]
    host_domain = module.params["host_domain"]
    host_fc_wwns = module.params["host_fc_wwns"]
    host_iscsi_names = module.params["host_iscsi_names"]
    host_persona = module.params["host_persona"]
    chap_name = module.params["chap_name"]
    chap_secret = module.params["chap_secret"]
    chap_secret_hex = module.params["chap_secret_hex"]
    force_path_removal = module.params["force_path_removal"]


    if AnsibleClient is None:
        module.fail_json(msg="Failed to import AnsibleClient from ansible_service.")
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)

    # Dispatch operations (functions exit/fail directly)
    try:
        op = module.params["operation"]
        # NOTE: Use keyword arguments to avoid positional drift as client signatures evolve.
        if op == "create_host":
            return_status, changed, msg, issue_attr_dict = flowkit_client.create_host(
                name=host_name,
                iscsiNames=host_iscsi_names,
                FCWwns=host_fc_wwns,
                host_domain=host_domain,
                host_persona=host_persona
            )
        elif op == "modify_host":
            return_status, changed, msg, issue_attr_dict = flowkit_client.modify_host(host_name, host_new_name, persona=host_persona)
        elif op == "delete_host":
            return_status, changed, msg, issue_attr_dict = flowkit_client.delete_host(host_name)
        elif op == "add_initiator_chap":
            return_status, changed, msg, issue_attr_dict = flowkit_client.add_initiator_chap(host_name, chap_name, chap_secret, chap_secret_hex)
        elif op == "remove_initiator_chap":
            return_status, changed, msg, issue_attr_dict = flowkit_client.remove_initiator_chap(host_name)
        elif op == "add_target_chap":
            return_status, changed, msg, issue_attr_dict = flowkit_client.add_target_chap(host_name, chap_name, chap_secret, chap_secret_hex)
        elif op == "remove_target_chap":
            return_status, changed, msg, issue_attr_dict = flowkit_client.remove_target_chap(host_name)
        elif op == "add_fc_path_to_host":
            return_status, changed, msg, issue_attr_dict = flowkit_client.add_fc_path_to_host(host_name, host_fc_wwns)
        elif op == "remove_fc_path_from_host":
            return_status, changed, msg, issue_attr_dict = flowkit_client.remove_fc_path_from_host(host_name, host_fc_wwns, force_path_removal=force_path_removal)
        elif op == "add_iscsi_path_to_host":
            return_status, changed, msg, issue_attr_dict = flowkit_client.add_iscsi_path_to_host(host_name, host_iscsi_names)
        elif op == "remove_iscsi_path_from_host":
            return_status, changed, msg, issue_attr_dict = flowkit_client.remove_iscsi_path_from_host(host_name, host_iscsi_names, force_path_removal=force_path_removal)
        if return_status:
            if issue_attr_dict:
                module.exit_json(changed=changed, msg=msg, issue=issue_attr_dict)
            else:
                module.exit_json(changed=changed, msg=msg)
        else:
            module.fail_json(msg=msg)
    finally:
        try:
            flowkit_client.logout()
        except Exception:
            pass


if __name__ == '__main__':
    main()
