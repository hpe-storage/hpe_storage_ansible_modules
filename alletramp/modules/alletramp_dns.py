#!/usr/bin/python

# -*- coding: utf-8 -*-

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
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: alletramp_dns
description:
    - Configure DNS servers, IPv4/IPv6 network settings, and proxy parameters on HPE Alletra MP storage systems
    - Uses the /api/v3/systems/{uid} endpoint with CONFIGURENETWORK action
author:
    - HPE Storage Team
requirements:
    - hpe_storage_flowkit_v3
options:
    operation:
        description: The operation to perform
        required: true
        type: str
        choices: ['configure_network']
    storage_system_ip:
        description: IP address of the storage system
        required: true
        type: str
    storage_system_username:
        description: Username for storage system authentication
        required: true
        type: str
    storage_system_password:
        description: Password for storage system authentication
        required: true
        type: str
        no_log: true
    dns_addresses:
        description: List of DNS server addresses (required, max 3 addresses)
        required: true
        type: list
        elements: str
    ipv4_address:
        description: IPv4 address for the system
        required: false
        type: str
    ipv4_gateway:
        description: IPv4 gateway address (required if ipv4_address is specified)
        required: false
        type: str
    ipv4_subnet_mask:
        description: IPv4 subnet mask (required if ipv4_address is specified)
        required: false
        type: str
    ipv6_address:
        description: IPv6 address for the system
        required: false
        type: str
    ipv6_gateway:
        description: IPv6 gateway address (required if ipv6_address is specified)
        required: false
        type: str
    ipv6_prefix_len:
        description: IPv6 prefix length (required if ipv6_address is specified)
        required: false
        type: str
    proxy_server:
        description: Proxy server hostname/IP
        required: false
        type: str
    proxy_port:
        description: Proxy server port (1-65535)
        required: false
        type: int
    proxy_protocol:
        description: Proxy protocol
        required: false
        type: str
        choices: ['HTTP', 'NTLM']
    proxy_authentication_required:
        description: Is proxy authentication required
        required: false
        type: str
        choices: ['enabled', 'disabled']
    proxy_user:
        description: Username for proxy authentication
        required: false
        type: str
    proxy_password:
        description: Password for proxy authentication
        required: false
        type: str
        no_log: true
    proxy_user_domain:
        description: User domain for NTLM authentication
        required: false
        type: str
    commit_change:
        description: Whether to commit network changes
        required: false
        type: bool
    slaac_enable:
        description: Enable/disable IPv6 SLAAC
        required: false
        type: bool
'''

EXAMPLES = '''
- name: Configure IPv4 network with DNS
  alletramp_dns:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: configure_network
    dns_addresses:
      - "x.x.x.x"
      - "x.x.x.x"
      - "x.x.x.x"
    ipv4_address: "x.x.x.x"
    ipv4_gateway: "x.x.x.x"
    ipv4_subnet_mask: "x.x.x.x"
    commit_change: true

- name: Configure IPv6 network with DNS
  alletramp_dns:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: configure_network
    dns_addresses:
      - "x.x.x.x"
      - "x.x.x.x"
    ipv6_address: "x:x::x"
    ipv6_gateway: "x:x::x"
    ipv6_prefix_len: "x"
    slaac_enable: true
    commit_change: true

- name: Configure network with HTTP proxy
  alletramp_dns:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: configure_network
    dns_addresses:
      - "x.x.x.x"
    ipv4_address: "x.x.x.x"
    ipv4_gateway: "x.x.x.x"
    ipv4_subnet_mask: "x.x.x.x"
    proxy_server: "proxy.example.com"
    proxy_port: port
    proxy_protocol: "HTTP"
    proxy_authentication_required: "enabled"
    proxy_user: "proxyuser"
    proxy_password: "proxypass"
    commit_change: true
'''

RETURN = '''
msg:
    description: Success/failure message
    returned: always
    type: str
changed:
    description: Whether the operation changed the system state
    returned: always
    type: bool
issue:
    description: Any issues encountered during operation
    returned: when issues exist
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from ansible_service import AnsibleClient
except ImportError:
    AnsibleClient = None


def main():
    fields = {
        'operation': {'required': True, 'choices': ['configure_network'], 'type': 'str'},
        'storage_system_ip': {'required': True, 'type': 'str'},
        'storage_system_username': {'required': True, 'type': 'str', 'no_log': True},
        'storage_system_password': {'required': True, 'type': 'str', 'no_log': True},
        'dns_addresses': {'required': True, 'type': 'list', 'elements': 'str'},
        'ipv4_address': {'type': 'str'},
        'ipv4_gateway': {'type': 'str'},
        'ipv4_subnet_mask': {'type': 'str'},
        'ipv6_address': {'type': 'str'},
        'ipv6_gateway': {'type': 'str'},
        'ipv6_prefix_len': {'type': 'str'},
        'proxy_server': {'type': 'str'},
        'proxy_port': {'type': 'int'},
        'proxy_protocol': {'type': 'str', 'choices': ['HTTP', 'NTLM']},
        'proxy_authentication_required': {'type': 'str', 'choices': ['enabled', 'disabled']},
        'proxy_user': {'type': 'str'},
        'proxy_password': {'type': 'str', 'no_log': True},
        'proxy_user_domain': {'type': 'str'},
        'commit_change': {'type': 'bool'},
        'slaac_enable': {'type': 'bool'}
    }
    
    module = AnsibleModule(argument_spec=fields)

    if AnsibleClient is None:
        module.fail_json(msg='Failed to import AnsibleClient from ansible_service.')

    storage_system_ip = module.params['storage_system_ip']
    storage_system_username = module.params['storage_system_username']
    storage_system_password = module.params['storage_system_password']
    dns_addresses = module.params['dns_addresses']
    ipv4_address = module.params['ipv4_address']
    ipv4_gateway = module.params['ipv4_gateway']
    ipv4_subnet_mask = module.params['ipv4_subnet_mask']
    ipv6_address = module.params['ipv6_address']
    ipv6_gateway = module.params['ipv6_gateway']
    ipv6_prefix_len = module.params['ipv6_prefix_len']
    proxy_server = module.params['proxy_server']
    proxy_port = module.params['proxy_port']
    proxy_protocol = module.params['proxy_protocol']
    proxy_authentication_required = module.params['proxy_authentication_required']
    proxy_user = module.params['proxy_user']
    proxy_password = module.params['proxy_password']
    proxy_user_domain = module.params['proxy_user_domain']
    commit_change = module.params['commit_change']
    slaac_enable = module.params['slaac_enable']

    flowkit_client = None

    # Build proxy parameters if any proxy settings are provided
    proxy_params = None
    if (proxy_server or proxy_port or proxy_protocol or proxy_authentication_required or 
        proxy_user or proxy_password or proxy_user_domain):
        proxy_params = {}
        if proxy_server:
            proxy_params['proxyServer'] = proxy_server
        if proxy_port:
            proxy_params['proxyPort'] = proxy_port
        if proxy_protocol:
            proxy_params['proxyProtocol'] = proxy_protocol
        if proxy_authentication_required:
            proxy_params['authenticationRequired'] = proxy_authentication_required
        if proxy_user:
            proxy_params['proxyUser'] = proxy_user
        if proxy_password:
            proxy_params['proxyPassword'] = proxy_password
        if proxy_user_domain:
            proxy_params['proxyUserDomain'] = proxy_user_domain

    try:
        flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
    except Exception as e:
        module.fail_json(msg=str(e))
   
    try:
        operation = module.params['operation']
        if operation == 'configure_network':
            # Cast IPv6 prefix length to int if provided
            ipv6_prefix_len_cast = None
            if ipv6_prefix_len is not None:
                try:
                    ipv6_prefix_len_cast = int(ipv6_prefix_len)
                except Exception:
                    module.fail_json(msg="ipv6_prefix_len must be an integer")
            
            try:
                return_status, changed, msg, issue_attr_dict = flowkit_client.configure_network(
                    dns_addresses=dns_addresses,
                    ipv4_address=ipv4_address,
                    ipv4_gateway=ipv4_gateway,
                    ipv4_subnet_mask=ipv4_subnet_mask,
                    ipv6_address=ipv6_address,
                    ipv6_gateway=ipv6_gateway,
                    ipv6_prefix_len=ipv6_prefix_len_cast if ipv6_prefix_len is not None else ipv6_prefix_len,
                    proxy_params=proxy_params,
                    commit_change=commit_change,
                    slaac_enable=slaac_enable
                )
            except Exception as e:
                module.fail_json(msg=str(e))
        
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
