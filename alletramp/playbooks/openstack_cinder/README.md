# Automated Failover / Failback Replication Recovery

This directory runs Cinder backend failover and failback independently of an OpenStack-Ansible checkout. It uses
the installed `cinder` or `openstack` CLI; it does not require an
OpenStack-Ansible collection. The only Python it runs is the driver capability
check, which imports the HPE driver constants (see
[Driver capability gate](#driver-capability-gate)).

The playbook does not talk to the storage arrays. It validates that the request
is safe, issues `cinder failover-host`, and then watches the Cinder service
record until the backend reaches the expected replication status. The HPE
Alletra MP driver does the array work; see
[Driver behavior: failover and failback](#driver-behavior-failover-and-failback)
for the driver's scenarios, status rules and operator notes.

## Contents

- [Files](#files)
- [Requirements](#requirements)
- [Standalone execution](#standalone-execution)
- [Variables](#variables)
- [How the workflow runs](#how-the-workflow-runs)
- [Result and status reference](#result-and-status-reference)
- [Driver behavior: failover and failback](#driver-behavior-failover-and-failback)
- [Driver capability gate](#driver-capability-gate)
- [Console output](#console-output)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [OpenStack-Ansible integration](#openstack-ansible-integration)

## Files

All paths are relative to `alletramp/playbooks/openstack_cinder/`.

- `cinder-failover.yml`: standalone failover entry point.
- `cinder-failback.yml`: standalone failback entry point.
- `cinder-replication.yml`: shared validation and execution workflow.
- `inventories/local-inventory`: localhost inventory for direct execution.
- `ansible.cfg`: enables the `minimal_progress` console callback.
- `callback_plugins/minimal_progress.py`: phase-grouped console output.

## Requirements

- Ansible on the execution host.
- The `cinder` CLI, or the `openstack` CLI used by the service-discovery
  fallback, installed on the execution host.
- An OpenStack RC file with credentials allowed to list Cinder services and
  invoke backend failover.
- Network access from the execution host to the OpenStack APIs.
- For the driver capability check, an execution host where the HPE Alletra MP
  Cinder driver is importable (normally the cinder-volume host). Not needed if
  you pass `-e auto_failback_supported=true`.

No HPE array credentials are required by Ansible. Cinder and the configured HPE
driver perform the storage operation.

## Standalone execution

Run failover from this directory:

```bash
ansible-playbook -i inventories/local-inventory \
  cinder-failover.yml \
  -e cinder_replication_openrc=/opt/stack/devstack/openrc \
  -e cinder_replication_openrc_args='admin admin' \
  -e cinder_replication_target='ubuntu@san-repiscsi-4' \
  -e cinder_replication_backend_id='s0452-FC'
```

Run failback against the same Cinder backend host:

```bash
ansible-playbook -i inventories/local-inventory \
  cinder-failback.yml \
  -e cinder_replication_openrc=/opt/stack/devstack/openrc \
  -e cinder_replication_openrc_args='admin admin' \
  -e cinder_replication_target='ubuntu@san-repiscsi-4'
```

Failback always sends `--backend_id default`; callers should omit
`cinder_replication_backend_id` or set it to `default`.

The shared entry point can also be called directly by setting the action:

```bash
ansible-playbook -i inventories/local-inventory \
  cinder-replication.yml \
  -e cinder_replication_action=failover \
  -e cinder_replication_target='ubuntu@san-repiscsi-4' \
  -e cinder_replication_backend_id='s0452-FC'
```

## Driver capability gate

Before any Cinder API call, the shared workflow imports
`cinder.volume.drivers.hpe.alletramp_constants` on the execution host and reads
`AUTO_FAILBACK_SUPPORTED`:

| Driver `AUTO_FAILBACK_SUPPORTED` | Override passed | Result |
|---|---|---|
| `True` | No | Failover/failback proceeds. |
| Missing or not `True` | No | **No-op**: the play ends and nothing is sent to Cinder. |
| Any | Yes (`-e auto_failback_supported=true`) | Warning, the check is skipped and the workflow proceeds. |

If the constants module cannot be imported at all, the play fails with a
diagnostic rather than silently skipping. Use the override only when you have
verified the deployed driver is up to date or the flag has not yet been
approved upstream. It bypasses only this gate; readiness, backend-policy and
idempotency checks still apply.

```bash
ansible-playbook -i inventories/local-inventory \
  cinder-failover.yml \
  -e auto_failback_supported=true \
  -e cinder_replication_target='ubuntu@san-repiscsi-4' \
  -e cinder_replication_backend_id='s0452-FC'
```

The check assumes the execution host is the cinder-volume host. If the driver
lives in a virtualenv, set `cinder_replication_python` to that interpreter; use
`cinder_replication_constants_module` if the module path differs.

## Variables

Pass variables with `-e`. Failover and failback share the same variables; the
wrapper playbooks set `cinder_replication_action` for you.

| Variable | Default | Description |
|---|---|---|
| `cinder_replication_action` | none (set by the wrapper playbook) | `failover` or `failback`. Required when calling `cinder-replication.yml` directly. |
| `cinder_replication_target` | none | Required. The cinder-volume host as `<host>@<backend>`, exactly as shown by `cinder service-list`. Alias: `cinder_failover_target`. |
| `cinder_replication_backend_id` | empty | Failover only: the `backend_id` of the `replication_device` to fail over to. Failback always uses `default`. Alias: `cinder_failover_backend_id`. |
| `cinder_replication_execution_host` | `localhost` | Inventory host the play runs on. This must be the cinder-volume host if you rely on the capability gate or on reading `cinder.conf`. |
| `cinder_replication_cli` | `cinder` | Cinder client command. |
| `cinder_replication_openrc` | `$HOME/openrc` | OpenStack RC file that is sourced before every CLI call. |
| `cinder_replication_openrc_args` | empty | Arguments passed when sourcing the RC file. DevStack needs `admin admin`. |
| `cinder_replication_verify_services` | `true` | Capture the service table before the action and report the target row afterwards. |
| `cinder_replication_conf_path` | `/etc/cinder/cinder.conf` | File read to discover the backend's `replication_device` entries. |
| `cinder_replication_valid_backend_ids` | `[]` | Extra permitted `backend_id` values, added to the ones found in `cinder.conf`. |
| `cinder_replication_settle_retries` | `24` | Number of status polls after the action. |
| `cinder_replication_settle_delay` | `5` | Seconds between polls. The settle window is retries x delay (120 s by default). |
| `auto_failback_supported` | `false` | Set `true` to skip the driver capability gate. See [Driver capability gate](#driver-capability-gate). |
| `cinder_replication_python` | auto-detected | Python interpreter used for the capability check. |
| `cinder_replication_constants_module` | `cinder.volume.drivers.hpe.alletramp_constants` | Module that defines `AUTO_FAILBACK_SUPPORTED`. |

## How the workflow runs

`cinder-replication.yml` runs six phases in order. Any failed check stops the
play before anything is sent to Cinder, except the settle checks in phase 5.

| Phase | What it does | Stops when |
|---|---|---|
| 1. Preflight | Checks the action is `failover` or `failback` and a target is given. | Action invalid or target missing. |
| 1b. Capability gate | Reads `AUTO_FAILBACK_SUPPORTED` from the deployed driver, which gates both failover and failback. | Driver constants cannot be imported (play fails). If the flag is not `True`, the play ends as a no-op. |
| 2. Service discovery | Reads the cinder-volume services (`cinder service-list --withreplication`, with fallbacks to `service-list` and `openstack volume service list --long`) and selects the target record. | API unreachable or not authorized. Target is not a registered cinder-volume service, is not `up`, or is already `failing-over`. For failover, `replication_status` must be `enabled` or `failed-over`. |
| 3. Backend policy | Reads the `replication_device` `backend_id` values from the backend section of `cinder.conf` and validates the requested `backend_id`. | See the policy rules below. |
| 4. Idempotency gate | Compares the current status with the requested outcome. | Not a failure: the play ends as a no-op if failover finds the host already `failed-over`, or failback finds it already `enabled`. |
| 5. Execution | Runs `cinder failover-host <target> [--backend_id <id>]`, then polls the service record for the settle window. | The final status is `error`, `failover-error`, or the opposite steady state (see below). |
| 6. Post-change verification | Prints the target backend's row of the service table. | Not applicable. |

### Backend policy rules (phase 3)

- Failback only accepts an empty `backend_id` or `default`, and always sends `--backend_id default`.
- Failover never accepts `default`.
- If `cinder.conf` lists `replication_device` entries (or you passed `cinder_replication_valid_backend_ids`), the failover `backend_id` must be one of them. If the file cannot be read and no list is given, this check is skipped.
- If the host is already `failed-over`, a failover request must name the same `backend_id` as the host's current `active_backend_id`. To move to a different target, fail back to `default` first.

### Settle polling (phase 5)

`cinder failover-host` returns before the backend has finished, so the playbook
polls the target's `replication_status` every `cinder_replication_settle_delay`
seconds, up to `cinder_replication_settle_retries` times. It stops early only on
the expected status, `unknown`, `error` or `failover-error`. The opposite steady
state is not a stop condition, so the backend gets the whole window to start
transitioning.

| Action | Expected status | Failure statuses after the window |
|---|---|---|
| `failover` | `failed-over` | `error`, `failover-error`, `enabled` |
| `failback` | `enabled` | `error`, `failover-error`, `failed-over` |

`failing-over` after the window is a warning, not a failure: the transition is
still running and you should keep watching. A status of `unknown` is ignored.

## Result and status reference

| Play result | Meaning | What to do |
|---|---|---|
| `NO-OP` (capability) | `AUTO_FAILBACK_SUPPORTED` is not `True` in the deployed driver. Nothing was sent. | Apply the driver patch, restart the cinder services, retry. Or pass `-e auto_failback_supported=true` if you have verified the driver. |
| `NO-OP` (already in state) | The host is already `failed-over` (failover) or `enabled` (failback). | Nothing to do. Note that a failover cannot be re-run on a host that is already `failed-over`. |
| Completed | The host reached the expected status. | Check the volumes (below). |
| Warning: still in progress | Status was `failing-over` when polling ended. | Keep monitoring with the commands below. Not a failure. |
| Failed: error status | Host ended `error`, `failover-error`, or in the opposite state. | Read the cinder-volume log for the reason. |

The backend status only tells you the failover or failback workflow completed.
After every run, also check that replicated volumes and consistency groups
report the expected `replication_status` and backend assignment:

```bash
cinder service-list --withreplication
cinder list --all-projects --field ID,Name,Status,os-vol-host-attr:host,replication_status
```

How driver outcomes show up in this playbook:

| Driver outcome | Host status after the action | Playbook result |
|---|---|---|
| All volumes switched | `failed-over` (failover) or `enabled` (failback) | Completed |
| Request rejected (for example an RCG that is not started, or the primary array still down on failback) | Unchanged: `enabled` after a failover request, `failed-over` after a failback request | Failed (opposite state). The cinder-volume log has the reason. |
| Driver raised another error | `failover-error` | Failed |
| Some volumes failed individually | Host `failed-over` or `enabled` | Completed, but the affected volumes show `replication_status` `error`. Always check the volume list. |

See [Driver behavior: failover and failback](#driver-behavior-failover-and-failback)
for the driver's scenarios, status rules and operator notes.

## Driver behavior: failover and failback

This section describes what the HPE Alletra MP driver does for Peer Persistence
(active-active) volumes and groups, and what Cinder shows afterwards. Read it
before running any failover or failback action. It describes the
driver, not this playbook; the playbook only reads the resulting host status.

### Scenarios

| Action | Primary array | What the driver does | Volume | Host |
|---|---|---|---|---|
| Failover | Up (planned) | `CHANGE_TO_SECONDARY` (action 8) on the primary array. | `failed-over` | `failed-over` |
| Failover | Down (unplanned) | `CHANGE_TO_PRIMARY` (action 7) on the DR array. No command is sent to the primary array. | `failed-over` | `failed-over` |
| Failback | Up | `CHANGE_TO_SECONDARY` (action 8) on the DR array, then waits up to 60 s for the original primary to confirm the primary role, natural direction and sync. | `enabled` | `enabled` |
| Failback | Down | Nothing. The request is rejected before any array change: "Cannot fail back volume/group `<id>`: the primary array is still down. Recover it and retry." | No updates | Stays `failed-over` |
| Failback | Session cannot be opened (credentials, session limit) | Nothing. The request is rejected before any array change: "Cannot fail back: a session to the primary array could not be established. Check the array's session limit and credentials, then retry." | No updates | Stays `failed-over` |

Failover with a remote copy group that is not started (WSAPI 276):

- **Primary up:** the request is rejected ("The host is not ready to be failed
  over") and the host stays `enabled`. Resume replication, wait for the volumes
  to resynchronize, then retry.
- **Primary down:** replication cannot be resumed, so only the affected volume
  or group is marked `error`. The rest of the host fails over normally.

Any other error is covered by the status rules below.

### Cinder host and volume status rules

| Driver outcome | Host (service) status | Volume status |
|---|---|---|
| Driver returns normally (failover) | `failed-over` | Each volume takes the status the driver returned: `failed-over` or `error` |
| Driver returns normally (failback) | `enabled` | `enabled`, or `error` if the driver returned that |
| Driver raises an `InvalidReplicationTarget` error (request rejected) | Unchanged (`enabled` before failover, `failed-over` before failback) | No updates applied |
| Driver raises any other exception | `failover-error`, and the service is disabled | No updates applied |

### Prerequisites

- Replication is configured on the backend (`replication_device` is set).
- The failover target is a valid `backend_id`.
- For failback, the original primary array is reachable.
- Every Peer Persistence RCG is started and fully synchronized. A stopped RCG returns WSAPI 276. With the primary up the action is rejected; with the primary down only that volume or group is marked `error`.
- Before failback, the DR RCGs are in sync so the primary can take the role back.

### Notes for operators

- **Re-running:** after a failed failover or failback, fix the cause and run the same command again.
  - RCGs already switched are skipped. For failover that means RCGs already primary or role-reversed. For failback it means RCGs already secondary and in natural direction.
  - Failover also skips volumes Cinder already shows as `failed-over`.
  - The playbook's own idempotency gate (phase 4) is separate: it ends as a no-op only when the host is already `failed-over` (failover) or `enabled` (failback).
- **Primary-down detection:** only a connection failure (host unreachable or timeout) counts as "down". Any other error on the probe request, such as a refused connection or a certificate error, is treated as the array being up, and the action fails later with that error. If a session to the primary cannot be opened at all, failback stops before changing anything.
- **Driver restarted while failed over:** the driver may be bound to the DR array. Failover and failback then build a session to the primary first. If the primary is unreachable the driver continues on the current binding; any other session error rejects the request instead of running on the wrong array.
- **Repeated failover:** a failover repeated to the same target is a no-op. Recover a volume whose RCG was restored on the array with a failback, not by repeating the failover.
- **Partial results:** with several volumes, a rejected or failed action can leave some RCGs switched on the array while Cinder still shows the old state. Check the RCGs on both arrays before retrying.
- **Volumes in `error`:** after a failover with per-volume errors, the host is already `failed-over`. Fix the RCG on the array, then correct the volume's `replication_status` in Cinder.
- **Rejected requests:** the host stays in its old state, so the playbook only reports the failure after the full settle window.

## Console output

The included `ansible.cfg` enables the `minimal_progress` callback. It prints
one `-> <task>` line per task with PASSED, CHANGED, INFO or OK, groups tasks
under phase headings, hides skipped tasks, and prints a highlighted message only
on failure, followed by a summary.

- Ansible only reads `ansible.cfg` from the directory you run it in. Run from this directory, or set `ANSIBLE_CONFIG=/abs/path/alletramp/playbooks/openstack_cinder/ansible.cfg`.
- Ansible ignores an `ansible.cfg` in a world-writable directory. Run `chmod go-w` on it.
- For the standard Ansible output, set `ANSIBLE_STDOUT_CALLBACK=default`.
- If you rename a task in `cinder-replication.yml`, update the matching text in `callback_plugins/minimal_progress.py`, otherwise it is shown in the wrong phase.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `Unable to query Cinder services` | The client could not list services or you are not admin. Check the RC file path and add `-e cinder_replication_openrc_args='admin admin'` on DevStack. The error text lists each client attempt. |
| `NO-OP: AUTO_FAILBACK_SUPPORTED is not defined` or `set to False` | The deployed driver does not have the feature enabled. Apply the driver patch and restart the cinder services, or use the override. |
| `Unable to import '<module>'` | The play could not import the driver constants. Set `cinder_replication_python` to the interpreter cinder runs under and, if needed, `cinder_replication_constants_module`. The check assumes the play runs on the cinder-volume host. |
| `host is not a registered cinder-volume service` | `cinder_replication_target` does not match the Host column. The message lists the known hosts. |
| `service state is 'down'` | The cinder-volume service for the target is not running. Start it and retry. |
| `backend is mid-transition` | The backend is `failing-over`. Wait for it to settle. |
| `Cinder failover requires replication_status 'enabled' or 'failed-over'` | The host is in an error or other state. Check `cinder service-list --withreplication` and the cinder-volume log. |
| `backend_id ... is not a configured replication target` | The value does not match a `backend_id` in the `replication_device` lines of the backend section. Check `cinder.conf`. |
| `Backend is already failed over to '<id>'` | Fail back to `default` before failing over to a different target. |
| `Failback always targets 'default'` | Remove `cinder_replication_backend_id`, or set it to `default`. |
| Warning that the transition is still in progress | The backend did not finish within the settle window. Raise `cinder_replication_settle_retries` or `cinder_replication_settle_delay`, or monitor with the commands above. |
| `The transition has FAILED` | The host ended `error`, `failover-error`, or never left its old state. Check the cinder-volume log for the driver's message. |
| Output shows full `TASK [...]` banners | `ansible.cfg` was not picked up. See [Console output](#console-output). |

## Limitations

- The playbooks orchestrate Cinder replication operations and do not perform
  storage failover directly. The HPE Alletra MP Cinder driver does the array
  work.
- Successful backend failover does not guarantee application-level
  availability.
- Network connectivity between the execution host, the OpenStack services and
  the target backend must be available.
- Failback requires the original primary array and replication relationships to
  be healthy and synchronized. Otherwise the driver rejects the request and the
  backend stays in its old state.
- The backend status only shows that the workflow completed. Individual volumes
  can still end in `error`, so always check them after a run.
- Mistakes during manual execution can leave a backend in an intermediate or
  inconsistent failover state. Use the playbooks rather than running
  `cinder failover-host` by hand.

## OpenStack-Ansible integration

An OpenStack-Ansible playbook can import the standalone entry point from the
path where this directory is checked out:

```yaml
---
- name: Import standalone Cinder failover workflow
  import_playbook: /opt/hpe_storage_ansible_modules/alletramp/playbooks/openstack_cinder/cinder-failover.yml
```

The imported playbook accepts the same `cinder_replication_*` variables as
direct execution, so the management interface does not change.