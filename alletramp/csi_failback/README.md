# CSI Failback for HPE Alletra Storage MP B10000 Active Peer Persistence

**Tech Preview** — `hpe.csi_failback` Ansible collection

Automates failing back HPE CSI Driver volumes to a recovered primary array
after an Active Peer Persistence (APP) failover, on Kubernetes and OpenShift.

> **Where this lives.** This folder is part of
> [`hpe-storage/hpe_storage_ansible_modules`](https://github.com/hpe-storage/hpe_storage_ansible_modules)
> but is **self-contained**: it is an Ansible *collection* with roles and
> playbooks, not a set of `alletramp_*` modules. It does not use
> `hpe_storage_flowkit_py`, does not need `PYTHONPATH` or `library=` set, and
> talks to the array over WSAPI and to Kubernetes over its API directly. Follow
> the setup in **this** README, not the one at the repository root.

---

## Contents

1. [What it does](#1-what-it-does)
2. [Support status and scope](#2-support-status-and-scope)
3. [Requirements](#3-requirements)
4. [Install](#4-install)
5. [Configure](#5-configure)
6. [Run](#6-run)
7. [Safety model](#7-safety-model)
8. [Recovering from a partial run](#8-recovering-from-a-partial-run)
9. [Audit output](#9-audit-output)
10. [Troubleshooting](#10-troubleshooting)
11. [Variable reference](#11-variable-reference)
12. [Folder layout](#12-folder-layout)

---

## 1. What it does

When the primary array of an APP pair goes down, the HPE CSI Driver fails
workloads over to the surviving array automatically. It does **not** fail them
back. When the original array recovers, three manual steps are required today:

| # | Manual step | Why |
|---|---|---|
| 1 | Recreate VLUNs on the recovered array | It was down while volumes were (re)published on the survivor, so it has the replicated data but no host mappings. |
| 2 | `SWITCHOVER_GROUP` on the Remote Copy Group | Hands ownership back to the original primary. |
| 3 | Restart the affected workloads | Makes the CSI driver re-attach on the restored primary. Only pods published **while the primary was down** need this — pods that were running before the outage already have paths to both arrays and are left alone. |

Plus an implicit fourth: the `HPEReplicationMapping` CRD that tells the driver
which array to publish against must be corrected, or step 3 attaches on the
wrong side.

This collection performs all of them, in order, behind safety gates, with one
command:

```bash
ansible-playbook playbooks/failback.yml -e failback_mode=automatic --ask-vault-pass
```

It runs on an operator workstation or jump host. It makes **HTTPS calls to
WSAPI and to the Kubernetes API server, and nothing else** — no SSH to nodes,
no device, multipath or mount operations. The CSI driver keeps sole ownership
of the data path. **No CSI driver change or redeploy is required.**

---

## 2. Support status and scope

**Status: Tech Preview.** Provided as-is to support early adopters. It is not
yet covered by HPE product support; report issues via this repository.

**Validated**

- HPE Alletra Storage MP B10000, two-site Active Peer Persistence
  (`active_active` policy) with a third-site quorum witness
- HPE CSI Driver v3.0.0+ installed with `disableHostDeletion=true`
- iSCSI hosts; `Deployment` workloads
- One Remote Copy Group per run; single-target (two-array) RCGs

**Not supported in this release**

| Limitation | Detail |
|---|---|
| Multi-target / 3DC RCGs | Refused at runtime. WSAPI `SWITCHOVER_GROUP` cannot select a target. |
| Classic Peer Persistence, async / periodic replication | Out of scope. |
| Automatic host creation | APP requires hosts to be pre-created on both arrays with a protocol prefix (`iqn-`, `nqntcp-`, `wwn-`). Missing hosts are reported and skipped, never invented. |
| FC / NVMe-oF hosts | Host-name resolution is implemented but has not been validated. |
| StatefulSet / DaemonSet | Restart logic exists but has not been validated. |
| Multiple RCGs in one run | Run once per RCG. |
| Scale | Validated with a handful of PVCs. |

---

## 3. Requirements

### Storage and cluster

- Two B10000 arrays in APP with quorum witness; RCG with `active_active`
  policy; hosts admitted with `admitrcopyhost -proximity all`.
- HPE CSI Driver ≥ 3.0.0, Helm value `disableHostDeletion=true`.
- A replication StorageClass whose parameters include `remoteCopyGroup`. The
  collection discovers volumes by that attribute:

  ```bash
  kubectl get pv -o custom-columns=NAME:.metadata.name,RCG:.spec.csi.volumeAttributes.remoteCopyGroup
  ```

  If the RCG column is empty, discovery finds nothing.

### Control node

| | Requirement |
|---|---|
| Python | 3.9+ |
| ansible-core | **2.15 – 2.17** (the root repo's 2.17.4 is fine) |
| Network | TCP 443 to both arrays' management IPs; reachability to the Kubernetes API server |
| kubeconfig | Permissions below |

Minimum Kubernetes RBAC for the kubeconfig identity:

```yaml
- apiGroups: [""]
  resources: [persistentvolumes, pods]
  verbs: [get, list]
- apiGroups: [""]
  resources: [events]
  verbs: [create]
- apiGroups: [storage.k8s.io]
  resources: [volumeattachments]
  verbs: [get, list]
- apiGroups: [apps]
  resources: [deployments, statefulsets]
  verbs: [get, list, patch]
- apiGroups: [storage.hpe.com]
  resources: [hpereplicationmappings]
  verbs: [get, list, patch]
```

Array credentials need Remote Copy and VLUN management rights (`3paradm` or an
equivalent `super`/`edit` role).

---

## 4. Install

```bash
cd hpe_storage_ansible_modules/alletramp/csi_failback

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml -p ./collections

ansible --version                              # must report core 2.15–2.17
ansible-playbook playbooks/failback.yml --list-tasks   # parses everything, contacts nothing
```

`ansible.cfg` in this folder already points `collections_path` at
`./collections`, so run all commands from this directory (or export
`ANSIBLE_CONFIG=$PWD/ansible.cfg`).

> **Keep the venv active.** The most common setup failure is running the
> system `ansible-core` (often 2.12), which `kubernetes.core` rejects.

---

## 5. Configure

### 5.1 Identify the two arrays — read this first

Role names swap during a failover and this confuses everyone once:

| Term | Means |
|---|---|
| **original primary** | The array that **went down**. It is currently the *secondary*. You are failing back **to** it. |
| **current primary** | The array that **took over**. It is the original secondary. |

Get the Remote Copy **target names** from either array:

```
showrcopy
```

Use the target name (e.g. `s042N-FC`), not the DNS name or serial.

### 5.2 Inventory variables

```bash
cp inventory/group_vars/all.yml.example inventory/group_vars/all.yml
$EDITOR inventory/group_vars/all.yml
```

```yaml
failback_rcg_name: "my-csi-rcg"           # PLAIN name — not the ".r<serial>" form

failback_original_primary:
  name: "array-site-a"                    # showrcopy target name of the array that went down
  wsapi_url: "https://10.10.0.10:443"
  username: "{{ vault_array_a_username }}"
  password: "{{ vault_array_a_password }}"
  validate_certs: false

failback_current_primary:
  name: "array-site-b"
  wsapi_url: "https://10.20.0.10:443"
  username: "{{ vault_array_b_username }}"
  password: "{{ vault_array_b_password }}"
  validate_certs: false

failback_mode: approval                   # start here
failback_namespaces: ["prod-db"]          # limit blast radius; [] = all namespaces
failback_kubeconfig: "~/.kube/config"
```

### 5.3 Credentials in a vault

```bash
cp inventory/group_vars/vault.yml.example inventory/group_vars/vault.yml
$EDITOR inventory/group_vars/vault.yml
ansible-vault encrypt inventory/group_vars/vault.yml
```

Both files are excluded by `.gitignore`. Never commit an unencrypted vault.

---

## 6. Run

Work through these **in order**. Each step is safe to repeat.

### 6.1 Preflight — read-only, always safe

```bash
ansible-playbook playbooks/preflight.yml --ask-vault-pass
```

Answers *"could we fail back right now?"* and writes **nothing** to either
array (`changed=0`). Run it during the outage, repeatedly, until it reports:

```
PREFLIGHT VERDICT: READY TO FAIL BACK
```

On a healthy pair where no failover happened it stops at Gate 0 with
`NOTHING TO FAIL BACK` — that is the correct answer, not an error.

### 6.2 Dry run

```bash
ansible-playbook playbooks/failback.yml --check --ask-vault-pass
```

Every task prints what it *would* do.

### 6.3 Approval mode (default) — stops before the switchover

```bash
ansible-playbook playbooks/failback.yml --ask-vault-pass
```

Rehydrates missing VLUNs on the recovered array (idempotent, non-disruptive),
runs every gate, then **stops** and prints the exact `SWITCHOVER_GROUP` call
it would make.

### 6.4 Automatic — full failback

```bash
ansible-playbook playbooks/failback.yml -e failback_mode=automatic --ask-vault-pass
```

```
ZERO-TOUCH FAILBACK COMPLETED SUCCESSFULLY
RCG                    : my-csi-rcg
Primary is now         : array-site-a
VLUNs created          : 1
Workloads restarted    : 3
Volumes attached       : 3
Replication            : HEALTHY
```

### 6.5 Verify

```bash
kubectl get pods -n prod-db -o wide                       # Running, re-attached
kubectl get events -n hpe-storage --field-selector reason=FailbackCompleted
```

On the original primary: `showrcopy` shows the RCG as `Primary`, and
`showvlun -v <volume>` shows an active VLUN for every volume.

### 6.6 Multiple RCGs

Run once per group, changing `failback_rcg_name`:

```bash
ansible-playbook playbooks/failback.yml -e failback_mode=automatic -e failback_rcg_name=rcg-2 --ask-vault-pass
```

---

## 7. Safety model

The collection refuses far more often than it acts. Understand these before
relaxing anything.

| Gate | Checks | Why it exists |
|---|---|---|
| **0** | Original primary reports the RCG as **SECONDARY** | Otherwise no failover happened (or failback already completed). Prevents switching over a healthy pair. Most common trigger: the two arrays are **swapped in `all.yml`**. |
| **1** | RCG is Started | A stopped group cannot switch over. |
| **2** | Every volume `Synced` (polled) | **The data-loss gate.** Switching over a lagging group promotes stale blocks. |
| **3** | Quorum witness `STANDBY`/`ACTIVE` | No arbiter → split-brain risk. Disable only with `failback_require_quorum_witness: false` after confirming witness health yourself. |
| Target | RCG has exactly one target | 3DC groups are refused. |

Additional guarantees:

- **No `--force`.** Switching over an unsynced group is a human decision made
  with the array CLI.
- **`--check` and `failback_mode=off` each independently forbid every array
  write.** Preflight relies on this.
- **Ordering is enforced.** `switchover` refuses to run unless the gates
  passed in the same run; `republish_workloads` refuses unless the
  `HPEReplicationMapping` was reconciled. `--tags` cannot bypass them.
- **LUNs are never guessed.** VLUNs use `autoLun`; the assigned LUN is read
  back from active rows. A guessed LUN surfaces on the node as
  `device not found with serial …`.
- **Abort rather than guess.** If the array accepts the switchover but the role
  does not move, the run stops *before* touching workloads.
- **Idempotent.** Re-running any phase against an already-completed state
  creates nothing (`GET`-before-act; HTTP 409 is success).
- **Minimal restarts.** Only workloads whose pods were published while the
  original primary was down are restarted (`failback_republish_scope: outage`).
  Membership is decided from the array: a (volume, node) pair attached in
  Kubernetes but with no VLUN on the original primary can only have been
  attached during the outage. Pods running before the outage already hold
  paths to both arrays and are left untouched. Set
  `failback_republish_scope: all` to restore the restart-everything behaviour,
  or `failback_outage_start_time` to additionally restart any pod created
  after a known instant.

---

## 8. Recovering from a partial run

### The switchover did NOT happen (run aborted at or before Gate 2/3)

Fix the cause (usually wait for resync) and **re-run `failback.yml`**. Nothing
was mutated except idempotent VLUN creation.

### The switchover DID happen but the run aborted afterwards

On the original primary `showrcopy` shows `Primary`, but pods have not been
restarted or the mapping is stale. **Do not re-run `failback.yml`** — Gate 0
will correctly refuse. Use the resume playbook, which verifies the array is
already primary and then runs only the Kubernetes-side steps:

```bash
ansible-playbook playbooks/failback_resume.yml --check --ask-vault-pass
ansible-playbook playbooks/failback_resume.yml -e failback_mode=automatic --ask-vault-pass
```

It also re-runs VLUN rehydration, because a PVC provisioned **while the
primary was down** is replicated to it but has no VLUN there until this step
creates one.

---

## 9. Audit output

Each run writes `reports/failback-<rcg>-<epoch>.json`:

```json
{
  "rcg": "my-csi-rcg",
  "mode": "automatic",
  "original_primary": "array-site-a",
  "current_primary_before": "array-site-b",
  "volumes_discovered": "3",
  "vluns_created": "1",
  "replication_mappings_swapped": "1",
  "workloads_restarted": "3",
  "final_role": "PRIMARY",
  "final_attached_volumes": "3",
  "unsynced_volumes": [],
  "result": "SUCCESS"
}
```

Full output is kept in `reports/ansible.log`. A `FailbackCompleted` Event is
emitted in `hpe-storage`. Credentials are never logged at any verbosity.

---

## 10. Troubleshooting

| Symptom | Cause / action |
|---|---|
| `NOTHING TO FAIL BACK … still reports the RCG as PRIMARY` | No failover occurred, **or** `failback_original_primary` / `failback_current_primary` are swapped. The array that went *down* is the original primary. |
| `No attached volumes found for RCG` | Wrong `failback_rcg_name`, StorageClass lacks `remoteCopyGroup`, or no workloads running. Check the `kubectl get pv` command in §3. |
| `WARNING: N node(s) have no Host object on the original primary` | Create and admit them: `createhost -iscsi iqn-<node> <initiator-iqn>` then `admitrcopyhost -proximity all <rcg> iqn-<node>`. Re-run. |
| `GATE 2 FAILED … NOT synchronized` | Resync in progress. `showrcopy -d <rcg>`; re-run when Synced. Do not disable the gate. |
| `GATE 3 FAILED` with a healthy witness | Reported `quorumStatus` must be `3` (STANDBY) or `4` (ACTIVE). |
| `remote copy group does not exist` (code 187) on one array | You set the `.r<serial>` name. Use the plain name; the collection resolves the per-array variant. |
| `SWITCHOVER did not take effect` | Array accepted the request but the role did not move. **Do not restart workloads.** Inspect both arrays with `showrcopy -d`. |
| Login `status -1 … handshake operation timed out` | `https_proxy` is set and cannot reach the storage LAN. The collection bypasses proxies by default (`failback_wsapi_use_proxy: false`); confirm with `curl -sk --noproxy '*' https://<array>/api/v1/credentials`. |
| `Collection kubernetes.core does not support Ansible version 2.12` | System Ansible in use. `source .venv/bin/activate`. |
| `Batch did not return to Ready` | Run stops rather than disrupting more workloads. `kubectl describe pod` and `kubectl logs -n hpe-storage -l app=hpe-csi-node -c hpe-csi-driver`. |
| `404 volume does not exist` creating a VLUN | Should not occur — array volume names are truncated (`pvc-…-e1fde5320ea6` → `pvc-…-e1f`) and the collection resolves them from the array's inventory. If you see it, please report with `showvv` output. |

More detail: `ansible-playbook … -vvv`.

---

## 11. Variable reference

Set in `inventory/group_vars/all.yml` or with `-e`.

### Required

| Variable | Description |
|---|---|
| `failback_rcg_name` | Plain RCG name |
| `failback_original_primary` | `{name, wsapi_url, username, password, validate_certs}` — array that went down |
| `failback_current_primary` | Same — array that took over |

### Policy

| Variable | Default | Description |
|---|---|---|
| `failback_mode` | `approval` | `approval` \| `automatic` \| `off` |
| `failback_min_stable_window_seconds` | `600` | Recovered array must be healthy this long before trusting it |
| `failback_detect_timeout_seconds` | `1800` | Give up waiting for recovery |
| `failback_require_quorum_witness` | `true` | Gate 3 |
| `failback_task_timeout_seconds` | `900` | Bound on array task / resync polling |
| `failback_reconcile_replication_mapping` | `true` | Keep on unless your CSP is confirmed to swap the CRD eagerly |
| `failback_wsapi_use_proxy` | `false` | Keep `false`; arrays are on the management LAN |

### Workloads

| Variable | Default | Description |
|---|---|---|
| `failback_republish_enabled` | `true` | Restart workloads after switchover |
| `failback_republish_scope` | `outage` | `outage` = restart only pods published while the primary was down (no VLUN on it); `all` = restart every workload in the RCG |
| `failback_outage_start_time` | `""` | Optional ISO-8601 UTC time (`2026-10-05T04:46:11Z`); pods created at/after it are also restarted |
| `failback_republish_batch_size` | `1` | Workloads per batch |
| `failback_republish_batch_pause_seconds` | `30` | Pause between batches |
| `failback_republish_wait_timeout_seconds` | `120` | Wait for a batch to be Ready |
| `failback_namespaces` | `[]` | Limit scope; empty = all |

### Kubernetes / reporting

| Variable | Default | Description |
|---|---|---|
| `failback_kubeconfig` | `$KUBECONFIG` | kubeconfig path |
| `failback_kube_context` | `""` | context |
| `failback_csi_driver_name` | `csi.hpe.com` | PV / VolumeAttachment filter |
| `failback_report_dir` | `./reports` | Audit output |
| `failback_emit_k8s_events` | `true` | Emit `FailbackCompleted` Event |
| `failback_event_namespace` | `hpe-storage` | Event namespace |

### Tags

`detect`, `rehydrate`, `gate`, `switchover`, `mapping`, `republish`, `report`.
Gate and ordering assertions still apply when tags are used.

---

## 12. Folder layout

```
alletramp/csi_failback/
├── README.md                     ← this file
├── VERSION
├── ansible.cfg                   collections_path=./collections, log → reports/
├── requirements.txt              ansible-core, kubernetes, PyYAML, jsonpatch
├── requirements.yml              kubernetes.core (installed from Galaxy)
├── inventory/
│   ├── hosts.yml                 localhost only
│   └── group_vars/
│       ├── all.yml.example       copy → all.yml
│       └── vault.yml.example     copy → vault.yml, then ansible-vault encrypt
├── playbooks/
│   ├── preflight.yml             read-only readiness
│   ├── failback.yml              full pipeline
│   └── failback_resume.yml       post-switchover recovery
└── collections/ansible_collections/hpe/csi_failback/
    ├── galaxy.yml
    ├── LICENSE
    └── roles/
        ├── common/                        defaults, WSAPI constants, shared tasks
        ├── detect_recovery/               Gate 0 + stability window
        ├── rehydrate_hosts_vluns/         VLUN recreation on the recovered array
        ├── verify_rcg_sync/               Gates 1–3
        ├── reconcile_replication_mapping/ HPEReplicationMapping pre/post swap
        ├── switchover/                    SWITCHOVER_GROUP + verification
        ├── republish_workloads/           batched rollout restart
        └── verify_and_report/             end-state checks + audit JSON
```

---

## Contributing / issues

Open an issue in this repository with the `csi_failback` label. Attach the
`reports/failback-*.json`, the relevant portion of `reports/ansible.log`, and
`showrcopy -d <rcg>` from both arrays. Credentials are redacted from the log
automatically.
