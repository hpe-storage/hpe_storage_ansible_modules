<!--
(c) Copyright 2026 Hewlett Packard Enterprise Development LP  
All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
-->

# HPE Storage MP Ansible Modules Documentation for Alletra MP

This document provides comprehensive documentation for HPE Storage Ansible modules for Alletra MP

---

## Table of Contents

1. [alletramp_cpg](#alletramp_cpg) - Common Provisioning Groups
2. [alletramp_dns](#alletramp_dns) - DNS and Network Configuration
3. [alletramp_host](#alletramp_host) - Host Management
4. [alletramp_hostset](#alletramp_hostset) - Host Set Management
5. [alletramp_ntp](#alletramp_ntp) - NTP and Date/Time Configuration
6. [alletramp_offline_clone](#alletramp_offline_clone) - Offline Clone Management
7. [alletramp_online_clone](#alletramp_online_clone) - Online Clone Management
8. [alletramp_qos](#alletramp_qos) - Quality of Service Management
9. [alletramp_remote_copy](#alletramp_remote_copy) - Remote Copy Replication
10. [alletramp_snapshot](#alletramp_snapshot) - Snapshot Management
11. [alletramp_user](#alletramp_user) - User Account Management
12. [alletramp_vlun](#alletramp_vlun) - VLUN Export Management
13. [alletramp_volume](#alletramp_volume) - Volume Management
14. [alletramp_volumeset](#alletramp_volumeset) - Volume Set Management

---

# alletramp_cpg

Manage Common Provisioning Groups (CPGs) on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a new CPG with growth and HA settings |
| `delete` | Delete an existing CPG from the storage array |

---

## Operation Methods

### create

Create a new Common Provisioning Group (CPG) that serves as a storage pool for volume allocation.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cpg_name` | str | Name of the CPG to create |

**Optional Attributes**

| Parameter | Type | Default | Choices | Description |
|-----------|------|---------|---------|-------------|
| `domain` | str | - | - | Domain for the CPG |
| `growth_increment` | float | -1.0 | - | Growth increment size (auto-grow amount) |
| `growth_increment_unit` | str | `GiB` | `MiB`, `GiB`, `TiB` | Unit for growth increment |
| `growth_limit` | float | -1.0 | - | Maximum growth limit (-1.0 = unlimited) |
| `growth_limit_unit` | str | `GiB` | `MiB`, `GiB`, `TiB` | Unit for growth limit |
| `growth_warning` | float | -1.0 | - | Warning threshold for space usage |
| `growth_warning_unit` | str | `GiB` | `MiB`, `GiB`, `TiB` | Unit for warning threshold |
| `high_availability` | str | - | `HAJBOD_JBOD`, `HAJBOD_DISK` | High availability configuration |
| `cage` | str | - | - | Cage restrictions (e.g., "0,1" or "0-3") |
| `position` | str | - | - | Position restrictions for disk allocation |
| `keyValuePairs` | dict | - | - | Custom metadata key-value pairs (keys must start with v3_, dp_, or dscc_) |

---

### delete

Delete an existing CPG from the storage array. The CPG must not contain any volumes.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cpg_name` | str | Name of the CPG to delete |

---

**Examples**

```yaml
- name: Create CPG
  alletramp_cpg:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    cpg_name: "SSD_CPG"
    growth_increment: 8
    growth_increment_unit: "GiB"
    growth_limit: 100
    growth_limit_unit: "GiB"
    high_availability: "HAJBOD_DISK"
```

```yaml
- name: Delete CPG
  alletramp_cpg:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete
    cpg_name: "SSD_CPG"
```

**Notes**

- CPGs are storage pools from which volumes are allocated
- CPG must exist before creating volumes
- Deleting a CPG requires all volumes in it to be deleted first

---

# alletramp_dns

Configure DNS and network settings on HPE Alletra MP storage arrays.

**Note:** This module currently supports IPv4 network configuration and HTTP proxy settings only. IPv6 and NTLM proxy support are not available in this version.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `configure_network` | Configure DNS servers, IPv4 network settings, and HTTP proxy parameters |

---

## Operation Methods

### configure_network

Configure DNS servers and network parameters for the HPE Alletra MP storage array. This operation allows configuration of DNS addresses, IPv4 network settings, and HTTP proxy server parameters.

**Required Attributes:**

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `dns_addresses` | list | List of DNS server IP addresses (maximum 3) | - |

**Optional Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `ipv4_address` | str | IPv4 address for the array (required if configuring IPv4) |
| `ipv4_gateway` | str | IPv4 gateway address (required if configuring IPv4) |
| `ipv4_subnet_mask` | str | IPv4 subnet mask (required if configuring IPv4) |
| `proxy_server` | str | Proxy server address |
| `proxy_port` | int | Proxy server port (1-65535) |
| `proxy_protocol` | str | Proxy protocol type (only `HTTP` is supported) |
| `proxy_authentication_required` | str | Enable proxy authentication (`enabled`, `disabled`) |
| `proxy_user` | str | Proxy authentication username (Required only when proxy_aunthentication_required is "enabled") |
| `proxy_password` | str | Proxy authentication password (Required only when proxy_aunthentication_required is "enabled") |
| `commit_change` | bool | Commit changes immediately |

**Note:** When configuring IPv4, all three parameters (`ipv4_address`, `ipv4_gateway`, `ipv4_subnet_mask`) must be provided together.

---

## Examples

```yaml
# Configure DNS with IPv4 network settings
- name: Configure DNS and IPv4 network
  alletramp_dns:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: configure_network
    dns_addresses:
      - "8.8.8.8"
      - "8.8.4.4"
    ipv4_address: "10.10.10.100"
    ipv4_gateway: "10.10.10.1"
    ipv4_subnet_mask: "255.255.255.0"
    commit_change: true

# Configure DNS with proxy settings
- name: Configure DNS with HTTP proxy
  alletramp_dns:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: configure_network
    dns_addresses:
      - "8.8.8.8"
      - "8.8.4.4"
    ipv4_address: "10.10.10.100"
    ipv4_gateway: "10.10.10.1"
    ipv4_subnet_mask: "255.255.255.0"
    proxy_server: "proxy.example.com"
    proxy_port: 8080
    proxy_protocol: "HTTP"
    proxy_authentication_required: "enabled"
    proxy_user: "proxy_admin"
    proxy_password: "proxy_pass"
```

---

# alletramp_host

Manage hosts on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create_host` | Create a new host with FC or iSCSI initiators |
| `delete_host` | Delete an existing host from the storage array |
| `modify_host` | Modify host properties such as persona or name |
| `add_initiator_chap` | Add CHAP authentication for iSCSI initiators |
| `remove_initiator_chap` | Remove CHAP authentication from initiators |
| `add_target_chap` | Add target CHAP authentication |
| `remove_target_chap` | Remove target CHAP authentication |
| `add_fc_path_to_host` | Add Fibre Channel path to host |
| `remove_fc_path_from_host` | Remove Fibre Channel path from host |
| `add_iscsi_path_to_host` | Add iSCSI path to host |
| `remove_iscsi_path_from_host` | Remove iSCSI path from host |

**Note:** This module supports only iSCSI and Fibre Channel (FC) initiator paths.

---

## Operation Methods

### create_host

Create a new host with Fibre Channel or iSCSI initiators. Hosts represent physical or virtual servers that will access volumes on the storage array.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host to create |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_fc_wwns` | list | List of Fibre Channel WWNs (e.g., "50:01:43:80:12:34:56:78") |
| `host_iscsi_names` | list | List of iSCSI initiator names (e.g., "iqn.1991-05.com.example:host01") |
| `host_domain` | str | Domain in which to create the host |
| `host_persona` | str | Host persona (`GENERIC_ALUA`, `VMWARE`, `HPUX`, `WINDOWS_SERVER`, `AIX`, `SOLARIS`) |

---

### delete_host

Delete an existing host from the storage array. The host must not have any active VLUNs (volume exports).

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host to delete |

---

### modify_host

Modify host properties such as the host persona or rename the host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host to modify |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_new_name` | str | New name for the host |
| `host_persona` | str | New host persona |

---

### add_initiator_chap

Add CHAP (Challenge-Handshake Authentication Protocol) authentication for iSCSI initiators.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host |
| `chap_name` | str | CHAP username |
| `chap_secret` | str | CHAP secret/password |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `chap_secret_hex` | bool | If true, chap_secret is treated as hexadecimal |

---

### remove_initiator_chap

Remove CHAP authentication from iSCSI initiators.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host |

---

### add_target_chap

Add target CHAP authentication for mutual CHAP (bidirectional authentication).

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host |
| `chap_name` | str | Target CHAP username |
| `chap_secret` | str | Target CHAP secret/password |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `chap_secret_hex` | bool | If true, chap_secret is treated as hexadecimal |

---

### remove_target_chap

Remove target CHAP authentication.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host |

---

### add_fc_path_to_host

Add Fibre Channel WWN paths to an existing host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host |
| `host_fc_wwns` | list | List of FC WWNs to add |

---

### remove_fc_path_from_host

Remove Fibre Channel WWN paths from a host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host |
| `host_fc_wwns` | list | List of FC WWNs to remove |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `force_path_removal` | bool | Force removal even if VLUNs are exported |

---

### add_iscsi_path_to_host

Add iSCSI initiator paths to an existing host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host |
| `host_iscsi_names` | list | List of iSCSI names to add |

---

### remove_iscsi_path_from_host

Remove iSCSI initiator paths from a host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `host_name` | str | Name of the host |
| `host_iscsi_names` | list | List of iSCSI names to remove |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `force_path_removal` | bool | Force removal even if VLUNs are exported |

---

**Examples**

```yaml
- name: Create FC host
  alletramp_host:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create_host
    host_name: "esxi_host_01"
    host_fc_wwns:
      - "50:01:43:80:12:34:56:78"
    host_persona: "VMWARE"
```

```yaml
- name: Delete host
  alletramp_host:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete_host
    host_name: "esxi_host_01"
```

```yaml
- name: Modify host persona
  alletramp_host:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: modify_host
    host_name: "esxi_host_01"
    host_persona: "GENERIC_ALUA"
```

```yaml
- name: Add CHAP authentication
  alletramp_host:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: add_initiator_chap
    host_name: "linux_host_01"
    chap_name: "chapuser"
    chap_secret: "chappassword123"
```

---

# alletramp_hostset

Manage host sets on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a new host set with member hosts |
| `delete` | Delete an existing host set |
| `add_hosts` | Add hosts to an existing host set |
| `remove_hosts` | Remove hosts from a host set |

---

## Operation Methods

### create

Create a new host set with optional initial member hosts. Host sets allow you to group hosts together for simplified volume export management.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `hostset_name` | str | Name of the host set to create |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `domain` | str | Domain in which to create the host set |
| `setmembers` | list | Initial list of host names to add to the set |

---

### delete

Delete an existing host set from the storage array. The host set must not have any active VLUNs.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `hostset_name` | str | Name of the host set to delete |

---

### add_hosts

Add one or more hosts to an existing host set.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `hostset_name` | str | Name of the host set |
| `setmembers` | list | List of host names to add |

---

### remove_hosts

Remove one or more hosts from an existing host set.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `hostset_name` | str | Name of the host set |
| `setmembers` | list | List of host names to remove |

---

**Examples**

```yaml
- name: Create host set
  alletramp_hostset:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    hostset_name: "web_servers"
    setmembers:
      - "web01"
      - "web02"
```

```yaml
- name: Add hosts to host set
  alletramp_hostset:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: add_hosts
    hostset_name: "web_servers"
    setmembers:
      - "web03"
```

```yaml
- name: Remove hosts from host set
  alletramp_hostset:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: remove_hosts
    hostset_name: "web_servers"
    setmembers:
      - "web01"
```

```yaml
- name: Delete host set
  alletramp_hostset:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete
    hostset_name: "web_servers"
```

---

# alletramp_ntp

Configure date/time and NTP servers on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `configure_datetime` | Configure system date/time manually or via NTP servers |

---

## Operation Methods

### configure_datetime

Configure date and time settings for the HPE Alletra MP storage array. You can either set the time manually using `date_time` parameter or configure NTP servers using `ntp_addresses` parameter. These two options are mutually exclusive - you must specify exactly one.

**Required Attributes:**

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `timezone` | str | Timezone identifier (e.g., "Asia/Kolkata", "US/Samoa") | - |
 

**Mutually Exclusive Attributes (choose one):**

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `date_time` | str | Manual date and time setting in "MM/dd/yyyy HH:mm:ss" format | - |
| `ntp_addresses` | list | List of NTP server addresses for automatic time synchronization | - |

**Note:** You must specify either `date_time` OR `ntp_addresses`, but not both. If configuring NTP, the system will automatically synchronize time with the specified servers. If setting time manually, provide the datetime in "MM/dd/yyyy HH:mm:ss" format.

---

## Examples

```yaml
# Configure NTP servers for automatic time synchronization
- name: Configure NTP servers
  alletramp_ntp:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: configure_datetime
    timezone: "Asia/Kolkata"
    ntp_addresses:
      - "time.nist.gov"
      - "time.google.com"
      - "pool.ntp.org"

# Set date and time manually
- name: Set system time manually
  alletramp_ntp:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: configure_datetime
    timezone: "Asia/Kolkata"
    date_time: "02/11/2026 12:53:30"
```

---

# alletramp_offline_clone

Manage offline clones on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a full physical copy of a volume |
| `delete` | Delete an existing offline clone |
| `resync` | Resynchronize clone with parent volume |
| `stop` | Stop an ongoing offline clone operation |

---

## Operation Methods

### create

Create an offline clone (full physical copy) of a volume. Offline clones create independent, writable copies that can be used for backup, testing, or disaster recovery scenarios.

**Required Attributes**

| Attribute | Type | Description |
|-----------|------|-------------|
| `clone_name` | str | Name for the clone volume |
| `base_volume_name` | str | Source volume to clone |

**Optional Attributes**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `dest_cpg` | str | - | Destination CPG for the clone |
| `priority` | str | `PRIORITYTYPE_MED` | Copy operation priority: `PRIORITYTYPE_HIGH`, `PRIORITYTYPE_MED`, `PRIORITYTYPE_LOW` |
| `skip_zero` | bool | - | Copy only allocated portions from thin provisioned source |
| `enableResync` | bool | - | Enable resynchronization using saved snapshot |
| `reduce` | bool | - | Create deduplicated and compressed volume |
| `selectionType` | str | - | Volume selection type: `PARENTVV_INDEX`, `PARENTVV_PREFIX` |
| `expiration_time` | int | - | Expiration time value |
| `expiration_unit` | str | `hours` | Expiration time unit: `hours` or `days` |
| `retention_time` | int | - | Retention time value |
| `retention_unit` | str | `hours` | Retention time unit: `hours` or `days` |
| `appSetBusinessUnit` | str | - | Business unit for application using the set |
| `appSetComments` | str | - | Comments about volume set |
| `appSetExcludeAIQoS` | str | - | Exclude set from AIQOS: `yes`, `no` |
| `appSetImportance` | str | - | Volume set importance |
| `appSetType` | str | - | Application type using the set |

---

### delete

Delete an offline clone. This operation permanently removes the clone volume from the storage array.

**Required Attributes**

| Attribute | Type | Description |
|-----------|------|-------------|
| `clone_name` | str | Name of the clone to delete |
| `base_volume_name` | str | Parent volume name |

**Optional Attributes**

None

---

### resync

Resynchronize clone with parent volume using saved snapshot. Only changes since the last synchronization are copied, making this operation more efficient than recreating the clone.

**Required Attributes**

| Attribute | Type | Description |
|-----------|------|-------------|
| `clone_name` | str | Name of the clone to resync |
| `base_volume_name` | str | Parent volume name |

**Optional Attributes**

None

---

### stop

Stop an ongoing offline clone operation. This halts the copy process and may leave the clone in an incomplete state.

**Required Attributes**

| Attribute | Type | Description |
|-----------|------|-------------|
| `clone_name` | str | Name of the clone operation to stop |
| `base_volume_name` | str | Parent volume name |

**Optional Attributes**

None

---

**Examples**

**Create Basic Offline Clone:**

```yaml
- name: Create offline clone
  alletramp_offline_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    clone_name: "prod_vol_fullcopy"
    base_volume_name: "prod_vol_001"
    dest_cpg: "SSD_CPG"
    priority: "PRIORITYTYPE_MED"
```

**Create Clone with Data Reduction:**

```yaml
- name: Create reduced offline clone
  alletramp_offline_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    clone_name: "backup_clone_001"
    base_volume_name: "prod_vol_001"
    dest_cpg: "FC_CPG"
    reduce: true
    skip_zero: true
```

**Resync Clone:**

```yaml
- name: Resync offline clone
  alletramp_offline_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: resync
    clone_name: "prod_vol_fullcopy"
    base_volume_name: "prod_vol_001"
```

**Stop Clone Operation:**

```yaml
- name: Stop offline clone operation
  alletramp_offline_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: stop
    clone_name: "prod_vol_fullcopy"
    base_volume_name: "prod_vol_001"
```

**Delete Clone:**

```yaml
- name: Delete offline clone
  alletramp_offline_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete
    clone_name: "prod_vol_fullcopy"
    base_volume_name: "prod_vol_001"
```

---

# alletramp_online_clone

Manage online clones on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a thin provisioned online clone |
| `delete` | Delete an existing online clone |

---

## Operation Methods

### create

Create an online clone (thin provisioned copy) of a volume. Online clones use snapshots for fast, space-efficient cloning and remain available during the cloning process.

**Required Attributes**

| Attribute | Type | Description |
|-----------|------|-------------|
| `clone_name` | str | Name for the clone volume |
| `base_volume_name` | str | Source volume to clone |
| `dest_cpg` | str | Destination CPG for the clone |

**Optional Attributes**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `reduce` | bool | - | Create deduplicated and compressed volume |
| `addToSet` | str | - | Add volume copies to specified volume set |
| `selectionType` | str | - | Volume selection type: `PARENTVV_INDEX`, `PARENTVV_PREFIX` |
| `expiration_time` | int | - | Expiration time value |
| `expiration_unit` | str | `hours` | Expiration time unit: `seconds` or `minutes` or `hours` or `days` |
| `retention_time` | int | - | Retention time value |
| `retention_unit` | str | `hours` | Retention time unit: `seconds` or `minutes` or `hours` or `days` |
| `bulkvv` | bool | - | Make target volume VMware specific |
| `appSetBusinessUnit` | str | - | Business unit for application using the set |
| `appSetComments` | str | - | Comments about volume set |
| `appSetExcludeAIQoS` | str | - | Exclude set from AIQOS: `yes`, `no` |
| `appSetImportance` | str | - | Volume set importance |
| `appSetType` | str | - | Application type using the set |

Note: skip_zero is not supported for online clone.

---

### delete

Delete an online clone. This operation permanently removes the clone volume from the storage array.

**Required Attributes**

| Attribute | Type | Description |
|-----------|------|-------------|
| `clone_name` | str | Name of the clone to delete |
| `base_volume_name` | str | Parent volume name |

**Optional Attributes**

None

---

**Examples**

**Create Basic Online Clone:**

```yaml
- name: Create online clone
  alletramp_online_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    clone_name: "prod_vol_clone"
    base_volume_name: "prod_vol_001"
    dest_cpg: "SSD_CPG"
```

**Create Clone with Data Reduction:**

```yaml
- name: Create reduced online clone
  alletramp_online_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    clone_name: "backup_clone_001"
    base_volume_name: "prod_vol_001"
    dest_cpg: "FC_CPG"
    reduce: true
```

**Create Clone with Expiration:**

```yaml
- name: Create online clone with expiration
  alletramp_online_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    clone_name: "temp_clone_001"
    base_volume_name: "prod_vol_001"
    dest_cpg: "SSD_CPG"
    expiration_time: 48
    expiration_unit: "hours"
```

**Delete Clone:**

```yaml
- name: Delete online clone
  alletramp_online_clone:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete
    clone_name: "prod_vol_clone"
    base_volume_name: "prod_vol_001"
```

---

# alletramp_qos

Manage QoS (Quality of Service) policies on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create_qos` | Create a new QoS rule with IOPS and bandwidth limits |
| `modify_qos` | Modify an existing QoS rule |
| `delete_qos` | Delete a QoS rule |
| `get_qos` | Retrieve details of a specific QoS rule |
| `list_qos` | List all QoS rules on the storage array |

---

## Operation Methods

### create_qos

Create a new QoS rule to limit IOPS and bandwidth for volumes, volume sets, domains, or the entire system.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `targetName` | str | Name of the target (volume, volume set, domain, all) |
| `targetType` | str | Type: `QOS_TGT_VV`, `QOS_TGT_VVSET`, `QOS_TGT_DOMAIN`, or `QOS_TGT_SYSTEM` |

Note: "targetName" should be set to "all" only when "targetType" is set to "QOS_TGT_SYSTEM"

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `iopsMaxLimit` | int | Maximum IOPS limit |
| `bandwidthMaxLimitKiB` | int | Maximum bandwidth in KiB/s |
| `enable` | bool | Enable the QoS rule (default: false) |
| `allowAIQoS` | bool | Force allow even if AI QoS is enabled |

---

### modify_qos

Modify an existing QoS rule's IOPS or bandwidth limits.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `targetName` | str | Name of the target with existing QoS rule |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `iopsMaxLimit` | int | New maximum IOPS limit |
| `bandwidthMaxLimitKiB` | int | New maximum bandwidth in KiB/s |
| `enable` | bool | Enable or disable the rule |
| `allowAIQoS` | bool | Flag to force allow QoS rules even if Intelligent QoS is enabled |

---

### delete_qos

Delete an existing QoS rule from the target.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `targetName` | str | Name of the target to remove QoS from |

---

### get_qos

Retrieve details of a specific QoS rule.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `targetName` | str | Name of the target to query |

---

### list_qos

List all QoS rules configured on the storage array.

**Required Attributes**

None - this operation lists all QoS rules.

---

**Examples**

```yaml
- name: Create QoS rule for volume set
  alletramp_qos:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create_qos
    targetType: "QOS_TGT_VVSET"
    targetName: "web_volumes"
    iopsMaxLimit: 50000
    bandwidthMaxLimitKiB: 512000
    enable: true
```

```yaml
- name: Modify QoS limits
  alletramp_qos:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: modify_qos
    targetName: "web_volumes"
    iopsMaxLimit: 75000
    bandwidthMaxLimitKiB: 768000
```

```yaml
- name: Delete QoS rule
  alletramp_qos:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete_qos
    targetName: "web_volumes"
```

```yaml
- name: List all QoS rules
  alletramp_qos:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: list_qos
```

---

# alletramp_remote_copy

Manage remote copy replication on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a new remote copy group |
| `delete` | Delete an existing remote copy group |
| `modify` | Modify remote copy group settings |
| `add_volume` | Add a volume to a remote copy group |
| `remove_volume` | Remove a volume from a remote copy group |
| `start` | Start replication for a remote copy group |
| `stop` | Stop replication for a remote copy group |
| `synchronize` | Manually synchronize a remote copy group |
| `admit_link` | Admit (establish) a remote copy link |
| `dismiss_link` | Dismiss (remove) a remote copy link |
| `admit_target` | Admit (add) a target system to the remote copy group |
| `dismiss_target` | Dismiss (remove) a target system from the remote copy group |
| `start_rcopy` | Start the remote copy service |
| `remote_copy_status` | Check remote copy group status |

---

## Operation Methods

### create

Create a new remote copy group with specified targets and CPG configuration for data replication.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group to create |
| `remote_copy_targets` | list | List of target attributes for the remote copy group |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `domain` | str | Domain in which to create the remote copy group |
| `local_user_cpg` | str | Local user CPG for auto-created volumes |
| `local_snap_cpg` | str | Local snapshot CPG for auto-created volumes |

**remote_copy_targets Sub-parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_name` | str | Name of the target system |
| `target_mode` | str | Replication mode (`sync`, `periodic`, `async`) |
| `user_cpg` | str | User CPG on target system |
| `snap_cpg` | str | Snapshot CPG on target system |

---

### delete

Delete an existing remote copy group from the storage array.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group to delete |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keep_snap` | bool | `false` | Retain the local volume resynchronization snapshot |

---

### modify

Modify remote copy group settings including CPG configuration and target properties.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group to modify |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `local_user_cpg` | str | - | Updated local user CPG |
| `local_snap_cpg` | str | - | Updated local snapshot CPG |
| `modify_targets` | list | - | List of target attributes to modify |
| `unset_user_cpg` | bool | `false` | Unset the local and remote user CPG settings |
| `unset_snap_cpg` | bool | `false` | Unset the local and remote snap CPG settings |

---

### add_volume

Add a volume to the remote copy group with replication configuration.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group |
| `volume_name` | str | Name of the volume to add |
| `admit_volume_targets` | list | List of volume admission targets |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `snapshot_name` | str | - | Read-only snapshot name as starting point |
| `volume_auto_creation` | bool | `false` | Automatically create secondary volumes on target |
| `skip_initial_sync` | bool | `false` | Skip initial synchronization |
| `different_secondary_wwn` | bool | `false` | Ensure secondary volume uses different WWN |

**admit_volume_targets Sub-parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_name` | str | Name of the target system |
| `sec_volume_name` | str | Name of the secondary volume on target |

---

### remove_volume

Remove a volume from the remote copy group.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group |
| `volume_name` | str | Name of the volume to remove |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keep_snap` | bool | `false` | Retain the resynchronization snapshot |
| `remove_secondary_volume` | bool | `false` | Delete the remote volume on secondary array |

---

### start

Start the remote copy group to begin replication.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group to start |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_name` | str | - | Name of specific target to start |
| `skip_initial_sync` | bool | `false` | Skip initial synchronization |
| `starting_snapshots` | list | - | List of starting snapshots for resynchronization |

---

### stop

Stop the remote copy group to halt replication.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group to stop |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_name` | str | - | Name of specific target to stop |
| `no_snapshot` | bool | `false` | Disable snapshot creation and delete existing snapshots |

---

### synchronize

Manually synchronize the remote copy group.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group to synchronize |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_name` | str | - | Name of specific target to synchronize |
| `no_resync_snapshot` | bool | `false` | Prevent saving resynchronization snapshot |
| `full_sync` | bool | `false` | Force full synchronization |

---

### admit_link

Admit (establish) a remote copy link between source and target ports.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_name` | str | Name of the target system |
| `source_port` | str | Source port identifier (format: 'node:slot:port') |
| `target_port_wwn_or_ip` | str | IP address or WWN of the peer port on target |

---

### dismiss_link

Dismiss (remove) a remote copy link between source and target ports.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_name` | str | Name of the target system |
| `source_port` | str | Source port identifier (format: 'node:slot:port') |
| `target_port_wwn_or_ip` | str | IP address or WWN of the peer port on target |

---

### admit_target

Admit (add) a target system to the remote copy group.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group |
| `target_name` | str | Name of the target system |
| `target_mode` | str | Replication mode (`sync`, `periodic`, `async`) |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `local_remote_volume_pair_list` | list | List of volume pairs for replication |

**local_remote_volume_pair_list Sub-parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `sourceVolumeName` | str | Name of the source volume |
| `targetVolumeName` | str | Name of the target volume |

---

### dismiss_target

Dismiss (remove) a target system from the remote copy group.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group |
| `target_name` | str | Name of the target system to remove |

---

### start_rcopy

Start the remote copy service on the storage system.

**Required Attributes**

None - this operation starts the remote copy service globally.

---

### remote_copy_status

Check the status of the remote copy group.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_copy_group_name` | str | Name of the remote copy group to check |

---

**Examples**

```yaml
- name: Create remote copy group
  alletramp_remote_copy:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    remote_copy_group_name: "DR_Group_01"
    domain: "production"
    local_user_cpg: "SSD_CPG"
    local_snap_cpg: "FC_CPG"
    remote_copy_targets:
      - target_name: "DR_Site"
        target_mode: "async"
        user_cpg: "DR_SSD_CPG"
        snap_cpg: "DR_FC_CPG"
```

```yaml
- name: Add volume to remote copy group
  alletramp_remote_copy:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: add_volume
    remote_copy_group_name: "DR_Group_01"
    volume_name: "prod_vol_001"
    volume_auto_creation: true
    admit_volume_targets:
      - target_name: "DR_Site"
        sec_volume_name: "prod_vol_001_dr"
```

```yaml
- name: Start remote copy group
  alletramp_remote_copy:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: start
    remote_copy_group_name: "DR_Group_01"
    target_name: "DR_Site"
```

```yaml
- name: Synchronize remote copy group
  alletramp_remote_copy:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: synchronize
    remote_copy_group_name: "DR_Group_01"
    target_name: "DR_Site"
    full_sync: true
```

```yaml
- name: Admit remote copy link
  alletramp_remote_copy:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: admit_link
    target_name: "DR_Site"
    source_port: "0:2:1"
    target_port_wwn_or_ip: "192.168.1.100"
```

```yaml
- name: Check remote copy status
  alletramp_remote_copy:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: remote_copy_status
    remote_copy_group_name: "DR_Group_01"
```

```yaml
- name: Stop remote copy group
  alletramp_remote_copy:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: stop
    remote_copy_group_name: "DR_Group_01"
    target_name: "DR_Site"
```

**Notes**

- Remote copy provides data replication for disaster recovery
- Synchronous mode ensures zero data loss but may impact performance
- Asynchronous modes provide better performance with minimal data loss window
- Links must be established between primary and secondary sites before creating groups
- Volumes can be automatically created on targets or manually pre-created
- Starting snapshots allow resuming replication from specific points
- Full synchronization should be used when data integrity is questioned

---

# alletramp_snapshot

Manage snapshots and snapshot schedules on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a new snapshot of a volume |
| `modify` | Modify snapshot properties (name, expiration, retention) |
| `delete` | Delete an existing snapshot |
| `restore_offline` | Restore a volume from a snapshot (offline) |
| `restore_online` | Restore a volume from a snapshot (online) |
| `create_schedule` | Create a snapshot schedule for automated snapshots |
| `modify_schedule` | Modify an existing snapshot schedule |
| `suspend_schedule` | Suspend a snapshot schedule temporarily |
| `resume_schedule` | Resume a suspended snapshot schedule |
| `delete_schedule` | Delete a snapshot schedule |

---

## Operation Methods

### create

Create a new snapshot of a volume for point-in-time recovery and backup purposes.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `snapshot_name` | str | Name of the snapshot to create |
| `base_volume_name` | str | Source volume to create snapshot from |

**Optional Attributes**

| Parameter | Type | Default | Choices | Description |
|-----------|------|---------|---------|-------------|
| `read_only` | bool | `false` | - | Specifies that the snapshot is read-only |
| `comment` | str | - | - | Additional information for the snapshot |
| `expiration_time` | int | - | - | Relative time from current time when snapshot expires (1-43,800) |
| `expiration_unit` | str | `hours` | `seconds`, `minutes`, `hours`, `days` | Unit for expiration_time |
| `retention_time` | int | - | - | Relative time from current time to retain snapshot (1-43,800) |
| `retention_unit` | str | `hours` | `seconds`, `minutes`, `hours`, `days` | Unit for retention_time |

---

### modify

Modify properties of an existing snapshot such as name, comments, expiration, or retention settings.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `snapshot_name` | str | Name of the snapshot to modify |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `new_name` | str | New name for the snapshot |
| `comment` | str | Updated comment for the snapshot |
| `expiration_time` | int | New expiration time value |
| `expiration_unit` | str | Unit for expiration_time |
| `retention_time` | int | New retention time value |
| `retention_unit` | str | Unit for retention_time |

---

### delete

Delete an existing snapshot from the storage array.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `snapshot_name` | str | Name of the snapshot to delete |

---

### restore_offline

Restore a volume from a snapshot using offline restore (volume is unavailable during restore).

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `snapshot_name` | str | Name of the snapshot to restore from |

**Optional Attributes**

| Parameter | Type | Choices | Description |
|-----------|------|---------|-------------|
| `priority` | str | `PRIORITYTYPE_HIGH`, `PRIORITYTYPE_MED`, `PRIORITYTYPE_LOW` | Priority level for the restore operation |
| `allow_remote_copy_parent` | bool | - | Allow restore even if parent volume is in Remote Copy group |

---

### restore_online

Restore a volume from a snapshot using online restore (volume remains available during restore).

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `snapshot_name` | str | Name of the snapshot to restore from |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `allow_remote_copy_parent` | bool | Allow restore even if parent volume is in Remote Copy group |
| `priority` | str | `PRIORITYTYPE_HIGH`, `PRIORITYTYPE_MED`, `PRIORITYTYPE_LOW` | Priority level for the restore operation |

---

### create_schedule

Create an automated snapshot schedule to periodically create snapshots of a volume.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `schedule_name` | str | Name of the snapshot schedule |
| `base_volume_name` | str | Source volume for scheduled snapshots |

**Optional Attributes - Schedule Timing**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `minute` | str | `*` | Minute to run schedule (0-59 or * for every minute) |
| `hour` | str | `*` | Hour to run schedule (0-23 or * for every hour) |
| `dayofmonth` | str | `*` | Day of month to run (1-31 or * for every day) |
| `dayofweek` | str | `*` | Day of week to run (0-6 or * for every day) |
| `month` | str | `*` | Month to run (1-12 or * for every month) |
| `year` | str | - | Year to run schedule |
| `interval` | str | - | Interval between schedule runs |

**Optional Attributes - Snapshot Settings**

| Parameter | Type | Description |
|-----------|------|-------------|
| `read_only` | bool | Create read-only snapshots |
| `addToSet` | str | Volume set name to add created snapshots to |
| `rcopy` | bool | Enable remote copy for the snapshots |
| `expiration_time` | int | Expiration time for created snapshots |
| `expiration_unit` | str | Unit for expiration time |
| `retention_time` | int | Retention time for created snapshots |
| `retention_unit` | str | Unit for retention time |

**Optional Attributes - Schedule Options**

| Parameter | Type | Description |
|-----------|------|-------------|
| `noalert` | bool | Suppress alerts for the schedule |
| `norebalance` | bool | Do not rebalance this schedule |
| `runonce` | bool | Schedule should run only once |

---

### modify_schedule

Modify an existing snapshot schedule's timing, name, or options.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `schedule_name` | str | Name of the schedule to modify |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `new_schedule_name` | str | New name for the schedule |
| `minute` | str | New minute setting |
| `hour` | str | New hour setting |
| `dayofmonth` | str | New day of month setting |
| `dayofweek` | str | New day of week setting |
| `month` | str | New month setting |
| `year` | str | New year setting |
| `interval` | str | New interval setting |
| `noalert` | bool | Updated alert suppression setting |
| `norebalance` | bool | Updated rebalance setting |

---

### suspend_schedule

Temporarily suspend a snapshot schedule without deleting it.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `schedule_name` | str | Name of the schedule to suspend |

---

### resume_schedule

Resume a suspended snapshot schedule.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `schedule_name` | str | Name of the schedule to resume |

---

### delete_schedule

Delete a snapshot schedule permanently.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `schedule_name` | str | Name of the schedule to delete |

---

**Examples**

```yaml
- name: Create snapshot
  alletramp_snapshot:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    snapshot_name: "web_vol_backup_001"
    base_volume_name: "web_vol_001"
    read_only: true
    comment: "Daily backup snapshot"
```

```yaml
- name: Create snapshot with expiration
  alletramp_snapshot:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    snapshot_name: "temp_snapshot_001"
    base_volume_name: "test_vol_001"
    expiration_time: 48
    expiration_unit: "hours"
    retention_time: 7
    retention_unit: "days"
```

```yaml
- name: Restore volume offline
  alletramp_snapshot:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: restore_offline
    snapshot_name: "web_vol_backup_001"
    priority: "PRIORITYTYPE_HIGH"
```

```yaml
- name: Create daily snapshot schedule
  alletramp_snapshot:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create_schedule
    schedule_name: "daily_backup"
    base_volume_name: "prod_vol_001"
    hour: "2"
    minute: "0"
    read_only: true
    retention_time: 30
    retention_unit: "days"
```

```yaml
- name: Modify snapshot schedule
  alletramp_snapshot:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: modify_schedule
    schedule_name: "daily_backup"
    hour: "3"
    minute: "30"
    new_schedule_name: "nightly_backup"
```

```yaml
- name: Suspend snapshot schedule
  alletramp_snapshot:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: suspend_schedule
    schedule_name: "nightly_backup"
```

```yaml
- name: Delete snapshot
  alletramp_snapshot:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete
    snapshot_name: "web_vol_backup_001"
```

**Notes**

- Snapshots provide point-in-time copies for backup and recovery
- Read-only snapshots prevent accidental modifications
- Snapshot schedules automate regular backup creation
- Online restore allows volume access during restoration
- Offline restore provides faster restoration but volume is unavailable
- Schedule timing uses cron-like syntax for flexible scheduling
- Retention and expiration times help manage storage space automatically

---

# alletramp_user

Manage user accounts on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a new user account with privileges |
| `modify` | Modify user properties such as password or privileges |
| `delete` | Delete an existing user account |
| `get` | Get details of a specific user account |
| `get_all` | Get details of all user accounts |

---

## Operation Methods

### create

Create a new user account with specified password and domain privileges.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Name of the user account to create |
| `password` | str | Password for the local user account |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `domain_privileges` | list | List of domains and associated privileges for the user |

**domain_privileges Sub-parameters**

| Parameter | Type | Choices | Description |
|-----------|------|---------|-------------|
| `name` | str | - | Name of the domain |
| `privilege` | str | `super`, `service`, `security_admin`, `edit`, `create`, `browse`, `basic_edit` | The privilege level assigned in the domain |

---

### modify

Modify properties of an existing user account, including password changes and domain privilege updates.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Name of the user account to modify |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `current_password` | str | Current password when changing password |
| `new_password` | str | New password when changing password |
| `domain_privileges` | list | Updated list of domains and associated privileges |

**Note:** To change password, both `current_password` and `new_password` must be provided.

---

### delete

Delete an existing user account from the storage array.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Name of the user account to delete |

---

### get

Retrieve details of a specific user account including domain privileges.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Name of the user account to retrieve |

---

### get_all

List all user accounts configured on the storage array with their privileges.

**Required Attributes**

None - this operation lists all user accounts.

---

**Examples**

```yaml
- name: Create user with domain privileges
  alletramp_user:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    name: "backup_operator"
    password: "securepassword123"
    domain_privileges:
      - name: "system"
        privilege: "edit"
      - name: "default"
        privilege: "browse"
```

```yaml
- name: Modify user domain privileges
  alletramp_user:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: modify
    name: "backup_operator"
    domain_privileges:
      - name: "system"
        privilege: "create"
      - name: "management"
        privilege: "security_admin"
```

```yaml
- name: Change user password
  alletramp_user:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: modify
    name: "backup_operator"
    current_password: "securepassword123"
    new_password: "newsecurepassword456"
```

```yaml
- name: Get specific user details
  alletramp_user:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: get
    name: "backup_operator"
  register: user_info
```

```yaml
- name: Get all users
  alletramp_user:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: get_all
  register: all_users
```

```yaml
- name: Delete user
  alletramp_user:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete
    name: "backup_operator"
```

**Notes**

- User accounts provide access control to the storage array management
- Domain privileges control what operations users can perform in each domain
- Password requirements follow storage array security policies
- Super privilege provides full administrative access
- Service accounts are typically used for automation and monitoring
- Users with security_admin privilege can manage other user accounts

---

# alletramp_vlun

Manage VLUN (Virtual LUN) exports on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `export_volume_to_host` | Export a volume to a specific host |
| `export_volume_to_hostset` | Export a volume to a host set |
| `export_volumeset_to_host` | Export a volume set to a specific host |
| `export_volumeset_to_hostset` | Export a volume set to a host set |
| `unexport_volume_from_host` | Unexport a volume from a specific host |
| `unexport_volume_from_hostset` | Unexport a volume from a host set |
| `unexport_volumeset_from_host` | Unexport a volume set from a specific host |
| `unexport_volumeset_from_hostset` | Unexport a volume set from a host set |

---

## Operation Methods

### export_volume_to_host

Export a volume to a specific host, making the volume accessible to that host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the volume to export |
| `host_name` | str | Name of the host to export to |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lun` | int | - | Specific LUN number to assign (Logical Unit Number) |
| `autolun` | bool | `false` | Automatically assign an available LUN number |
| `node_val` | int | - | Node value for the export configuration |
| `slot` | int | - | Slot for the export configuration |
| `card_port` | int | - | Card port for the export configuration |

---

### export_volume_to_hostset

Export a volume to a host set, making the volume accessible to all hosts in the set.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the volume to export |
| `host_set_name` | str | Name of the host set to export to |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lun` | int | - | Specific LUN number to assign |
| `autolun` | bool | `false` | Automatically assign an available LUN number |
| `node_val` | int | - | Node value for the export configuration |
| `slot` | int | - | Slot for the export configuration |
| `card_port` | int | - | Card port for the export configuration |

---

### export_volumeset_to_host

Export a volume set to a specific host, making all volumes in the set accessible to that host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_set_name` | str | Name of the volume set to export |
| `host_name` | str | Name of the host to export to |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lun` | int | - | Base LUN number to start assigning from |
| `autolun` | bool | `false` | Automatically assign available LUN numbers |
| `node_val` | int | - | Node value for the export configuration |
| `slot` | int | - | Slot for the export configuration |
| `card_port` | int | - | Card port for the export configuration |

---

### export_volumeset_to_hostset

Export a volume set to a host set, making all volumes accessible to all hosts in the set.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_set_name` | str | Name of the volume set to export |
| `host_set_name` | str | Name of the host set to export to |

**Optional Attributes**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lun` | int | - | Base LUN number to start assigning from |
| `autolun` | bool | `false` | Automatically assign available LUN numbers |
| `node_val` | int | - | Node value for the export configuration |
| `slot` | int | - | Slot for the export configuration |
| `card_port` | int | - | Card port for the export configuration |

---

### unexport_volume_from_host

Remove a volume export from a specific host, making the volume inaccessible to that host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the volume to unexport |
| `host_name` | str | Name of the host to unexport from |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lun` | int | Specific LUN number to unexport |
| `node_val` | int | Node value for the export configuration |
| `slot` | int | Slot for the export configuration |
| `card_port` | int | Card port for the export configuration |

---

### unexport_volume_from_hostset

Remove a volume export from a host set, making the volume inaccessible to all hosts in the set.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the volume to unexport |
| `host_set_name` | str | Name of the host set to unexport from |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lun` | int | Specific LUN number to unexport |
| `node_val` | int | Node value for the export configuration |
| `slot` | int | Slot for the export configuration |
| `card_port` | int | Card port for the export configuration |

---

### unexport_volumeset_from_host

Remove volume set exports from a specific host, making all volumes in the set inaccessible to that host.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_set_name` | str | Name of the volume set to unexport |
| `host_name` | str | Name of the host to unexport from |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lun` | int | Base LUN number to unexport from |
| `node_val` | int | Node value for the export configuration |
| `slot` | int | Slot for the export configuration |
| `card_port` | int | Card port for the export configuration |

---

### unexport_volumeset_from_hostset

Remove volume set exports from a host set, making all volumes inaccessible to all hosts in the set.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_set_name` | str | Name of the volume set to unexport |
| `host_set_name` | str | Name of the host set to unexport from |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lun` | int | Base LUN number to unexport from |
| `node_val` | int | Node value for the export configuration |
| `slot` | int | Slot for the export configuration |
| `card_port` | int | Card port for the export configuration |

---

**Examples**

```yaml
- name: Export volume to host
  alletramp_vlun:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: export_volume_to_host
    volume_name: "web_vol_001"
    host_name: "web_server_01"
    lun: 1
```

```yaml
- name: Export volume to host with automatic LUN assignment
  alletramp_vlun:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: export_volume_to_host
    volume_name: "db_vol_001"
    host_name: "db_server_01"
    autolun: true
```

```yaml
- name: Export volume set to host set
  alletramp_vlun:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: export_volumeset_to_hostset
    volume_set_name: "web_volumes"
    host_set_name: "web_servers"
    autolun: true
```

```yaml
- name: Unexport volume from host
  alletramp_vlun:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: unexport_volume_from_host
    volume_name: "web_vol_001"
    host_name: "web_server_01"
    lun: 1
```

```yaml
- name: Export volume to host set with specific port configuration
  alletramp_vlun:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: export_volume_to_hostset
    volume_name: "shared_vol_001"
    host_set_name: "cluster_nodes"
    lun: 10
    node_val: 0
    slot: 1
    card_port: 1
```

**Notes**

- VLUNs provide the mapping between volumes and hosts/host sets
- Each VLUN creates a LUN (Logical Unit Number) visible to the host
- Use `autolun` to automatically assign available LUN numbers
- Specific LUN assignments must be unique per host
- Volume sets export all contained volumes with sequential LUN assignments
- Unexport operations remove host access to volumes immediately

---

# alletramp_volume

Manage virtual volumes on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a new virtual volume with specified size and CPG |
| `delete` | Delete an existing volume from the storage array |
| `modify` | Modify volume properties such as name, comments, or policies |
| `grow` | Increase the size of an existing volume |
| `tune` | Change volume CPG or convert provisioning type |

---

## Operation Methods

### create

Create a new virtual volume with specified size allocation from a Common Provisioning Group.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the virtual volume to create |
| `cpg` | str | Name of the CPG from which volume user space will be allocated |
| `size` | int | Size of the volume |

**Optional Attributes**

| Parameter | Type | Default | Choices | Description |
|-----------|------|---------|---------|-------------|
| `size_unit` | str | `MiB` | `MiB`, `GiB`, `TiB` | Unit for the volume size |
| `comments` | str | - | - | Additional comments for the volume |
| `count` | int | - | - | Count of volumes to be created with similar configuration |
| `dataReduction` | bool | - | - | Enable or disable data reduction for the volume |
| `expiration_time` | int | - | - | Remaining time before the volume expires |
| `expiration_unit` | str | `hours` | - | Unit for expiration_time |
| `retention_time` | int | - | - | Time to retain the volume |
| `retention_unit` | str | `hours` | - | Unit for retention_time |
| `keyValuePairs` | dict | - | - | Custom metadata key-value pairs (keys must start with v3_, dp_, or dscc_) |
| `ransomWare` | bool | - | - | Enable/disable ransomware policy for volume protection |
| `reduce` | bool | - | - | Enable both deduplication and compression technologies |
| `userAllocWarning` | int | - | - | User allocation warning threshold percentage |

---

### delete

Delete an existing virtual volume from the storage array. The volume must not be exported to any hosts.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the volume to delete |

---

### modify

Modify properties of an existing virtual volume such as name, comments, or retention policies.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the volume to modify |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `new_name` | str | New name for the volume |
| `comments` | str | New comments for the volume |
| `expiration_time` | int | New expiration time value |
| `expiration_unit` | str | Unit for expiration_time |
| `retention_time` | int | New retention time value |
| `retention_unit` | str | Unit for retention_time |
| `keyValuePairs` | dict | Updated custom metadata key-value pairs |
| `ransomWare` | bool | Enable/disable ransomware policy |
| `userAllocWarning` | int | New user allocation warning threshold percentage |
| `wwn` | str | World Wide Name (WWN) of the volume |

---

### grow

Increase the size of an existing virtual volume by a specified amount.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the volume to grow |
| `growth_size_mib` | int | Amount by which to grow the volume in MiB |

---

### tune

Convert volume provisioning type or move volume to a different CPG. This operation allows changing the underlying storage characteristics of a volume.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volume_name` | str | Name of the volume to tune |
| `cpg` | str | Target CPG for the tuned volume |

**Optional Attributes**

| Parameter | Type | Default | Choices | Description |
|-----------|------|---------|---------|-------------|
| `type` | str | `CONVERSIONTYPE_V1` | `CONVERSIONTYPE_THIN`, `CONVERSIONTYPE_V1`, `CONVERSIONTYPE_V2` | Conversion type for the volume |
| `saveToNewName` | str | - | - | Name of the new volume when tuning (keeps original volume) |

---

**Examples**

```yaml
- name: Create volume
  alletramp_volume:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    volume_name: "web_vol_001"
    cpg: "SSD_CPG"
    size: 100
    size_unit: "GiB"
    comments: "Web server volume"
```

```yaml
- name: Create volume with data reduction and ransomware protection
  alletramp_volume:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    volume_name: "secure_vol_001"
    cpg: "SSD_CPG"
    size: 500
    size_unit: "GiB"
    dataReduction: true
    ransomWare: true
    expiration_time: 30
    expiration_unit: "days"
```

```yaml
- name: Grow volume
  alletramp_volume:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: grow
    volume_name: "web_vol_001"
    growth_size_mib: 51200  # Grow by 50 GiB
```

```yaml
- name: Tune volume to thin provisioned
  alletramp_volume:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: tune
    volume_name: "web_vol_001"
    cpg: "THIN_CPG"
    type: "CONVERSIONTYPE_THIN"
```

```yaml
- name: Modify volume properties
  alletramp_volume:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: modify
    volume_name: "web_vol_001"
    new_name: "webapp_vol_001"
    comments: "Updated web application volume"
    userAllocWarning: 80
```

```yaml
- name: Delete volume
  alletramp_volume:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete
    volume_name: "webapp_vol_001"
```

**Notes**

- Volumes must be created in an existing CPG
- Growing a volume increases its capacity but cannot shrink it
- Tune operation can convert between thin and thick provisioning types
- Volume names must be unique within the storage array
- Data reduction and ransomware features may require specific array licensing

---

# alletramp_volumeset

Manage volume sets on HPE Alletra MP storage arrays.

**Supported Operations:**

| Operation | Description |
|-----------|-------------|
| `create` | Create a new volume set with member volumes |
| `delete` | Delete an existing volume set |
| `add_volumes` | Add volumes to an existing volume set |
| `remove_volumes` | Remove volumes from a volume set |

---

## Operation Methods

### create

Create a new volume set with optional initial member volumes. Volume sets allow you to group volumes together for simplified management and export operations.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volumeset_name` | str | Name of the volume set to create |
| `volumeset_type` | str | Type of volume set to create |

**Optional Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `domain` | str | Domain in which to create the volume set |
| `setmembers` | list | Initial list of volume names to add to the set |

---

### delete

Delete an existing volume set from the storage array. The volume set must not have any active VLUNs.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volumeset_name` | str | Name of the volume set to delete |

---

### add_volumes

Add one or more volumes to an existing volume set.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volumeset_name` | str | Name of the volume set |
| `setmembers` | list | List of volume names to add |

---

### remove_volumes

Remove one or more volumes from an existing volume set.

**Required Attributes**

| Parameter | Type | Description |
|-----------|------|-------------|
| `volumeset_name` | str | Name of the volume set |
| `setmembers` | list | List of volume names to remove |

---

**Examples**

```yaml
- name: Create volume set
  alletramp_volumeset:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: create
    volumeset_name: "database_volumes"
    volumeset_type: "REGULAR"
    setmembers:
      - "db_vol_001"
      - "db_vol_002"
```

```yaml
- name: Add volumes to volume set
  alletramp_volumeset:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: add_volumes
    volumeset_name: "database_volumes"
    setmembers:
      - "db_vol_003"
      - "db_vol_004"
```

```yaml
- name: Remove volumes from volume set
  alletramp_volumeset:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: remove_volumes
    volumeset_name: "database_volumes"
    setmembers:
      - "db_vol_001"
```

```yaml
- name: Delete volume set
  alletramp_volumeset:
    storage_system_ip: "10.10.10.100"
    storage_system_username: "admin"
    storage_system_password: "password"
    operation: delete
    volumeset_name: "database_volumes"
```

**Notes**

- Volume sets simplify management by grouping related volumes
- All volumes in a set can be exported together to hosts or host sets
- Deleting a volume set does not delete the individual volumes
- Volume sets must be empty of VLUNs before deletion

---

## Common Parameters

All modules share the following common authentication parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `storage_system_ip` | str | Yes | IP address or hostname of the HPE Alletra MP storage array |
| `storage_system_username` | str | Yes | Username for authentication |
| `storage_system_password` | str | Yes | Password for authentication |
| `operation` | str | Yes | The specific operation to perform (varies by module) |

---

## Return Values

All modules return the following values:

| Key | Type | Description |
|-----|------|-------------|
| `changed` | bool | Indicates whether the module made any changes |
| `msg` | str | Human-readable message describing the result |
| `issue/output` | dict | Additional operation-specific output data (when applicable) |

---

## Notes

- All modules are idempotent - running them multiple times with the same parameters will not cause errors or duplicate resources
- Secure communication via HTTPS is used for all API calls
- Storage system credentials are required for all operations
- Most operations support check mode for dry-run validation

---

## Support

For issues, questions, or contributions, please contact Hewlett Packard Enterprise support or refer to the official documentation.

**Author:** Hewlett Packard Enterprise

**Copyright:** © 2026 Hewlett Packard Enterprise Development LP

---

