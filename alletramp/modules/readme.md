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
| `bulkvv` | bool | - | Make target volume VMware specific |
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
| `targetName` | str | Name of the target (volume, volume set, domain) |
| `targetType` | str | Type: `QOS_TGT_VV`, `QOS_TGT_VVSET`, `QOS_TGT_DOMAIN`, or `QOS_TGT_SYSTEM` |

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

## Operation Methods (See full documentation for details)

For complete operation methods documentation including all parameters and examples, please refer to the online documentation or individual module files.

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
| `output` | dict | Additional operation-specific output data (when applicable) |

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

**Copyright:** © 2025 Hewlett Packard Enterprise Development LP

---

