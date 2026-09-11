#!/usr/bin/python

# Copyright: (c) 2026, HPE Storage Alletra MP Ansible Module

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: alletramp_certs
description:
    - Create, modify, or delete certificates on HPE Alletra MP storage systems
    - Manage SSL/TLS certificates for various services (VASA, WSAPI, SSH, etc.)
    - Supports self-signed certificates, CSR generation, and certificate import
    - Uses the /api/v3/certificates endpoint for certificate management operations
author:
    - HPE Storage Team
requirements:
    - "Alletra MP OS - 10.5.x"
    - "Ansible - 2.9 | 2.10 | 2.11"
    - "hpe_storage_alletramp_ansible"
    - "WSAPI service should be enabled on the HPE Alletra MP."
options:
    operation:
        description: The operation to perform
        required: true
        type: str
        choices: ['create', 'patch', 'delete', 'get', 'get_all']
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
    cert_name:
        description: Certificate name for identification (required for get, patch, delete operations)
        required: false
        type: str
    cert_type:
        description: Type of certificate to create
        required: false
        type: str
        choices: ['selfsigned', 'csr', 'import']
    common_name:
        description: Common name for the certificate (required for selfsigned and csr types)
        required: false
        type: str
    key_length:
        description: Key length (in bits) for the certificate. Mandatory for selfsigned certificates
        required: false
        type: int
        choices: [2048, 3072, 4096]
        default: 2048
    days:
        description: Number of days the certificate should be valid (for selfsigned certificates). Valid range 1-3650 days
        required: false
        type: int
        default: 1095
    country:
        description: Country for the certificate
        required: false
        type: str
    province:
        description: Province/state for the certificate
        required: false
        type: str
    locality:
        description: Locality/city for the certificate
        required: false
        type: str
    organization:
        description: Organization for the certificate
        required: false
        type: str
    organization_unit:
        description: Organization unit for the certificate
        required: false
        type: str
    subject_alt:
        description: Subject Alternative Name for the certificate (e.g., DNS:TestArray,IP:10.1.1.10)
        required: false
        type: str
    authority_chain:
        description: Authority chain for import certificates (PEM format)
        required: false
        type: str
    certificate:
        description: Certificate content for import certificates (PEM format)
        required: false
        type: str
    service:
        description: SSL service name for certificate operations. Valid services are cim, cli, dscc, ekm-client, ekm-server, ldap, qw-client, qw-server, syslog-gen-client, syslog-gen-server, syslog-sec-client, syslog-sec-server, wsapi, and unified-server
        required: false
        type: str
        choices: ['cim', 'cli', 'dscc', 'ekm-client', 'ekm-server', 'ldap', 'qw-client', 'qw-server', 'syslog-gen-client', 'syslog-gen-server', 'syslog-sec-client', 'syslog-sec-server', 'wsapi', 'unified-server']
'''

EXAMPLES = '''
- name: Get all certificates
  alletramp_certs:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get_all

- name: Get certificate information by name
  alletramp_certs:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: get
    cert_name: "TestArray"
  register: cert_info

- name: Create self-signed certificate for unified-server service
  alletramp_certs:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: create
    cert_type: "selfsigned"
    service: "unified-server"
    common_name: "TestArray"
    key_length: 2048  # Mandatory for selfsigned certificates
    days: 1095  # Default value (3 years)
    subject_alt: "DNS:TestArray,IP:10.1.1.10"
    organization_unit: "Unit"
    organization: "My Company"
    locality: "My City"
    province: "Colorado"
    country: "US"

- name: Create CSR certificate
  alletramp_certs:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: create
    cert_type: "csr"
    service: "wsapi"
    common_name: "TestArray"
    key_length: 2048
    organization: "My Company"

- name: Import certificate
  alletramp_certs:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: create
    cert_type: "import"
    service: "wsapi"
    authority_chain: |
      -----BEGIN CERTIFICATE-----
      MIIBkTCB...
      -----END CERTIFICATE-----
    certificate: |
      -----BEGIN CERTIFICATE-----
      MIIDXTCCAkWg...
      -----END CERTIFICATE-----

- name: Finish CSR certificate by providing signed certificate
  alletramp_certs:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: patch
    cert_name: "TestArray"
    authority_chain: |
      -----BEGIN CERTIFICATE-----
      MIIBkTCB...
      -----END CERTIFICATE-----
    certificate: |
      -----BEGIN CERTIFICATE-----
      MIIDXTCCAkWg...
      -----END CERTIFICATE-----

- name: Delete certificate by name
  alletramp_certs:
    storage_system_ip: "x.x.x.x"
    storage_system_username: "username"
    storage_system_password: "password"
    operation: delete
    cert_name: "TestArray"
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
certificate_info:
    description: Certificate information when operation is 'get'
    returned: when operation is 'get'
    type: dict
    contains:
        uid:
            description: Certificate UID
            type: str
        commonname:
            description: Certificate common name
            type: str
        service:
            description: Service name
            type: str
        type:
            description: Certificate type
            type: str
        fingerprint:
            description: Certificate fingerprint
            type: str
        issuer:
            description: Certificate issuer
            type: str
        subject:
            description: Certificate subject
            type: str
        signaturetype:
            description: Certificate signature type
            type: str
certificates:
    description: List of all certificates when operation is 'get_all'
    returned: when operation is 'get_all'
    type: list
issue:
    description: Any issues encountered during operation
    returned: when issues exist
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_service import AnsibleClient
except:
    AnsibleClient = None


def main():
    fields = {
        'operation': {'required': True, 'choices': ['create', 'patch', 'delete', 'get', 'get_all'], 'type': 'str'},
        'storage_system_ip': {'required': True, 'type': 'str'},
        'storage_system_username': {'required': True, 'type': 'str'},
        'storage_system_password': {'required': True, 'type': 'str', 'no_log': True},
        'cert_type': {'type': 'str', 'choices': ['selfsigned', 'csr', 'import']},
        'cert_name': {'type': 'str'},
        'service': {'type': 'str'},
        'common_name': {'type': 'str'},
        'key_length': {'type': 'int', 'choices': [2048, 3072, 4096], 'default': 2048},
        'days': {'type': 'int', 'default': 1095},
        'country': {'type': 'str'},
        'province': {'type': 'str'},
        'locality': {'type': 'str'},
        'organization': {'type': 'str'},
        'organization_unit': {'type': 'str'},
        'subject_alt': {'type': 'str'},
        'authority_chain': {'type': 'str'},
        'certificate': {'type': 'str'}
    }
    
    module = AnsibleModule(argument_spec=fields)

    if AnsibleClient is None:
        module.fail_json(msg='Failed to import AnsibleClient from ansible_service.')

    storage_system_ip = module.params['storage_system_ip']
    storage_system_username = module.params['storage_system_username']
    storage_system_password = module.params['storage_system_password']
    operation = module.params['operation']
    
    flowkit_client = AnsibleClient(storage_system_ip, storage_system_username, storage_system_password)
   
    try:
        if operation == 'create':
            return_status, changed, msg, issue_attr_dict = flowkit_client.create_certificate(
                cert_type=module.params['cert_type'],
                service=module.params['service'],
                common_name=module.params['common_name'],
                key_length=module.params['key_length'],
                days=module.params['days'],
                country=module.params['country'],
                province=module.params['province'],
                locality=module.params['locality'],
                organization=module.params['organization'],
                organization_unit=module.params['organization_unit'],
                subject_alt=module.params['subject_alt'],
                authority_chain=module.params['authority_chain'],
                certificate=module.params['certificate']
            )
        elif operation == 'patch':
            return_status, changed, msg, issue_attr_dict = flowkit_client.patch_certificate_by_name(
                cert_name=module.params['cert_name'],
                authority_chain=module.params['authority_chain'],
                certificate=module.params['certificate']
            )
        elif operation == 'delete':
            return_status, changed, msg, issue_attr_dict = flowkit_client.delete_certificate_by_name(
                module.params['cert_name']
            )
        elif operation == 'get':
            return_status, changed, msg, issue_attr_dict = flowkit_client.get_certificate_by_name(
                module.params['cert_name']
            )
        elif operation == 'get_all':
            return_status, changed, msg, issue_attr_dict = flowkit_client.get_all_certificates()
            
        if return_status:
            result = {'changed': changed, 'msg': msg}
            if issue_attr_dict:
                response = issue_attr_dict.get('response')
                remaining_issue = {
                    key: value for key, value in issue_attr_dict.items()
                    if key != 'response'
                }
                if operation == 'get' and response is not None:
                    result['certificate_info'] = response
                elif operation == 'get_all' and response is not None:
                    if isinstance(response, dict) and 'members' in response:
                        result['certificates'] = list(response['members'].values())
                    elif isinstance(response, list):
                        result['certificates'] = response
                    else:
                        result['certificates'] = [response]

                if remaining_issue:
                    result['issue'] = remaining_issue

            module.exit_json(**result)
        else:
            module.fail_json(msg=msg)
    finally:
        try:
            flowkit_client.logout()
        except Exception:
            pass


if __name__ == '__main__':
    main()