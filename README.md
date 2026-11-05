# HPE Storage Ansible Module

Welcome to the documentation for HPE Storage Ansible Module.

This comprehensive guide covers:

- **HPE Ansible Module** for Alletra MP storage automation
- **Installation & Setup** instructions
- **System Requirements** and platform compatibility
- **Getting Started** guides and quick examples
- **Module Reference** documentation with detailed operation methods

These modules enable automation of HPE Alletra MP storage arrays with Ansible.

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation & Setup](#installation--setup)
4. [Running Unit Tests](#running-unit-tests)
5. [Getting Started](#getting-started)
6. [Supported Modules](#supported-modules)
7. [Failover and Failback (OpenStack Cinder)](#failover-and-failback-openstack-cinder)
8. [Module Reference](#module-reference)

---

# Overview

The HPE Storage Ansible Module enable automation of storage provisioning for the HPE Alletra MP array. The modules use the HPE Storage Flowkit for Python to communicate with the storage array over the WSAPI REST interface.

**Supported Storage Platform:**

- **HPE Alletra MP** (OS version 10.5.x)

**What You Can Automate:**

The collection provides modules to automate complete storage lifecycle management including:

- Volume and volume set operations
- Host and host set operations
- Storage provisioning operations (CPG)
- VLUN management 
- Data protection with snapshots
- Manages Online and Offline Clones
- Replication Copy Group operations
- Performance optimization with QoS policies
- System Management - DNS, NTP and user accounts.
- SSL/TLS certificate management
- Alert monitoring and test alert generation

**Key Benefits:**

- **Declarative** - Define desired state, Ansible handles the implementation
- **Idempotent** - Safe to run repeatedly without side effects
- **Error Handling** - Clear error messages with parameter validation

## Non Idempotent Actions

Actions are Idempotent when they can be run multiple times on the same system and the results will always be identical, without producing unintended side effects.

The following actions are non-idempotent:

- **Clone**: resync, create_offline
- **Snapshot**: restore online, restore offline
- **Virtual Volume**: grow
- **VLUN**: All actions become non-idempotent when autolun is set to true
- **Alert**: test_alert

---

# System Requirements

**Platform Compatibility:**

| Component | Version | Status |
|-----------|---------|--------|
| **HPE Alletra MP** | OS 10.5.x with WSAPI service enabled | ✅ Required |
| **Ansible** | 2.17.4 | ✅ Supported |
| **Python** | 3.10 + | ✅ Required |

**Prerequisites:**

- **pip**: Python package installer must be available (`pip --version` to verify)
- **Network Connectivity**: Connectivity to HPE Alletra MP array
- **WSAPI Service**: Enabled on the target HPE Alletra MP array

**Python Package Dependencies:**

| Package | Version |
|---------|---------|
| **hpe_storage_flowkit_py** | 0.8 |

**Installation:**

```bash
pip install hpe-storage-flowkit-py
```
---

# Installation & Setup

This guide walks you through installing and configuring the HPE Storage Ansible Module for Alletra MP.

**Prerequisites:**

Refer to [System Requirements](#system-requirements) for detailed platform compatibility and dependency information.

---

## 1. Install Python Dependencies

Install Ansible and the required HPE Storage Flowkit python package:

```bash
pip install ansible
pip install hpe-storage-flowkit-py
```
---

## 2. Verify Installation

Test that the packages were installed correctly:

```bash
python3 -c "import hpe_storage_flowkit_py; print('✓ HPE Storage Flowkit installed successfully')"
```

**Expected Outcomes:**

- **Success:** Message displays without errors
- **Error:** Missing dependencies - reinstall packages and retry

**Troubleshooting:**

If import fails, check:
```bash
# Verify pip installation
pip list | grep hpe_storage

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Reinstall if needed
pip uninstall hpe-storage-flowkit-py
pip install hpe-storage-flowkit-py
```

---

## 3. Clone the Ansible Module Repository

Clone the latest HPE Alletra MP Ansible module repository from [GitHub](https://github.com/hpe-storage/hpe_storage_ansible_modules):

```bash
git clone https://github.com/hpe-storage/hpe_storage_ansible_modules.git
cd hpe_storage_ansible_modules
```

**Repository Contents:**

- `alletramp/` - Main module directory for AlletraMP
  - `ansible_service.py` - Ansible client that interfaces with hpe_storage_flowkit_py
  - `modules/` - Ansible modules for HPE Alletra MP
  - `playbooks/` - Example playbooks and templates
  - `ansible.cfg` - Sample Ansible configuration

---

## 4. Configure Environment

Set up the required environment variables:

```bash
export PYTHONPATH="/path/to/your/hpe_storage_ansible_modules/alletramp:$PYTHONPATH"
export ANSIBLE_CONFIG="/path/to/your/hpe_storage_ansible_modules/alletramp/ansible.cfg"
export PATH="$HOME/.local/bin:$PATH"
```

**Note:** Replace `/path/to/your/` with your actual installation path.

## 5. Configure ansible.cfg

Edit the `ansible.cfg` file in your project root directory to specify the module library path:

```ini
library = /path/to/your/hpe_storage_ansible_modules/alletramp/modules
```

**Example with Absolute Path:**

```ini
[defaults]
library = /home/user/workspace/hpe_storage_ansible_modules/modules
```

---

## 6. Validate Configuration

Create a simple test playbook to verify your setup.

---

**Quick Setup Checklist:**

- ☐ Python dependencies installed
- ☐ Python package import test passed
- ☐ Environment variables configured
- ☐ ansible.cfg updated with correct library path
- ☐ Test playbook executed successfully

---

# Running Unit Tests

This section explains how to run the unit tests for the HPE Storage Ansible Module.

## Prerequisites

Install the required testing dependencies:

```bash
pip install pytest mock
```

## Running Tests

Run tests from the `hpe_storage_ansible_modules/alletramp` directory:

### Run All Tests

```bash
python3 -m pytest -vv -s
```

### Run a Specific Test File

```bash
python3 -m pytest test/test_alletramp_volume.py -vv -s
```

### Run a Specific Test

```bash
python3 -m pytest test/test_alletramp_volume.py::TestAlletrampVolume::test_create_volume_success -vv -s
```


**Setting up your working directory:**

```bash
cd /path/to/hpe_storage_ansible_modules/alletramp
python3 -m pytest
```

**Note:** Python Path should be set to `hpe_storage_ansible_modules/alletramp` for running test files.

---

# Getting Started

This guide provides quick examples to help you start using the HPE Storage Ansible Module for Alletra MP.

**Prerequisites:**

Before you begin, ensure you have:

- ✅ Ansible installed (2.17.4)
- ✅ Python 3.10 or later
- ✅ HPE Storage Ansible Module is cloned
- ✅ Python dependencies installed (`hpe_storage_flowkit_py`)
- ✅ Connectivity to your Alletra MP array
- ✅ Valid credentials with appropriate privileges

See [Installation & Setup](#installation--setup) for detailed instructions.

**Basic Playbook Structure:**

All playbooks follow this basic structure:

```yaml
---
- name: Manage HPE Alletra MP Storage
  hosts: localhost
  
  vars:
    storage_ip: "10.10.10.100"
    storage_user: "admin"
    storage_pass: "password"
  
  tasks:
    # Your tasks here
```

**Example: Create a Volume**

```yaml
---
- hosts: localhost
  tasks:
    - name: Create volume
      alletramp_volume:
        storage_system_ip: "10.10.10.100"
        storage_system_username: "admin"
        storage_system_password: "password"
        operation: create
        volume_name: "prod_vol_001"
        cpg: "SSD_CPG"
        size: 100
```

**Running Playbooks:**

Execute your playbook:

```bash
ansible-playbook -i <playbook.yml> -vvv
```

---

# Supported Modules

This section provides an overview of all modules available in the HPE Storage Ansible Module for Alletra MP.

| **Module** | **Description** |
|-----------|-----------------|
| [`alletramp_alert`](alletramp/modules/readme.md#alletramp_alert) | Queries alerts and generates test alerts |
| [`alletramp_certs`](alletramp/modules/readme.md#alletramp_certs) | Manages SSL/TLS certificates for array services |
| [`alletramp_cpg`](alletramp/modules/readme.md#alletramp_cpg) | Manages Common Provisioning Group (storage pool) operations |
| [`alletramp_dns`](alletramp/modules/readme.md#alletramp_dns) | Manages DNS configuration and network settings |
| [`alletramp_host`](alletramp/modules/readme.md#alletramp_host) | Manages host operations with FC/iSCSI initiators and CHAP authentication |
| [`alletramp_hostset`](alletramp/modules/readme.md#alletramp_hostset) | Manages host set operations for grouping multiple hosts |
| [`alletramp_ntp`](alletramp/modules/readme.md#alletramp_ntp) | Manages NTP configuration for time servers and timezone |
| [`alletramp_offline_clone`](alletramp/modules/readme.md#alletramp_offline_clone) | Manages offline clone operations |
| [`alletramp_online_clone`](alletramp/modules/readme.md#alletramp_online_clone) | Manages online clone operations |
| [`alletramp_qos`](alletramp/modules/readme.md#alletramp_qos) | Manages QoS operations for performance limits and priorities |
| [`alletramp_remote_copy`](alletramp/modules/readme.md#alletramp_remote_copy) | Manages remote copy operations for replication groups |
| [`alletramp_snapshot`](alletramp/modules/readme.md#alletramp_snapshot) | Manages snapshot operations |
| [`alletramp_user`](alletramp/modules/readme.md#alletramp_user) | Manages user account operations |
| [`alletramp_vlun`](alletramp/modules/readme.md#alletramp_vlun) | Manages VLUN operations for exporting |
| [`alletramp_volume`](alletramp/modules/readme.md#alletramp_volume) | Manages volume operations |
| [`alletramp_volumeset`](alletramp/modules/readme.md#alletramp_volumeset) | Manages volume set operations |

---

# Failover and Failback (OpenStack Cinder)

The `alletramp/playbooks/openstack_cinder/` directory contains playbooks that automate Cinder backend failover and failback for replicated HPE Alletra MP backends. They run standalone, without an OpenStack-Ansible checkout, and use the installed `cinder` or `openstack` CLI.

The playbooks do not talk to the storage arrays. They validate the request, issue `cinder failover-host`, and poll the Cinder service record until the backend reaches the expected `replication_status`. The HPE Alletra MP Cinder driver performs the array-side work.

> **Note:** These playbooks depend on the HPE Alletra MP Cinder driver patch [1006944](https://review.opendev.org/c/openstack/cinder/+/1006944).

## Failover and Failback at a Glance

| Item | Failover | Failback |
|------|----------|----------|
| Purpose | Move backend to the secondary (DR) array | Return backend to the primary array |
| Playbook | `cinder-failover.yml` | `cinder-failback.yml` |
| `backend_id` | Target `replication_device` backend | `default` (always) |
| Primary array | Available or unavailable | Available and reachable |
| Expected `replication_status` | `failed-over` | `enabled` |

## Workflow

1. **Preflight and capability check** - validates the action and target, and checks that the deployed driver sets `AUTO_FAILBACK_SUPPORTED`. If not, the run ends as a no-op.
2. **Service and policy validation** - confirms the target cinder-volume service is `up`, not `failing-over`, and that the `backend_id` is a configured `replication_device`.
3. **Idempotency check** - ends as a no-op if the backend is already in the requested state.
4. **Execution and settle polling** - sends the request and polls `replication_status` until it completes, fails, or the settle window ends.
5. **Verification** - reports the final state of the target backend.

## Prerequisites

- Replication is configured on the backend (`replication_device` is set).
- Every Peer Persistence remote copy group is started and fully synchronized.
- For failback, the original primary array is reachable and the DR remote copy groups are in sync.
- An OpenStack RC file with credentials allowed to list Cinder services and invoke backend failover.
- The playbook runs on the cinder-volume host, so the driver capability check can import the driver and `cinder.conf` can be read.

No HPE array credentials are required by Ansible.

## Running

Run both commands from `alletramp/playbooks/openstack_cinder/`.

**Failover:**

```bash
ansible-playbook -i inventories/local-inventory cinder-failover.yml \
  -e cinder_replication_openrc=/opt/stack/devstack/openrc \
  -e cinder_replication_target='<host>@<backend>' \
  -e cinder_replication_backend_id='<replication_device_backend_id>'
```

**Failback:**

```bash
ansible-playbook -i inventories/local-inventory cinder-failback.yml \
  -e cinder_replication_openrc=/opt/stack/devstack/openrc \
  -e cinder_replication_target='<host>@<backend>'
```

**Key variables:**

| Variable | Description |
|----------|-------------|
| `cinder_replication_target` | Required. The cinder-volume host as `<host>@<backend>`, as shown by `cinder service-list`. |
| `cinder_replication_backend_id` | Failover only. The `backend_id` of the `replication_device` to fail over to. |
| `cinder_replication_openrc` | OpenStack RC file to source. Default `$HOME/openrc`. |
| `cinder_replication_openrc_args` | Arguments for the RC file. DevStack needs `admin admin`. |
| `cinder_replication_settle_retries` / `cinder_replication_settle_delay` | Status polls (default 24) and seconds between polls (default 5). |
| `auto_failback_supported` | Set `true` to skip the driver capability check. |

## Verifying the Result

The backend status only shows that the workflow completed. If individual volumes fail, the backend can still end `failed-over` or `enabled` while those volumes show `replication_status` `error`. After every run, check:

```bash
cinder service-list --withreplication
cinder list --all-projects --field ID,Name,Status,os-vol-host-attr:host,replication_status
```

## Limitations

- Supported only for Active-Active Peer Persistence (AAPP) synchronous replication.
- A request the driver rejects (for example a remote copy group that is not started while the primary is up, or a primary that is still down on failback) leaves the backend unchanged. The failure is reported only after the full settle window.
- If `cinder-volume` is restarted while the primary array is unreachable, the driver does not initialize and failover ends in `failover-error`. Restore the primary and restart `cinder-volume` before retrying.
- A successful backend failover does not guarantee application-level availability.

For the full variable list, driver scenarios, status rules, and troubleshooting, see the [OpenStack Cinder failover/failback README](alletramp/playbooks/openstack_cinder/README.md) and the [automated failover/failback guide](alletramp/playbooks/openstack_cinder/docs/automated-failover-failback.md).
