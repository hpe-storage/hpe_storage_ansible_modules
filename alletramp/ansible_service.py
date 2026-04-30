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
"""
Unified Ansible Client that combines v3 workflows (for most operations)
and v1 workflows (for remote copy group, hosts and vluns operations).

This client expects both hpe_storage_flowkit (v1) and hpe_storage_flowkit_v3 (v3)
to be importable.

Note: v1 API is used for Host, VLUN, and Remote Copy Group operations because these
features are not yet fully supported in v3 API. Migration to v3 will occur once all
required operations are available in the v3 API endpoint.
"""

# Import v3 Flowkit modules for most workflows
from hpe_storage_flowkit_py.v3.src.core import exceptions
from hpe_storage_flowkit_py.v3.src.core.session import SessionManager as SessionManagerV3
from hpe_storage_flowkit_py.v3.src.core.logger import Logger
from hpe_storage_flowkit_py.v3.src.workflows.volumeset import VolumeSetWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.cpg import CpgWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.volume import VolumeWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.snapshot import SnapshotWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.qos import QosWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.task import TaskManager
from hpe_storage_flowkit_py.v3.src.workflows.clone import CloneWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.hostset import HostSetWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.ntp import NTPWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.dns import DNSWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.schedule import ScheduleWorkflow
from hpe_storage_flowkit_py.v3.src.workflows.user import UserWorkflow

# Import v1 Flowkit modules for remote copy operations only
from hpe_storage_flowkit_py.v1.src.core.session import SessionManager as SessionManagerV1
from hpe_storage_flowkit_py.v1.src.core.ssh import SSHClient
from hpe_storage_flowkit_py.v1.src.core import exceptions as exceptions_v1
from hpe_storage_flowkit_py.v1.src.workflows.remote_copy import RemoteCopyGroupWorkflow
from hpe_storage_flowkit_py.v1.src.workflows.system import SystemWorkflow
from hpe_storage_flowkit_py.v1.src.utils import remote_copy_utils
from hpe_storage_flowkit_py.v1.src.validators.remote_copy_validator import validate_remote_copy_group_params
from hpe_storage_flowkit_py.v1.src.workflows.host import HostWorkflow
from hpe_storage_flowkit_py.v1.src.utils import host_utils
from hpe_storage_flowkit_py.v1.src.validators.host_validator import validate_host_params
from hpe_storage_flowkit_py.v1.src.workflows.vlun import VLUNWorkflow
from hpe_storage_flowkit_py.v1.src.utils.vlun_utils import find_vlun, build_payload
from hpe_storage_flowkit_py.v1.src.validators.vlun_validator import validate_params

class AnsibleClient:
    # API version constants
    API_VERSION_V1 = "v1"
    API_VERSION_V3 = "v3"
    
    def __init__(self, base_path, username, password, log_file='ansible_client.log'):
        """
        Initialize Ansible client facade with dual session managers.

        Arguments:
            base_path: IP address or hostname of the HPE Storage array (e.g., "10.201.5.12")
                      The adapter will construct the full API URL internally.
            username: Username for authentication
            password: Password for authentication

        Note:
            - Uses v3 workflows for most operations (cpg, volume, snapshot, qos, task, clone, volumeset,
			  hostset, schedule)
            - Uses v1 workflows for remote copy group operations
            - Maintains separate session managers for v1 and v3 APIs
        """

        # Initialize logger
        self.logger = Logger(name='ansible_client', log_file=log_file)
        self.logger.info("Initializing AnsibleClient ")

        # Construct API URLs for both v3 and v1 endpoints
        # v3 is used for most operations, v1 for host, vlun, and remote copy group operations
        self.api_url_v3 = self._normalize_api_url(base_path, self.API_VERSION_V3)
        self.api_url_v1 = self._normalize_api_url(base_path, self.API_VERSION_V1)
        self.username = username
        self.password = password
        
        # Initialize v3 session manager for v3 workflows
        self.logger.info(f"Creating v3 session manager for {self.api_url_v3}")
        self.session_manager_v3 = SessionManagerV3(self.api_url_v3, self.username, self.password)

        # Initialize v1 session manager for remote copy, hosts and vluns operations
        self.logger.info(f"Creating v1 session manager for {self.api_url_v1}")
        self.session_manager_v1 = SessionManagerV1(self.api_url_v1, self.username, self.password)

        # Initialize SSH client for remote copy operations
        self.logger.info(f"Creating SSH client for {self.api_url_v1}")
        self.ssh_client = SSHClient(self.api_url_v1, self.username, self.password)

        # Initialize v3 workflows
        self.logger.info("Initializing v3 workflows")
        self.task_workflow = TaskManager(self.session_manager_v3)
        self.volumeset_workflow = VolumeSetWorkflow(self.session_manager_v3, self.task_workflow)
        self.hostset_workflow = HostSetWorkflow(self.session_manager_v3, self.task_workflow)
        self.cpg_workflow = CpgWorkflow(self.session_manager_v3, self.task_workflow)
        self.volume_workflow = VolumeWorkflow(self.session_manager_v3, self.task_workflow)
        self.snapshot_workflow = SnapshotWorkflow(self.session_manager_v3, self.task_workflow)
        self.qos_workflow = QosWorkflow(self.session_manager_v3, self.task_workflow)
        self.clone_workflow = CloneWorkflow(self.session_manager_v3, self.task_workflow)
        self.ntp_workflow = NTPWorkflow(self.session_manager_v3, self.task_workflow)
        self.dns_workflow = DNSWorkflow(self.session_manager_v3, self.task_workflow)
        self.schedule_workflow=ScheduleWorkflow(self.session_manager_v3, self.task_workflow)
        self.user_workflow = UserWorkflow(self.session_manager_v3, self.task_workflow)

        # Initialize v1 workflows
        # Note: Host, VLUN, and Remote Copy Group operations use v1 API temporarily as these features
        # are not yet fully supported in v3. Will migrate to v3 once all operations are available.
        self.logger.info("Initializing v1 workflows")
        self.remote_copy_workflow = RemoteCopyGroupWorkflow(self.session_manager_v1, self.ssh_client)
        self.system_workflow = SystemWorkflow(self.session_manager_v1)
        self.vlun_workflow = VLUNWorkflow(self.session_manager_v1)
        self.host_workflow = HostWorkflow(self.session_manager_v1)

        self.logger.info("AnsibleClient initialization complete")

    @staticmethod
    def _normalize_api_url(base_path, version):
        """
        Normalize and construct the API URL from base path and version.

        Arguments:
            base_path: IP address or hostname of the HPE Storage array
            version: API version (e.g., "v1", "v3")

        Returns:
            str: Fully constructed API URL (e.g., "https://x.x.x.x/api/v3")
        """
        return f"https://{base_path}/api/{version}"

    # Volume Set related workflow operations
    def create_volumeset(self, name, appSetType=None, **kwargs):
        self.logger.info(f"AnsibleClient: Creating volume set '{name}' with type '{appSetType}'")
        try:
            resp = self.volumeset_workflow.create_volumeset(name, appSetType, **kwargs)
            self.logger.info(f"AnsibleClient: Volume set '{name}' created successfully")
            return (True, True, f"Volume set {name} created successfully", {})
        except exceptions.VolumeSetAlreadyExists as ve:
            self.logger.warning(f"AnsibleClient: Volume set '{name}' already exists")
            return (True, False, str(ve), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume set '{name}' creation failed: {e}")
            return (False, False, f"Volume set {name} creation failed | {e}", {})

    def modify_volumeset(self, name, new_name=None, **kwargs):
        self.logger.info(f"AnsibleClient: Modifying volume set '{name}'")
        try:
            resp = self.volumeset_workflow.modify_volumeset(name, new_name, **kwargs)
            self.logger.info(f"AnsibleClient: Volume set '{name}' modified successfully")
            return (True, True, f"Volume set {name} modified successfully", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume set '{name}' modification failed: {e}")
            return (False, False, f"Volume set {name} modification failed | {e}", {})

    def delete_volumeset(self, name):
        self.logger.info(f"AnsibleClient: Deleting volume set '{name}'")
        try:
            resp = self.volumeset_workflow.delete_volumeset(name)
            self.logger.info(f"AnsibleClient: Volume set '{name}' deleted successfully")
            return (True, True, f"Volume set {name} deleted successfully", {})
        except exceptions.VolumeSetDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume set '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume set '{name}' deletion failed: {e}")
            return (False, False, f"Volume set {name} deletion failed | {e}", {})

    def add_volumes_to_volumeset(self, name, members):
        self.logger.info(f"AnsibleClient: Adding volumes to volume set '{name}'")
        try:
            resp = self.volumeset_workflow.add_volumes_to_volumeset(name, members)
            self.logger.info(f"AnsibleClient: Volumes added to volume set '{name}' successfully")
            return (True, True, f"Volumes added to volume set {name} successfully", {})
        except exceptions.VolumeSetMembersAlreadyPresent as vmp:
            self.logger.warning(f"AnsibleClient: Members already present in volume set '{name}'")
            return (True, False, str(vmp), {})
        except exceptions.VolumeSetDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume set '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Adding volumes to volume set '{name}' failed: {e}")
            return (False, False, f"Adding volumes to volume set {name} failed | {e}", {})

    def remove_volumes_from_volumeset(self, name, members):
        self.logger.info(f"AnsibleClient: Removing volumes from volume set '{name}'")
        try:
            resp = self.volumeset_workflow.remove_volumes_from_volumeset(name, members)
            self.logger.info(f"AnsibleClient: Volumes removed from volume set '{name}' successfully")
            return (True, True, f"Volumes removed from volume set {name} successfully", {})
        except exceptions.VolumeSetMembersAlreadyRemoved as vmr:
            self.logger.warning(f"AnsibleClient: Members already removed from volume set '{name}'")
            return (True, False, str(vmr), {})
        except exceptions.VolumeSetDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume set '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Removing volumes from volume set '{name}' failed: {e}")
            return (False, False, f"Removing volumes from volume set {name} failed | {e}", {})

    # cpg operations
    def create_cpg(self, name, **kwargs):
        self.logger.info(f"AnsibleClient: Creating CPG '{name}'")
        try:
            resp = self.cpg_workflow.create_cpg(name, **kwargs)
            self.logger.info(f"AnsibleClient: CPG '{name}' created successfully. Response: {resp}")
            return (True, True, f"CPG {name} created successfully", {})
        except exceptions.CpgAlreadyExists as ce:
            self.logger.warning(f"AnsibleClient: CPG '{name}' already exists")
            return (True, False, str(ce), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: CPG '{name}' creation failed: {e}")
            return (False, False, f"CPG {name} creation failed | {e}", {})

    def delete_cpg(self, name):
        self.logger.info(f"AnsibleClient: Deleting CPG '{name}'")
        try:
            resp = self.cpg_workflow.delete_cpg(name)
            self.logger.info(f"AnsibleClient: CPG '{name}' deleted successfully. Response: {resp}")
            return (True, True, f"CPG {name} deleted successfully", {})
        except exceptions.CpgDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: CPG '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: CPG '{name}' deletion failed: {e}")
            return (False, False, f"CPG {name} deletion failed | {e}", {})

    # volume operations
    def create_volume(self, name, cpg, size, **kwargs):
        self.logger.info(f"AnsibleClient: Creating volume '{name}' on CPG '{cpg}' with size {size}")
        try:
            resp = self.volume_workflow.create_volume(name, cpg, size, **kwargs)
            self.logger.info(f"AnsibleClient: Volume '{name}' created successfully. Response: {resp}")
            return (True, True, f"Volume {name} created successfully", {})
        except exceptions.VolumeAlreadyExists as ve:
            self.logger.warning(f"AnsibleClient: Volume '{name}' already exists")
            return (True, False, str(ve), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume '{name}' creation failed: {e}")
            return (False, False, f"Volume {name} creation failed | {e}", {})

    def delete_volume(self, name):
        self.logger.info(f"AnsibleClient: Deleting volume '{name}'")
        try:
            resp = self.volume_workflow.delete_volume(name)
            self.logger.info(f"AnsibleClient: Volume '{name}' deleted successfully. Response: {resp}")
            return (True, True, f"Volume {name} deleted successfully", {})
        except exceptions.VolumeDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume '{name}' deletion failed: {e}")
            return (False, False, f"Volume {name} deletion failed | {e}", {})

    def modify_volume(self, vol_name, **kwargs):
        self.logger.info(f"AnsibleClient: Modifying volume '{vol_name}'")
        try:
            resp = self.volume_workflow.modify_volume(vol_name, **kwargs)
            self.logger.info(f"AnsibleClient: Volume '{vol_name}' modified successfully. Response: {resp}")
            return (True, True, f"Volume {vol_name} modified successfully", {})
        except exceptions.VolumeDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume '{vol_name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume '{vol_name}' modification failed: {e}")
            return (False, False, f"Volume {vol_name} modification failed | {e}", {})
    
    #TODO
    #This method is currently used by Ansible modules and returns a simple boolean
    #instead of the standard (success_status, changed_flag, message, issue_details) tuple
    #that other AnsibleClient methods return.
    # Refactoring the method to use the standard return format or make this method private
    # and move the usage of this method computation from modules to AnsibleClient itself.
    def is_volume_exists(self, name):
        self.logger.info(f"AnsibleClient: Getting volume '{name}'")
        try:
            resp=self.volume_workflow.get_volume_info(name)
            if resp:
                self.logger.info(f"AnsibleClient: Volume '{name}' retrieved successfully. Response: {resp}")
                return True
            else:
                self.logger.warning(f"AnsibleClient: Volume '{name}' not found. Response: {resp}")
                return False
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume '{name}' retrieval failed: {e}")
            raise

    def grow_volume(self, name, growth_size_mib):
        self.logger.info(f"AnsibleClient: Growing volume '{name}' by {growth_size_mib} MiB")
        try:
            resp = self.volume_workflow.grow_volume(name, growth_size_mib)
            self.logger.info(f"AnsibleClient: Volume '{name}' size modified successfully. Response: {resp}")
            return (True, True, f"Volume {name} size modified", {})
        except exceptions.VolumeDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume '{name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume '{name}' size modification failed: {e}")
            return (False, False, f"Volume {name} size modification failed | {e}", {})

    def tune_volume(self, name, cpg, **kwargs):
        self.logger.info(f"AnsibleClient: Tuning volume '{name}' with CPG '{cpg}'")
        try:
            resp = self.volume_workflow.tune_volume(name, cpg, **kwargs)
            self.logger.info(f"AnsibleClient: Volume '{name}' tuned successfully. Response: {resp}")
            return (True, True, f"Volume {name} tuned successfully", {})
        except exceptions.VolumeDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume '{name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Volume '{name}' tuning failed: {e}")
            return (False, False, f"Volume {name} tuning failed | {e}", {})

    # snapshot operations
    def create_snapshot(self, volume_name, snapshot_name, **kwargs):
        self.logger.info(f"AnsibleClient: Creating snapshot '{snapshot_name}' for volume '{volume_name}'")
        try:
            resp = self.snapshot_workflow.create_snapshot(volume_name, snapshot_name, **kwargs)
            self.logger.info(f"AnsibleClient: Snapshot '{snapshot_name}' created successfully for volume '{volume_name}'. Response: {resp}")
            return (True, True, f"Snapshot {snapshot_name} created successfully for volume {volume_name}", {})
        except exceptions.VolumeAlreadyExists as ve:
            self.logger.warning(f"AnsibleClient: Snapshot '{snapshot_name}' already exists")
            return (True, False, str(ve), {})
        except exceptions.VolumeDoesNotExist as vne:
            self.logger.warning(f"AnsibleClient: Volume '{volume_name}' does not exist")
            return (False, False, str(vne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Snapshot '{snapshot_name}' creation failed: {e}")
            return (False, False, f"Snapshot {snapshot_name} creation failed | {e}", {})

    def delete_snapshot(self, snapshot_name):
        self.logger.info(f"AnsibleClient: Deleting snapshot '{snapshot_name}'")
        try:
            resp = self.snapshot_workflow.delete_snapshot(snapshot_name)
            self.logger.info(f"AnsibleClient: Snapshot '{snapshot_name}' deleted successfully. Response: {resp}")
            return (True, True, f"Snapshot {snapshot_name} deleted successfully", {})
        except exceptions.VolumeDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Snapshot '{snapshot_name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Snapshot '{snapshot_name}' deletion failed: {e}")
            return (False, False, f"Snapshot {snapshot_name} deletion failed | {e}", {})

    def promote_snapshot_volume(self, snapshot_name, **kwargs):
        self.logger.info(f"AnsibleClient: Promoting snapshot '{snapshot_name}'")
        try:
            resp = self.snapshot_workflow.promote_snapshot_volume(snapshot_name, **kwargs)
            self.logger.info(f"AnsibleClient: Snapshot '{snapshot_name}' promoted successfully. Response: {resp}")
            return (True, True, f"Snapshot {snapshot_name} promoted successfully", {})
        except exceptions.VolumeDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Snapshot '{snapshot_name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Snapshot '{snapshot_name}' promotion failed: {e}")
            return (False, False, f"Snapshot {snapshot_name} promotion failed | {e}", {})

    # qos operations
    def create_qos(self, vvs_name, qos, **kwargs):
        self.logger.info(f"AnsibleClient: Creating QoS rule for '{vvs_name}'")
        try:
            resp = self.qos_workflow.create_qos(vvs_name, qos, **kwargs)
            self.logger.info(f"AnsibleClient: QoS rule for '{vvs_name}' created successfully. Response: {resp}")
            return (True, True, f"QoS rule for {vvs_name} created successfully", {})
        except exceptions.QosAlreadyExists as qe:
            self.logger.warning(f"AnsibleClient: QoS rule '{vvs_name}' already exists")
            return (True, False, str(qe), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: QoS rule creation failed: {e}")
            return (False, False, f"QoS rule creation failed | {e}", {})

    def modify_qos(self, name, **kwargs):
        self.logger.info(f"AnsibleClient: Modifying QoS rule '{name}'")
        try:
            resp = self.qos_workflow.modify_qos(name, **kwargs)
            self.logger.info(f"AnsibleClient: QoS rule '{name}' modified successfully. Response: {resp}")
            return (True, True, f"QoS rule {name} modified successfully", {})
        except exceptions.QosDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: QoS rule '{name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: QoS rule '{name}' modification failed: {e}")
            return (False, False, f"QoS rule {name} modification failed | {e}", {})

    def delete_qos(self, name):
        self.logger.info(f"AnsibleClient: Deleting QoS rule '{name}'")
        try:
            resp = self.qos_workflow.delete_qos(name)
            self.logger.info(f"AnsibleClient: QoS rule '{name}' deleted successfully. Response: {resp}")
            return (True, True, f"QoS rule {name} deleted successfully", {})
        except exceptions.QosDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: QoS rule '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: QoS rule '{name}' deletion failed: {e}")
            return (False, False, f"QoS rule {name} deletion failed | {e}", {})

    def get_qos(self, name):
        self.logger.info(f"AnsibleClient: Getting QoS rule '{name}'")
        try:
            resp = self.qos_workflow.get_qos(name)
            if resp:
                self.logger.info(f"AnsibleClient: QoS rule '{name}' retrieved successfully. Response: {resp}")
                return (True, False, f"QoS rule {name} retrieved successfully", {"response": resp})
            self.logger.warning(f"AnsibleClient: QoS rule '{name}' not found. Response: {resp}")
            return (False,False,f"Qos rule {name} not found", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: QoS rule '{name}' retrieval failed: {e}")
            return (False, False, f"QoS rule {name} retrieval failed | {e}", {})

    def list_qos(self):
        self.logger.info(f"AnsibleClient: Listing QoS rules")
        try:
            resp = self.qos_workflow.list_qos()
            self.logger.info(f"AnsibleClient: QoS rules listed successfully. Response: {resp}")
            return (True, False, f"QoS rules listed successfully", {"response": resp})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: QoS rules listing failed: {e}")
            return (False, False, f"QoS rules listing failed | {e}", {})
    
    #task operations
    def wait_for_task(self, task_id):
        self.logger.info(f"AnsibleClient: Waiting for task '{task_id}'")
        try:
            resp = self.task_workflow.wait_for_task_to_end(task_id)
            self.logger.info(f"AnsibleClient: Task '{task_id}' completed successfully")
            return (True, False, f"Task {task_id} completed successfully", {'response': resp})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Task '{task_id}' wait failed: {e}")
            return (False, False, f"Task {task_id} wait failed | {e}", {})

    def get_task(self, task_id):
        self.logger.info(f"AnsibleClient: Getting task '{task_id}'")
        try:
            resp = self.task_workflow.get_task(task_id)
            self.logger.info(f"AnsibleClient: Task '{task_id}' retrieved successfully")
            return (True, False, f"Task {task_id} retrieved successfully", {'response': resp})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Task '{task_id}' retrieval failed: {e}")
            return (False, False, f"Task {task_id} retrieval failed | {e}", {})

    def get_all_task(self):
        try:
            resp = self.task_workflow.get_all_tasks()
            return resp
        except Exception:
            raise

    # clone operations
    def copy_volume(self, src_name, dest_name, **kwargs):
        self.logger.info(f"AnsibleClient: Copying volume from '{src_name}' to '{dest_name}'")
        try:
            resp = self.clone_workflow.copy_volume(src_name, dest_name, **kwargs)
            self.logger.info(f"AnsibleClient: Clone from '{src_name}' to '{dest_name}' created successfully. Response: {resp}")
            return(True,True,f"Clone created successfully",{})
        except exceptions.VolumeDoesNotExist as vne:
            self.logger.warning(f"AnsibleClient: Source volume '{src_name}' does not exist")
            return (False, False, str(vne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Clone creation from '{src_name}' to '{dest_name}' failed: {e}")
            return (False, False, f"Clone creation failed| {e}", {})

    def online_phy_copy_exist(self, src_name, phycopy_name):
        """
        Returns True if:
        - physical copy volume already exists OR
        - physical copy volume does not exist but task is still in progress

        Returns False if:
        - physical copy volume does not exist AND
        - task is finished / failed / canceled OR task not found
        """
        self.logger.info(f"AnsibleClient: Checking if online physical copy '{phycopy_name}' exists for source '{src_name}'")
        try:
            resp = self.clone_workflow.online_physical_copy_exist(src_name, phycopy_name)
            self.logger.info(f"AnsibleClient: Online physical copy check completed: {resp}")
            return resp
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Online physical copy existence check failed: {e}")
            return e

    def offline_phy_copy_exist(self, src_name, phycopy_name):
        """
        Returns True if:
        - physical copy volume already exists OR
        - physical copy volume does not exist but task is still in progress

        Returns False if:
        - physical copy volume does not exist AND
        - task is finished / failed / canceled OR task not found
        """
        self.logger.info(f"AnsibleClient: Checking if offline physical copy '{phycopy_name}' exists for source '{src_name}'")
        try:
            resp = self.clone_workflow.offline_physical_copy_exist(src_name, phycopy_name)
            self.logger.info(f"AnsibleClient: Offline physical copy check completed: {resp}")
            return resp
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Offline physical copy existence check failed: {e}")
            return e

    def resync_physical_copy(self, volume_name, **kwargs):
        self.logger.info(f"AnsibleClient: Resyncing physical copy for volume '{volume_name}'")
        try:
            resp = self.clone_workflow.resync_physical_copy(volume_name, **kwargs)
            self.logger.info(f"AnsibleClient: Physical copy for volume '{volume_name}' resynced successfully")
            return (True, True, f"Resync physical copy operation completed successfully", {"response": resp})
        except exceptions.VolumeDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume '{volume_name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Resync physical copy operation for volume '{volume_name}' failed: {e}")
            return (False, False, f"Resync operation failed| {e}", {})

    def stop_physical_copy(self, volume_name):
        self.logger.info(f"AnsibleClient: Stopping physical copy for volume '{volume_name}'")
        try:
            resp = self.clone_workflow.stop_physical_copy(volume_name)
            self.logger.info(f"AnsibleClient: Physical copy for volume '{volume_name}' stopped successfully. Response: {resp}")
            return (True, True, f"Stop physical copy operation completed successfully", {"response": resp})
        except exceptions.VolumeDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Volume '{volume_name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Stop physical copy operation for volume '{volume_name}' failed: {e}")
            return (False, False, f"Stop operation failed| {e}", {})
    #Host Set related workflow operations
    def create_hostset(self, name, **kwargs):
        self.logger.info(f"AnsibleClient: Creating host set '{name}'")
        try:
            resp = self.hostset_workflow.create_hostset(name, **kwargs)
            self.logger.info(f"AnsibleClient: Host set '{name}' created successfully")
            return (True, True, f"Host set {name} created successfully", {})
        except exceptions.HostSetAlreadyExists as ve:
            self.logger.warning(f"AnsibleClient: Host set '{name}' already exists")
            return (True, False, str(ve), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Host set '{name}' creation failed: {e}")
            return (False, False, f"Host set {name} creation failed | {e}", {})
    def delete_hostset(self, name):
        self.logger.info(f"AnsibleClient: Deleting host set '{name}'")
        try:
            resp = self.hostset_workflow.delete_hostset(name)
            self.logger.info(f"AnsibleClient: Host set '{name}' deleted successfully")
            return (True, True, f"Host set {name} deleted successfully", {})
        except exceptions.HostSetDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Host set '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Host set '{name}' deletion failed: {e}")
            return (False, False, f"Host set {name} deletion failed | {e}", {})
    def add_hosts_to_hostset(self, name, members):
        self.logger.info(f"AnsibleClient: Adding hosts to host set '{name}'")
        try:
            resp = self.hostset_workflow.add_hosts_to_hostset(name, members)
            self.logger.info(f"AnsibleClient: Hosts added to host set '{name}' successfully")
            return (True, True, f"Hosts added to host set {name} successfully", {})
        except exceptions.HostSetMembersAlreadyPresent as hmp:
            self.logger.warning(f"AnsibleClient: Members already present in host set '{name}'")
            return (True, False, str(hmp), {})
        except exceptions.HostSetDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Host set '{name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Adding hosts to host set '{name}' failed: {e}")
            return (False, False, f"Adding hosts to host set {name} failed | {e}", {})
    
    def remove_hosts_from_hostset(self, name, members):
        self.logger.info(f"AnsibleClient: Removing hosts from host set '{name}'")
        try:
            resp = self.hostset_workflow.remove_hosts_from_hostset(name, members)
            self.logger.info(f"AnsibleClient: Hosts removed from host set '{name}' successfully")
            return (True, True, f"Hosts removed from host set {name} successfully", {})
        except exceptions.HostSetMembersAlreadyRemoved as hmr:
            self.logger.warning(f"AnsibleClient: Members already removed from host set '{name}'")
            return (True, False, str(hmr), {})
        except exceptions.HostSetDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Host set '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Removing hosts from host set '{name}' failed: {e}")
            return (False, False, f"Removing hosts from host set {name} failed | {e}", {})

    #NTP and datetime related workflow operations
    def configure_datetime(self, date_time=None, ntp_addresses=None, timezone=None):
        """Configure NTP servers, timezone, and datetime settings.
        
        Args:
            date_time (str, optional): Date/time in format MM/dd/yyyy HH:mm:ss. Cannot be used with ntp_addresses.
            ntp_addresses (list, optional): List of NTP server addresses. Cannot be used with date_time.  
            timezone (str, required): Timezone identifier (required)
            
        Returns:
            tuple: (success, changed, message, data)
        
        Note:

            - System UID is automatically fetched from the storage system if not provided.
            - Either date_time OR ntp_addresses must be provided, but not both.
            - Timezone is always required.
        """
        self.logger.info(f"AnsibleClient: Configuring datetime with timezone: {timezone}")
        try:
            resp = self.ntp_workflow.configure_datetime(date_time, ntp_addresses, timezone)
            self.logger.info(f"AnsibleClient: Datetime settings configured successfully")
            return (True, True, f"Successfully configured datetime settings", {})
            
        except exceptions.SystemDoesNotExist as sne:
            self.logger.warning(f"AnsibleClient: System not found for datetime configuration: {sne}")
            return (True, False, str(sne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Failed to configure datetime settings: {e}")
            return (False, False, f"Failed to configure datetime settings: {e}", {})

    def get_system_info(self, system_uid=None):
        """Get system information.
        
        Args:
            system_uid (str, optional): System UID to get info for. If None, gets all systems.
            
        Returns:
            tuple: (success, changed, message, data)
        """
        self.logger.info(f"AnsibleClient: Getting system information for UID: {system_uid}")
        try:
            resp = self.ntp_workflow.get_system_info(system_uid)
            self.logger.info(f"AnsibleClient: System information retrieved successfully")
            return (True, False, f"Successfully retrieved system information", resp)
        except exceptions.SystemDoesNotExist as sne:
            self.logger.warning(f"AnsibleClient: System not found: {sne}")
            return (True, False, str(sne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Failed to get system information: {e}")
            return (False, False, f"Failed to get system information: {e}", {})

    # DNS and Network Configuration related workflow operations
    def configure_network(self, dns_addresses, ipv4_address=None, ipv4_gateway=None, 
                         ipv4_subnet_mask=None, ipv6_address=None, ipv6_gateway=None, 
                         ipv6_prefix_len=None, proxy_params=None, commit_change=None, 
                         slaac_enable=None):
        """Configure DNS and network settings for the storage system.
        
        Args:
            dns_addresses (list): List of DNS server addresses (required)
            ipv4_address (str, optional): IPv4 address for the system
            ipv4_gateway (str, optional): IPv4 gateway address
            ipv4_subnet_mask (str, optional): IPv4 subnet mask
            ipv6_address (str, optional): IPv6 address for the system
            ipv6_gateway (str, optional): IPv6 gateway address
            ipv6_prefix_len (str, optional): IPv6 prefix length
            proxy_params (dict, optional): Proxy configuration parameters
            commit_change (bool, optional): Whether to commit network changes
            slaac_enable (bool, optional): Enable/disable IPv6 SLAAC
            
        Returns:
            tuple: (success, changed, message, data)
        """
        self.logger.info(f"Configuring DNS and network settings")
        try:
            resp = self.dns_workflow.configure_network(
                dns_addresses=dns_addresses,
                ipv4_address=ipv4_address,
                ipv4_gateway=ipv4_gateway,
                ipv4_subnet_mask=ipv4_subnet_mask,
                ipv6_address=ipv6_address,
                ipv6_gateway=ipv6_gateway,
                ipv6_prefix_len=ipv6_prefix_len,
                proxy_params=proxy_params,
                commit_change=commit_change,
                slaac_enable=slaac_enable
            )
            self.logger.info(f"DNS and network settings configured successfully")
            # Determine changed flag based on commit_change: staging (False) should not mark changed
            changed = True if commit_change is None else bool(commit_change)
            return (True, changed, "Successfully configured DNS and network settings", {'response': resp})
            
        except exceptions.SystemDoesNotExist as sne:
            self.logger.exception(f"System not found for DNS/network configuration: {str(sne)}")
            return (True, False, str(sne), {})
        except Exception as e:
            self.logger.exception(f"DNS/network configuration failed: {str(e)}")
            return (False, False, f"Failed to configure DNS and network settings: {e}", {})

    def get_dns_system_info(self, system_uid=None):
        """Get system information using DNS workflow.
        
        Args:
            system_uid (str, optional): System UID to get info for. If None, gets all systems.
            
        Returns:
            tuple: (success, changed, message, data)
        """
        self.logger.info(f"Getting system information via DNS workflow for UID: {system_uid}")
        try:
            resp = self.dns_workflow.get_system_info(system_uid)
            self.logger.info(f"System information retrieved successfully via DNS workflow")
            return (True, False, "Successfully retrieved system information via DNS workflow", resp)
        except exceptions.SystemDoesNotExist as sne:
            self.logger.exception(f"System not found: {str(sne)}")
            return (True, False, str(sne), {})
        except Exception as e:
            self.logger.exception(f"Failed to get system information via DNS workflow: {str(e)}")
            return (False, False, f"Failed to get system information via DNS workflow: {e}", {})

    #schedule operations
    def create_schedule(self,name,**kwargs):
        self.logger.info(f"AnsibleClient: Creating schedule '{name}'")
        try:
            resp=self.schedule_workflow.create_schedule(name,**kwargs)
            self.logger.info(f"AnsibleClient: Schedule '{name}' created successfully. Response: {resp}")
            return(True,True,f"Schedule {name} created successfully",{})
        except exceptions.ScheduleAlreadyExists as se:
            self.logger.warning(f"AnsibleClient: Schedule '{name}' already exists")
            return (True, False, str(se), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Schedule '{name}' creation failed: {e}")
            return (False, False, f"Schedule {name} creation failed | {e}", {})

    def modify_schedule(self,schedule_name,**kwargs):
        self.logger.info(f"AnsibleClient: Modifying schedule '{schedule_name}'")
        try:
            resp=self.schedule_workflow.modify_schedule(schedule_name,**kwargs)
            self.logger.info(f"AnsibleClient: Schedule '{schedule_name}' modified successfully. Response: {resp}")
            return(True,True,f"Schedule {schedule_name} modified successfully",{})
        except exceptions.ScheduleDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Schedule '{schedule_name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Schedule '{schedule_name}' modification failed: {e}")
            return (False, False, f"Schedule {schedule_name} modification failed | {e}", {})

    def delete_schedule(self,name):
        self.logger.info(f"AnsibleClient: Deleting schedule '{name}'")
        try:
            resp=self.schedule_workflow.delete_schedule(name)
            self.logger.info(f"AnsibleClient: Schedule '{name}' deleted successfully. Response: {resp}")
            return(True,True,f"Schedule {name} deleted successfully",{})
        except exceptions.ScheduleDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Schedule '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Schedule '{name}' deletion failed: {e}")
            return (False, False, f"Schedule {name} deletion failed | {e}", {})

    def suspend_schedule(self,name,**kwargs):
        self.logger.info(f"AnsibleClient: Suspending schedule '{name}'")
        try:
            resp=self.schedule_workflow.suspend_schedule(name,**kwargs)
            self.logger.info(f"AnsibleClient: Schedule '{name}' suspended successfully. Response: {resp}")
            return(True,True,f"Schedule {name} suspended successfully",{})
        except exceptions.ScheduleDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Schedule '{name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Schedule '{name}' suspension failed: {e}")
            return (False, False, f"Schedule {name} suspension failed | {e}", {})

    def resume_schedule(self,name,**kwargs):
        self.logger.info(f"AnsibleClient: Resuming schedule '{name}'")
        try:
            resp=self.schedule_workflow.resume_schedule(name,**kwargs)
            self.logger.info(f"AnsibleClient: Schedule '{name}' resumed successfully. Response: {resp}")
            return(True,True,f"Schedule {name} resumed successfully",{})
        except exceptions.ScheduleDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: Schedule '{name}' does not exist")
            return (False, False, str(dne), {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Schedule '{name}' resumption failed: {e}")
            return (False, False, f"Schedule {name} resumption failed | {e}", {}) 

    #User related workflow operations
    def get_all_users(self, **kwargs):
        """Get all users (GET /api/v3/users)."""
        self.logger.info("AnsibleClient: Getting all users")
        try:
            resp = self.user_workflow.get_all_users(**kwargs)
            self.logger.info("AnsibleClient: All users retrieved successfully")
            return (True, False, "All users retrieved successfully", {"response": resp})
        except Exception as e:
            self.logger.error(f"AnsibleClient: Failed to get all users: {e}")
            return (False, False, f"Failed to get all users | {e}", {})

    def get_user_by_name(self, name, **kwargs):
        """Get user by name."""
        self.logger.info(f"AnsibleClient: Getting user '{name}' by name")
        try:
            resp = self.user_workflow.get_user_by_name(name, **kwargs)
            self.logger.info(f"AnsibleClient: User '{name}' retrieved successfully")
            return (True, False, f"User {name} retrieved successfully", {"response": resp})
        except exceptions.UserDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: User '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.error(f"AnsibleClient: Failed to get user '{name}': {e}")
            return (False, False, f"Failed to get user {name} | {e}", {})

    def create_user(self, name, password, domain_privileges, **kwargs):
        """Create a new user account (POST /api/v3/users)."""
        self.logger.info(f"AnsibleClient: Creating user '{name}'")
        try:
            resp = self.user_workflow.create_user(name, password, domain_privileges, **kwargs)
            self.logger.info(f"AnsibleClient: User '{name}' created successfully")
            return (True, True, f"User {name} created successfully", {})
        except exceptions.UserAlreadyExists as ue:
            self.logger.warning(f"AnsibleClient: User '{name}' already exists")
            return (True, False, str(ue), {})
        except Exception as e:
            self.logger.error(f"AnsibleClient: User '{name}' creation failed: {e}")
            return (False, False, f"User {name} creation failed | {e}", {})

    def modify_user_by_name(self, name, current_password=None, new_password=None, domain_privileges=None, **kwargs):
        """Modify user by name."""
        self.logger.info(f"AnsibleClient: Modifying user '{name}' by name")
        try:
            resp = self.user_workflow.modify_user_by_name(name, current_password, new_password, domain_privileges, **kwargs)
            self.logger.info(f"AnsibleClient: User '{name}' modified successfully")
            return (True, True, f"User {name} modified successfully", {})
        except exceptions.UserDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: User '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.error(f"AnsibleClient: User '{name}' modification failed: {e}")
            return (False, False, f"User {name} modification failed | {e}", {})

    def delete_user_by_name(self, name, **kwargs):
        """Delete user by name."""
        self.logger.info(f"AnsibleClient: Deleting user '{name}' by name")
        try:
            resp = self.user_workflow.delete_user_by_name(name, **kwargs)
            self.logger.info(f"AnsibleClient: User '{name}' deleted successfully")
            return (True, True, f"User {name} deleted successfully", {})
        except exceptions.UserDoesNotExist as dne:
            self.logger.warning(f"AnsibleClient: User '{name}' does not exist")
            return (True, False, str(dne), {})
        except Exception as e:
            self.logger.error(f"AnsibleClient: User '{name}' deletion failed: {e}")
            return (False, False, f"User {name} deletion failed | {e}", {})

    # Host related workflows
    # Note: Few host operations are yet not supported in v3 so utilizing v1 implementation for time being.
    # As and when all the operations are supported in v3, will migrate to v3 implementation.
    # TODO:
    # - After changing to v3 implementation, need to move all this preprocessing utils logic and post computation
    #   to flowkit and keep the client very thin like other workflows.
    # - Currently for v1 workflows, arguments are provided directly, later need to change to kwargs format.
    def create_host(self, name, iscsiNames=None, FCWwns=None, host_domain=None, host_persona=None):
        """Idempotent create host orchestration.

        Returns (changed, failed, message, data)
        """
        self.logger.info(f"AnsibleClient: Creating host '{name}'")
        try:
            payload_params = host_utils.preprocess_create_host(name, iscsiNames, FCWwns, host_domain, host_persona)
            if self.host_workflow.host_exists(name):
                self.logger.warning(f"AnsibleClient: Host '{name}' already exists")
                return (True, False, f"Host '{name}' already exists", {})
            self.host_workflow.create_host(name, payload_params)
            self.logger.info(f"AnsibleClient: Host '{name}' created successfully")
            return (True, True, f"Created host '{name}' successfully", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Host '{name}' creation failed: {e}")
            return (False, False, f"Create host '{name}' failed | {e}", {})

    def delete_host(self, name):
        self.logger.info(f"AnsibleClient: Deleting host '{name}'")
        try:
            validate_host_params(name)
            if not self.host_workflow.host_exists(name):
                self.logger.warning(f"AnsibleClient: Host '{name}' not present")
                return (True, False, f"Host '{name}' not present", {})
            self.host_workflow.delete_host(name)
            self.logger.info(f"AnsibleClient: Host '{name}' deleted successfully")
            return (True, True, f"Deleted host '{name}' successfully", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Host '{name}' deletion failed: {e}")
            return (False, False, f"Delete host '{name}' failed | {e}", {})
            
    def modify_host(self, host_name, host_new_name, persona=None):
        self.logger.info(f"AnsibleClient: Modifying host '{host_name}'")
        try:
            payload_params = host_utils.preprocess_modify_host(host_name, host_new_name, persona)
            if not self.host_workflow.host_exists(host_name):
                self.logger.warning(f"AnsibleClient: Host '{host_name}' not present")
                return (False, False, f"Host '{host_name}' not present", {})
            self.host_workflow.modify_host(host_name, payload_params)
            self.logger.info(f"AnsibleClient: Host '{host_name}' modified successfully")
            return (True, True, f"Modified host '{host_name}' successfully", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Host '{host_name}' modification failed: {e}")
            return (False, False, f"Modify host '{host_name}' failed | {e}", {})



    def add_initiator_chap(self, host_name, chap_name, chap_secret, chap_secret_hex=False):
        self.logger.info(f"AnsibleClient: Adding initiator CHAP to host '{host_name}'")
        try:
            # Basic host name validation (avoid raising to allow custom messages for CHAP fields)
            payload = host_utils.preprocess_initiator_chap(host_name, chap_name, chap_secret, chap_secret_hex)

            if not self.host_workflow.host_exists(host_name):
                self.logger.warning(f"AnsibleClient: Host '{host_name}' not present")
                return (False, False, f"Host '{host_name}' not present", {})
            
            self.host_workflow.modify_host(host_name, payload)
            self.logger.info(f"AnsibleClient: Initiator CHAP added to host '{host_name}' successfully")
            return (True, True, f"Added initiator CHAP to host '{host_name}'", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Add initiator CHAP failed for host '{host_name}': {e}")
            return (False, False, f"Add initiator CHAP failed for host {host_name} | {e}", {})

    def remove_initiator_chap(self, host_name):
        self.logger.info(f"AnsibleClient: Removing initiator CHAP from host '{host_name}'")
        try:
            validate_host_params(name=host_name)
            if not self.host_workflow.host_exists(host_name):
                self.logger.warning(f"AnsibleClient: Host '{host_name}' not present (treat as removed)")
                return (True, False, f"Host '{host_name}' not present (treat as removed)", {})
            payload = {'chapOperation': host_utils.HOST_EDIT_REMOVE}
            self.host_workflow.modify_host(host_name, payload)
            self.logger.info(f"AnsibleClient: Initiator CHAP removed from host '{host_name}' successfully")
            return (True, True, f"Removed initiator CHAP from host '{host_name}'", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Remove initiator CHAP failed: {e}")
            return (False, False, f"Remove initiator CHAP failed | {e}", {})

    def initiator_chap_exists(self, host_name):
        self.logger.info(f"AnsibleClient: Checking if initiator CHAP exists for host '{host_name}'")
        try:
            validate_host_params(name=host_name)
            exists = self.host_workflow.initiator_chap_exists(host_name)
            self.logger.info(f"AnsibleClient: Initiator CHAP exists check for host '{host_name}': {exists}")
            return exists
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Check initiator CHAP existence for host '{host_name}' failed: {e}")
            return e
    def add_target_chap(self, host_name, chap_name, chap_secret, chap_secret_hex=False):
        self.logger.info(f"AnsibleClient: Adding target CHAP to host '{host_name}'")
        try:
            payload = host_utils.preprocess_target_chap(host_name, chap_name, chap_secret, chap_secret_hex)
            if not self.host_workflow.host_exists(host_name):
                self.logger.warning(f"AnsibleClient: Host '{host_name}' not present")
                return (True, False, f"Host '{host_name}' not present", {})
            # Must have initiator first
            if not self.host_workflow.initiator_chap_exists(host_name):
                self.logger.warning(f"AnsibleClient: Initiator CHAP must exist before adding target CHAP on host '{host_name}'")
                return (True, False, f"Initiator CHAP must exist before adding target CHAP on host '{host_name}'", {})
            self.host_workflow.modify_host(host_name, payload)
            self.logger.info(f"AnsibleClient: Target CHAP added to host '{host_name}' successfully")
            return (True, True, f"Added target CHAP to host '{host_name}'", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Adding target CHAP failed for host '{host_name}': {e}")
            return (False, False, f"Adding target CHAP failed for host {host_name}| {e}", {})

    def remove_target_chap(self, host_name):
        self.logger.info(f"AnsibleClient: Removing target CHAP from host '{host_name}'")
        try:
            validate_host_params(name=host_name)
            if not self.host_workflow.host_exists(host_name):
                self.logger.warning(f"AnsibleClient: Host '{host_name}' not present (treat as removed)")
                return (True, False, f"Host '{host_name}' not present (treat as removed)", {})
            # We cannot easily distinguish initiator vs target presence without full host record; perform unconditional remove of target only
            payload = {'chapOperation': host_utils.HOST_EDIT_REMOVE, 'chapRemoveTargetOnly': True}
            self.host_workflow.modify_host(host_name, payload)
            self.logger.info(f"AnsibleClient: Target CHAP removed from host '{host_name}' successfully")
            return (True, True, f"Removed target CHAP from host '{host_name}'", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Remove target CHAP failed: {e}")
            return (False, False, f"Remove target CHAP failed | {e}", {})
        
    def queryHost(self, iqns=None, wwns=None):
        self.logger.info(f"AnsibleClient: Querying hosts with IQNs: {iqns}, WWNs: {wwns}")
        query = host_utils.prepare_iqn_wwn_queryurl(iqns=iqns, wwns=wwns)
        result = self.host_workflow.query_hosts(query)['members']
        self.logger.info(f"AnsibleClient: Query hosts returned {len(result)} results")
        return result
        


    def _normalize_wwn(self, wwn):
        """Deprecated: Use host_utils.normalize_wwn() instead.
        
        Kept for backward compatibility if referenced elsewhere.
        """
        return host_utils.normalize_wwn(wwn)

    # _index_fc_paths/_index_iscsi_paths removed; logic centralized in HostWorkflow

    def add_fc_path_to_host(self, host_name, host_fc_wwns):
        """Add FC paths (WWNs) to a host.
        
        This method categorizes the provided WWNs based on their current ownership:
        - New WWNs (not assigned to any host) will be added
        - WWNs already assigned to the target host are skipped
        - WWNs assigned to other hosts cause the operation to fail
        
        Args:
            host_name: Name of the target host
            host_fc_wwns: List of FC WWNs to add to the host
            
        Returns:
            Tuple: (success, changed, message, data)
        """
        self.logger.info(f"AnsibleClient: Adding FC paths to host '{host_name}'")
        try:
            # Validate input parameters
            validate_host_params(name=host_name, FCWwns=host_fc_wwns)
            
            # Early return for empty WWN list
            if not host_fc_wwns:
                return (True, False, 'No FC WWNs provided', {})
            
            # Check if host exists
            if not self.host_workflow.host_exists(host_name):
                return (True, False, f"Host '{host_name}' not present", {})
            
            wwn_new = []
            wwn_same_host = []
            wwn_other_host = []

            for wwn in host_fc_wwns:
                wwn_list = [wwn]
                host_list = self.queryHost(wwns=wwn_list)
                # return (True, True, host_list,{})
                for host_obj in host_list:
                    if host_name == host_obj.get('name'):
                        wwn_same_host.append(self._normalize_wwn(wwn))
                    else:
                        wwn_other_host.append(self._normalize_wwn(wwn))

                if host_list == []:
                    wwn_new.append(self._normalize_wwn(wwn))
            
            # Handle conflicts: WWNs assigned to other hosts
            if wwn_other_host:
                return (False, False, 
                    f"FC path(s) {', '.join(wwn_other_host)} already assigned to other host", {})
            
            # Add new WWNs to the host
            if wwn_new:
                payload = {'pathOperation': host_utils.PATH_OPERATION_ADD, 'FCWWNs': list(wwn_new)}
                self.host_workflow.modify_host(host_name, payload)
                self.logger.info(f"AnsibleClient: FC path(s) {', '.join(wwn_new)} added to host '{host_name}' successfully")
                return (True, True, 
                    f"Added FC path(s) {', '.join(wwn_new)} to host '{host_name}'", {})
            
            # All WWNs already assigned to this host - no changes needed
            if wwn_same_host:
                self.logger.warning(f"AnsibleClient: FC path(s) {', '.join(wwn_same_host)} already assigned to host '{host_name}'")
                return (True, False, 
                    f"FC path(s) {', '.join(wwn_same_host)} already assigned to this host", {})
            
            # Fallback case (should not happen with current logic)
            self.logger.warning(f"AnsibleClient: No FC path changes applied for host '{host_name}'")
            return (True, False, 'No changes applied', {})
            
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Add FC paths to host '{host_name}' failed: {e}")
            return (False, False, f"Add FC paths failed | {e}", {})

    def remove_fc_path_from_host(self, host_name, host_fc_wwns, force_path_removal=False):
        self.logger.info(f"AnsibleClient: Removing FC paths from host '{host_name}'")
        try:
            validate_host_params(name=host_name, FCWwns=host_fc_wwns, force_path_removal=force_path_removal)
            if not host_fc_wwns:
                return (True, False, 'No FC WWNs provided', {})
            if not self.host_workflow.host_exists(host_name):
                return (True, False, f"Host '{host_name}' not present (treat as removed)", {})
            wwn_new = []
            wwn_same_host = []
            wwn_other_host = []

            for wwn in host_fc_wwns:
                wwn_list = [wwn]
                host_list = self.queryHost(wwns=wwn_list)
                # return (True, True, host_list,{})
                for host_obj in host_list:
                    if host_name == host_obj.get('name'):
                        wwn_same_host.append(self._normalize_wwn(wwn))
                    else:
                        wwn_other_host.append(self._normalize_wwn(wwn))

                if host_list == []:
                    wwn_new.append(self._normalize_wwn(wwn))
            if wwn_other_host:
                return (False, False, f"FC path(s) {', '.join(wwn_other_host)} assigned to other host", {})
            if wwn_same_host:
                payload = {'pathOperation': host_utils.PATH_OPERATION_REMOVE, 'FCWWNs': list(wwn_same_host), 'forcePathRemoval': force_path_removal}
                self.host_workflow.modify_host(host_name, payload)
                self.logger.info(f"AnsibleClient: FC path(s) {', '.join(wwn_same_host)} removed from host '{host_name}' successfully")
                return (True, True, f"Removed FC path(s) {', '.join(wwn_same_host)} from host '{host_name}'", {})
            if wwn_new:
                self.logger.warning(f"AnsibleClient: FC path(s) {', '.join(wwn_new)} not present/already removed from host '{host_name}'")
                return (True, False, f"Seems FC path(s) {', '.join(wwn_new)} not present/already removed on system", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Remove FC paths from host '{host_name}' failed: {e}")
            return (False, False, f"Remove FC paths failed | {e}", {})

    # _index_iscsi_paths removed (centralized in HostWorkflow)

    def add_iscsi_path_to_host(self, host_name, host_iscsi_names):
        self.logger.info(f"AnsibleClient: Adding iSCSI paths to host '{host_name}'")
        try:
            validate_host_params(name=host_name, iscsiNames=host_iscsi_names)
            if not host_iscsi_names:
                return (True, False, 'No iSCSI names provided', {})
            if not self.host_workflow.host_exists(host_name):
                return (False, False, f"Host '{host_name}' not present", {})
            iqn_new = []
            iqn_same_host = []
            iqn_other_host = []

            for iqn in host_iscsi_names:
                iscsi_name = [iqn]
                host_list = self.queryHost(iqns=iscsi_name)
                for host_obj in host_list:
                    if host_name == host_obj.get('name'):
                        iqn_same_host.append(iqn)
                    else:
                        iqn_other_host.append(iqn)

                if host_list == []:
                    iqn_new.append(iqn)

            if iqn_other_host:
                return (False, False, f"iSCSI name(s) {', '.join(iqn_other_host)} already assigned to other host", {})
            if iqn_new:
                payload = {'pathOperation': host_utils.PATH_OPERATION_ADD, 'iSCSINames': list(iqn_new)}
                self.host_workflow.modify_host(host_name, payload)
                self.logger.info(f"AnsibleClient: iSCSI name(s) {', '.join(iqn_new)} added to host '{host_name}' successfully")
                return (True, True, f"Added iSCSI name(s) {', '.join(iqn_new)} to host '{host_name}'", {})
            if iqn_same_host:
                self.logger.warning(f"AnsibleClient: iSCSI name(s) {', '.join(iqn_same_host)} already assigned to host '{host_name}'")
                return (True, False, f"iSCSI name(s) {', '.join(iqn_same_host)} already assigned to this host", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Add iSCSI paths to host '{host_name}' failed: {e}")
            return (False, False, f"Add iSCSI paths failed | {e}", {})

    def remove_iscsi_path_from_host(self, host_name, host_iscsi_names, force_path_removal=False):
        self.logger.info(f"AnsibleClient: Removing iSCSI paths from host '{host_name}'")
        try:
            validate_host_params(name=host_name, iscsiNames=host_iscsi_names, force_path_removal=force_path_removal)
            if not host_iscsi_names:
                return (True, False, 'No iSCSI names provided', {})
            if not self.host_workflow.host_exists(host_name):
                return (True, False, f"Host '{host_name}' not present (treat as removed)", {})
            iqn_new = []
            iqn_same_host = []
            iqn_other_host = []

            for iqn in host_iscsi_names:
                iscsi_name = [iqn]
                host_list = self.queryHost(iqns=iscsi_name)
                for host_obj in host_list:
                    if host_name == host_obj.get('name'):
                        iqn_same_host.append(iqn)
                    else:
                        iqn_other_host.append(iqn)

                if host_list == []:
                    iqn_new.append(iqn)

            if iqn_other_host:
                return (False, False, f"iSCSI name(s) {', '.join(iqn_other_host)} assigned to other host", {})
            if iqn_same_host:
                payload = {'pathOperation': host_utils.PATH_OPERATION_REMOVE, 'iSCSINames': list(iqn_same_host), 'forcePathRemoval': force_path_removal}
                self.host_workflow.modify_host(host_name, payload)
                self.logger.info(f"AnsibleClient: iSCSI name(s) {', '.join(iqn_same_host)} removed from host '{host_name}' successfully")
                return (True, True, f"Removed iSCSI name(s) {', '.join(iqn_same_host)} from host '{host_name}'", {})
            if iqn_new:
                self.logger.warning(f"AnsibleClient: iSCSI name(s) {', '.join(iqn_new)} already removed/not present on host '{host_name}'")
                return (True, False, f"iSCSI name(s) {', '.join(iqn_new)} already removed/not present on system", {})        
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Remove iSCSI paths from host '{host_name}' failed: {e}")
            return (False, False, f"Remove iSCSI paths failed | {e}", {})
        
    # VLUN Related workflows
    # Note: Few VLUN operations are yet not supported in v3 so utilizing v1 implementation for time being.
    # As and when all the operations are supported in v3, will migrate to v3 implementation.
    # TODO:
    # - After changing to v3 implementation, need to move all this preprocessing utils logic and post computation
    #   to flowkit and keep the client very thin like other workflows.
    # - Currently for v1 workflows, arguments are provided directly, later need to change to kwargs format.
    def export_volume_to_host(
        self, volume_name, host_name, lun=None, node_val=None, slot=None, card_port=None, autolun=False
    ):
        """
        export_volume_to_host
        """
        self.logger.info(f"AnsibleClient: Exporting volume '{volume_name}' to host '{host_name}'")
        try:
            if not validate_params(volumeName=volume_name, hostname=host_name, lun=lun, autoLun=autolun):
                self.logger.warning(f"AnsibleClient: Invalid params for export volume '{volume_name}' to host '{host_name}'")
                return (False, False, "Given Params are not valid", {})
            payload = build_payload(volume_name, host_name, lun, autolun, node_val, slot, card_port)
            if not payload:
                return (False, False, "Payload must not be empty", {})
            # Check if VLUN already exists
            if not autolun:
                if self.vlun_workflow.vlun_exists(volume_name, lun, host_name, payload.get("portPos")):
                    self.logger.warning(f"AnsibleClient: VLUN for volume '{volume_name}' to host '{host_name}' already present")
                    return (True, False, "VLUN already present", {})
            self.vlun_workflow.export_volume_to_host(payload)
            self.logger.info(f"AnsibleClient: Export volume '{volume_name}' to host '{host_name}' completed successfully")
            return (True, True, "Export Volume To Host Completed Successfully.", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Export volume '{volume_name}' to host '{host_name}' failed: {e}")
            return (False, False, "Export Volume To Host Failed  | %s" % e, {})

    def unexport_volume_from_host(
        self, volume_name, host_name, lun, node_val=None, slot=None, card_port=None, autolun=False
    ):
        """
        unexport_volume_from_host
        """
        self.logger.info(f"AnsibleClient: Unexporting volume '{volume_name}' from host '{host_name}'")
        try:
            if not validate_params(volumeName=volume_name, hostname=host_name, lun=lun):
                self.logger.warning(f"AnsibleClient: Invalid params for unexport volume '{volume_name}' from host '{host_name}'")
                return (False, False, "Given Params are not valid", {})
            payload = build_payload(volume_name, host_name, lun, autolun, node_val, slot, card_port)
            # Find the VLUN to delete
            port_pos = payload.get("portPos")
            vluns = self.vlun_workflow.list_vluns()
            vlun_to_delete = find_vlun(vluns, volume_name, host_name, lun, port_pos)
            if vlun_to_delete:
                vlun_id = f"{vlun_to_delete['volumeName']},{vlun_to_delete['lun']},{vlun_to_delete['hostname']}"
                self.vlun_workflow.unexport_volume_from_host(vlun_id)
                self.logger.info(f"AnsibleClient: Unexport volume '{volume_name}' from host '{host_name}' completed successfully")
                return (True, True, "Unexport Volume From Host Completed Successfully.", {})
            else:
                self.logger.warning(f"AnsibleClient: VLUN for volume '{volume_name}' to host '{host_name}' does not exist")
                return (False, False, "VLUN does not exist", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Unexport volume '{volume_name}' from host '{host_name}' failed: {e}")
            return (False, False, "Unexport Volume From Host Failed | %s" % e, {})

    def export_volume_to_hostset(
        self, volume_name, host_set_name, lun=None, node_val=None, slot=None, card_port=None, autolun=False
    ):
        """
        export_volume_to_hostset
        """
        self.logger.info(f"AnsibleClient: Exporting volume '{volume_name}' to hostset '{host_set_name}'")
        try:
            if not validate_params(volumeName=volume_name, hostname=host_set_name, lun=lun, autoLun=autolun):
                self.logger.warning(f"AnsibleClient: Invalid params for export volume '{volume_name}' to hostset '{host_set_name}'")
                return (False, False, "Given Params are not valid", {})
            payload = build_payload(volume_name, host_set_name, lun, autolun, node_val, slot, card_port)
            if not payload:
                return (False, False, "Payload must not be empty", {})
            # Check if VLUN already exists
            if not autolun:
                if self.vlun_workflow.vlun_exists(volume_name, lun, host_set_name, payload.get("portPos")):
                    self.logger.warning(f"AnsibleClient: VLUN for volume '{volume_name}' to hostset '{host_set_name}' already present")
                    return (True, False, "VLUN already present", {})
            self.vlun_workflow.export_volume_to_hostset(payload)
            self.logger.info(f"AnsibleClient: Export volume '{volume_name}' to hostset '{host_set_name}' completed successfully")
            return (True, True, "Export Volume To Hostset Completed Successfully.", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Export volume '{volume_name}' to hostset '{host_set_name}' failed: {e}")
            return (False, False, "Export Volume To Hostset Failed | %s" % e, {})

    def unexport_volume_from_hostset(
        self, volume_name, host_set_name, lun, node_val=None, slot=None, card_port=None, autolun=False
    ):
        """
        unexport_volume_from_hostset
        """
        self.logger.info(f"AnsibleClient: Unexporting volume '{volume_name}' from hostset '{host_set_name}'")
        try:
            if not validate_params(volumeName=volume_name, hostname=host_set_name, lun=lun):
                self.logger.warning(f"AnsibleClient: Invalid params for unexport volume '{volume_name}' from hostset '{host_set_name}'")
                return (False, False, "Given Params are not valid", {})
            payload = build_payload(volume_name, host_set_name, lun, autolun, node_val, slot, card_port)
            port_pos = payload.get("portPos")
            # Find the VLUN to delete
            vluns = self.vlun_workflow.list_vluns()
            vlun_to_delete = find_vlun(vluns, volume_name, host_set_name, lun, port_pos)
            if vlun_to_delete:
                vlun_id = f"{vlun_to_delete['volumeName']},{vlun_to_delete['lun']},{vlun_to_delete['hostname']}"
                self.vlun_workflow.unexport_volume_from_hostset(vlun_id)
                self.logger.info(f"AnsibleClient: Unexport volume '{volume_name}' from hostset '{host_set_name}' completed successfully")
                return (True, True, "Unexport Volume From Hostset Completed Successfully.", {})
            else:
                self.logger.warning(f"AnsibleClient: VLUN for volume '{volume_name}' to hostset '{host_set_name}' does not exist")
                return (False, False, "VLUN does not exist", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Unexport volume '{volume_name}' from hostset '{host_set_name}' failed: {e}")
            return (False, False, "Unexport Volume From Hostset Failed | %s" % e, {})

    def export_volumeset_to_host(
        self, volume_set_name, host_name, lun=None, node_val=None, slot=None, card_port=None, autolun=False
    ):
        """
        export_volumeset_to_host
        """
        self.logger.info(f"AnsibleClient: Exporting volumeset '{volume_set_name}' to host '{host_name}'")
        try:
            if not validate_params(volumeName=volume_set_name, hostname=host_name, lun=lun, autoLun=autolun):
                self.logger.warning(f"AnsibleClient: Invalid params for export volumeset '{volume_set_name}' to host '{host_name}'")
                return (False, False, "Given Params are not valid", {})
            payload = build_payload(volume_set_name, host_name, lun, autolun, node_val, slot, card_port)
            if not payload:
                return (False, False, "Payload must not be empty", {})
            # Check if VLUN already exists
            if not autolun:
                if self.vlun_workflow.vlun_exists(volume_set_name, lun, host_name, payload.get("portPos")):
                    self.logger.warning(f"AnsibleClient: VLUN for volumeset '{volume_set_name}' to host '{host_name}' already present")
                    return (True, False, "VLUN already present", {})
            self.vlun_workflow.export_volumeset_to_host(payload)
            self.logger.info(f"AnsibleClient: Export volumeset '{volume_set_name}' to host '{host_name}' completed successfully")
            return (True, True, "Export Volumeset To Host Completed Successfully.", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Export volumeset '{volume_set_name}' to host '{host_name}' failed: {e}")
            return (False, False, "Export Volumeset To Host Failed | %s" % e, {})

    def unexport_volumeset_from_host(
        self, volume_set_name, host_name, lun, node_val=None, slot=None, card_port=None, autolun=False
    ):
        """
        unexport_volumeset_from_host
        """
        self.logger.info(f"AnsibleClient: Unexporting volumeset '{volume_set_name}' from host '{host_name}'")
        try:
            if not validate_params(volumeName=volume_set_name, hostname=host_name, lun=lun):
                self.logger.warning(f"AnsibleClient: Invalid params for unexport volumeset '{volume_set_name}' from host '{host_name}'")
                return (False, False, "Given Params are not valid", {})
            payload = build_payload(volume_set_name, host_name, lun, autolun, node_val, slot, card_port)
            port_pos = payload.get("portPos")
            # Find and delete all unique matching VLUNs using find_vlun
            vluns = self.vlun_workflow.list_vluns()
            vvsets = self.vlun_workflow.get_vvsets(volume_set_name=volume_set_name.removeprefix("set:"))
            set_members = vvsets.get("setmembers")
            seen = set()
            responses = []
            for member in set_members:
                vlun = find_vlun(vluns, member, host_name, lun, port_pos)
                if vlun:
                    key = (vlun["lun"], vlun["volumeName"], vlun["hostname"])
                    if key not in seen:
                        seen.add(key)
                        vlun_id = f"{vlun['volumeName']},{vlun['lun']},{vlun['hostname']}"
                        result = self.vlun_workflow.unexport_volumeset_from_host(vlun_id)
                        responses.append(result)
            if responses:
                self.logger.info(f"AnsibleClient: Unexport volumeset '{volume_set_name}' from host '{host_name}' completed successfully")
                return (True, True, "Unexport Volumeset From Host Completed Successfully.", {})
            else:
                self.logger.warning(f"AnsibleClient: No VLUNs found to delete for volumeset '{volume_set_name}' from host '{host_name}'")
                return (False, False, "No VLUNs found to delete", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Unexport volumeset '{volume_set_name}' from host '{host_name}' failed: {e}")
            return (False, False, "Unexport Volumeset From Host Failed | %s" % e, {})

    def export_volumeset_to_hostset(
        self, volume_set_name, host_set_name, lun=None, node_val=None, slot=None, card_port=None, autolun=False
    ):
        """
        export_volumeset_to_hostset
        """
        self.logger.info(f"AnsibleClient: Exporting volumeset '{volume_set_name}' to hostset '{host_set_name}'")
        try:
            if not validate_params(volumeName=volume_set_name, hostname=host_set_name, lun=lun, autoLun=autolun):
                self.logger.warning(f"AnsibleClient: Invalid params for export volumeset '{volume_set_name}' to hostset '{host_set_name}'")
                return (False, False, "Given Params are not valid", {})
            payload = build_payload(volume_set_name, host_set_name, lun, autolun, node_val, slot, card_port)
            if not payload:
                return (False, False, "Payload must not be empty", {})
            # Check if VLUN already exists
            if not autolun:
                if self.vlun_workflow.vlun_exists(volume_set_name, lun, host_set_name, payload.get("portPos")):
                    self.logger.warning(f"AnsibleClient: VLUN for volumeset '{volume_set_name}' to hostset '{host_set_name}' already present")
                    return (True, False, "VLUN already present", {})
            self.vlun_workflow.export_volumeset_to_hostset(payload)
            self.logger.info(f"AnsibleClient: Export volumeset '{volume_set_name}' to hostset '{host_set_name}' completed successfully")
            return (True, True, "Export Volumeset To Hostset Completed Successfully.", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Export volumeset '{volume_set_name}' to hostset '{host_set_name}' failed: {e}")
            return (False, False, "Export Volumeset To Hostset Failed | %s" % e, {})

    def unexport_volumeset_from_hostset(
        self, volume_set_name, host_set_name, lun, node_val=None, slot=None, card_port=None, autolun=False
    ):
        """
        unexport_volumeset_from_hostset
        """
        self.logger.info(f"AnsibleClient: Unexporting volumeset '{volume_set_name}' from hostset '{host_set_name}'")
        try:
            if not validate_params(volumeName=volume_set_name, hostname=host_set_name, lun=lun):
                self.logger.warning(f"AnsibleClient: Invalid params for unexport volumeset '{volume_set_name}' from hostset '{host_set_name}'")
                return (False, False, "Given Params are not valid", {})
            payload = build_payload(volume_set_name, host_set_name, lun, autolun, node_val, slot, card_port)
            port_pos = payload.get("portPos")
            vluns = self.vlun_workflow.list_vluns()
            vvsets = self.vlun_workflow.get_vvsets(volume_set_name=volume_set_name.removeprefix("set:"))
            set_members = vvsets.get("setmembers")
            seen = set()
            responses = []
            for member in set_members:
                vlun = find_vlun(vluns, member, host_set_name, lun, port_pos)
                if vlun:
                    key = (vlun["lun"], vlun["volumeName"], vlun["hostname"])
                    if key not in seen:
                        seen.add(key)
                        vlun_id = f"{vlun['volumeName']},{vlun['lun']},{vlun['hostname']}"
                        result = self.vlun_workflow.unexport_volumeset_from_hostset(vlun_id)
                        responses.append(result)
            if responses:
                self.logger.info(f"AnsibleClient: Unexport volumeset '{volume_set_name}' from hostset '{host_set_name}' completed successfully")
                return (True, True, "Unexport Volumeset From Hostset Completed Successfully.", {})
            else:
                self.logger.warning(f"AnsibleClient: No VLUNs found to delete for volumeset '{volume_set_name}' from hostset '{host_set_name}'")
                return (False, False, "No VLUNs found to delete", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Unexport volumeset '{volume_set_name}' from hostset '{host_set_name}' failed: {e}")
            return (False, False, "Unexport Volumeset From Hostset Failed | %s" % e, {})

    # Remote Copy Group related workflow operations
    # Note: remote copy group operations are not yet supported publicly in v3 so utilizing v1 implementation for time being.
    # As and when all the operations are supported in v3, will migrate to v3 implementation.
    # TODO:
    # - After changing to v3 implementation, need to move all this preprocessing utils logic and post computation
    #   to flowkit and keep the client very thin like other workflows.
    # - Currently for v1 workflows, arguments are provided directly, later need to change to kwargs format.
    def create_remote_copy_group(self, remote_copy_group_name, domain, remote_copy_targets, local_user_cpg, local_snap_cpg):
        """Orchestrate remote copy group creation: validate, normalize, check source/target, existence, and create.
        
        Returns a tuple (changed, failed, message, data)
        """
        self.logger.info(f"AnsibleClient: Creating remote copy group '{remote_copy_group_name}'")
        try:
            # Validates and Normalize the rcopytargets info
            remote_copy_targets, target_names_list, payload_params = remote_copy_utils.preprocess_create_remote_copy_group(
                remote_copy_group_name, domain, remote_copy_targets, local_user_cpg, local_snap_cpg)
            
            source_name = self.system_workflow.get_storage_system_info()['name']
            if source_name in target_names_list:
                self.logger.warning(f"AnsibleClient: Source and target cannot be same for remote copy group '{remote_copy_group_name}'")
                return (False, False, f"Source and target cannot be same. Source and target both are {source_name}", {})
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                result = self.remote_copy_workflow.create_remote_copy_group(remote_copy_group_name, remote_copy_targets, payload_params)
                self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' created successfully")
                return (True, True, f"Created Remote Copy Group {remote_copy_group_name} successfully.", result)
            else:
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' already present")
                return (True, False, "Remote Copy Group already present", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' creation failed: {e}")
            return (False, False, f"Remote Copy Group creation failed | {e}", {})

    def delete_remote_copy_group(self, remote_copy_group_name, keep_snap=False):
        """Delete remote copy group orchestration."""
        self.logger.info(f"AnsibleClient: Deleting remote copy group '{remote_copy_group_name}'")
        try:
            remote_copy_utils.preprocess_delete_remote_copy_group(remote_copy_group_name)
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' is not present")
                return (True, False, f"Remote Copy Group '{remote_copy_group_name}' is not present", {})
            self.remote_copy_workflow.delete_remote_copy_group(remote_copy_group_name, keep_snap=keep_snap)
            self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' deleted successfully")
            return (True, True, f"Deleted Remote Copy Group {remote_copy_group_name} successfully.", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' deletion failed: {e}")
            return (False, False, f"Remote Copy Group deletion failed | {e}", {})

    def modify_remote_copy_group(self, remote_copy_group_name, local_user_cpg, local_snap_cpg, modify_targets, unset_user_cpg=False, unset_snap_cpg=False):
        """Modify remote copy group orchestration."""
        self.logger.info(f"AnsibleClient: Modifying remote copy group '{remote_copy_group_name}'")
        try:
            payload, target_names = remote_copy_utils.preprocess_modify_remote_copy_group(
                remote_copy_group_name,
                modify_targets=modify_targets,
                local_user_cpg=local_user_cpg,
                local_snap_cpg=local_snap_cpg,
                unset_user_cpg=unset_user_cpg,
                unset_snap_cpg=unset_snap_cpg)
            source_name = self.system_workflow.get_storage_system_info()['name']
            if source_name in target_names:
                self.logger.warning(f"AnsibleClient: Source and target cannot be same for remote copy group '{remote_copy_group_name}'")
                return (False, False, f"Source and target cannot be same. Source and target both are {source_name}", {})
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' not present")
                return (False, False, f"Remote Copy Group '{remote_copy_group_name}' not present", {})
            
            self.remote_copy_workflow.modify_remote_copy_group(remote_copy_group_name, payload)
            self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' modified successfully")
            return (True, True, f"Modified Remote Copy Group {remote_copy_group_name} successfully.", payload)
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' modification failed: {e}")
            return (False, False, f"Remote Copy Group modify failed | {e}", {})

    def remote_copy_group_status(self, remote_copy_group_name):
        """Determines whether all volumes syncStatus is synced or not
        when remote copy group status is started. If all volumes
        syncStatus is 'synced' then it will return true else false
        :param remote_copy_group_name - Remote copy group name
        :type remote_copy_group_name: str
        :return: True: If remote copy group is started and all
                      volume syncStatus is 'synced' i.e. 3
                False: If remote copy group is started and some
                      volume status is not 'synced'.
        """
        self.logger.info(f"AnsibleClient: Checking sync status for remote copy group '{remote_copy_group_name}'")
        try:
            validate_remote_copy_group_params(remote_copy_group_name)
            resp = self.remote_copy_workflow.get_remote_copy_group(remote_copy_group_name)
            for target in resp['targets']:
                if target['state'] != 3:
                    self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' target not synced (state: {target['state']})")
                    return False
            for volume in resp['volumes']:
                for each_target_volume in volume['remoteVolumes']:
                    if each_target_volume['syncStatus'] != 3:
                        self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' volume not synced (syncStatus: {each_target_volume['syncStatus']})")
                        return False
            self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' all volumes synced")
            return True
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Check sync status for remote copy group '{remote_copy_group_name}' failed: {e}")
            raise e

    def add_volume_to_remote_copy_group(self, remote_copy_group_name, volume_name, admit_volume_targets, snapshot_name=None, volume_auto_creation=False, skip_initial_sync=False, different_secondary_wwn=False):
        """Orchestrate add volume: preprocess (validation inside utils) then workflow REST call."""
        self.logger.info(f"AnsibleClient: Adding volume '{volume_name}' to remote copy group '{remote_copy_group_name}'")
        try:
            # Preprocess & validate first
            admit_volume_targets, target_names_list, payload_params = remote_copy_utils.preprocess_add_volume_to_remote_copy_group(
                remote_copy_group_name,
                volume_name,
                admit_volume_targets,
                snapshot_name=snapshot_name,
                volume_auto_creation=volume_auto_creation,
                skip_initial_sync=skip_initial_sync,
                different_secondary_wwn=different_secondary_wwn
            )
            source_name = self.system_workflow.get_storage_system_info()['name']
            if source_name in target_names_list:
                self.logger.warning(f"AnsibleClient: Source and target cannot be same for volume '{volume_name}'")
                return (False, False, f"Source and target cannot be same. Source and target both are {source_name}", {})
            # Existence check after successful preprocessing
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' not present")
                return (False, False, f"Remote Copy Group '{remote_copy_group_name}' not present", {})    
            if self.remote_copy_group_volume_exists(remote_copy_group_name, volume_name):
                self.logger.warning(f"AnsibleClient: Volume '{volume_name}' already part of remote copy group '{remote_copy_group_name}'")
                return (True, False, f"Volume '{volume_name}' already part of Remote Copy Group '{remote_copy_group_name}'", {})
            result = self.remote_copy_workflow.add_volume_to_remote_copy_group(remote_copy_group_name, volume_name, admit_volume_targets, payload_params)
            self.logger.info(f"AnsibleClient: Volume '{volume_name}' added to remote copy group '{remote_copy_group_name}' successfully")
            return (True, True, f"Added volume '{volume_name}' to Remote Copy Group '{remote_copy_group_name}' successfully.", result)
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Add volume '{volume_name}' to remote copy group '{remote_copy_group_name}' failed: {e}")
            return (False, False, f"Add volume to Remote Copy Group failed | {e}", {})

    def remote_copy_group_volume_exists(self, remote_copy_group_name, volume_name):
        """Check if volume exists in remote copy group."""
        self.logger.info(f"AnsibleClient: Checking if volume '{volume_name}' exists in remote copy group '{remote_copy_group_name}'")
        try:
            self.remote_copy_workflow.get_remote_copy_group_volume_info(remote_copy_group_name, volume_name)
            self.logger.info(f"AnsibleClient: Volume '{volume_name}' exists in remote copy group '{remote_copy_group_name}'")
            return True
        except exceptions_v1.HTTPNotFound:
            self.logger.info(f"AnsibleClient: Volume '{volume_name}' does not exist in remote copy group '{remote_copy_group_name}'")
            return False
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Check volume existence in remote copy group failed: {e}")
            raise e

    def remove_volume_from_remote_copy_group(self, remote_copy_group_name, volume_name, keep_snap=False, remove_secondary_volume=False):
        """Orchestrate remove volume: preprocess (validation inside utils) then workflow REST call."""
        self.logger.info(f"AnsibleClient: Removing volume '{volume_name}' from remote copy group '{remote_copy_group_name}'")
        try:
            # Preprocess & validate first
            if volume_name is None:
                self.logger.warning(f"AnsibleClient: Volume name cannot be null for remove operation")
                return (False, False, "Volume name cannot be null", {}) 
            remote_copy_utils.preprocess_remove_volume_from_remote_copy_group(
                remote_copy_group_name,
                volume_name,
                keep_snap=keep_snap,
                remove_secondary_volume=remove_secondary_volume
            )
            # Existence check after successful preprocessing
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' not present")
                return (False, False, f"Remote Copy Group '{remote_copy_group_name}' not present", {})
            if not self.remote_copy_group_volume_exists(remote_copy_group_name, volume_name):
                self.logger.warning(f"AnsibleClient: Volume '{volume_name}' not part of remote copy group '{remote_copy_group_name}'")
                return (True, False, f"Volume '{volume_name}' not part of Remote Copy Group '{remote_copy_group_name}'", {})
            option = None
            if keep_snap:
                option = 'keepSnap'
            if remove_secondary_volume:
                option = 'removeSecondaryVolume'
            result = self.remote_copy_workflow.remove_volume_from_remote_copy_group(remote_copy_group_name, volume_name, option)
            self.logger.info(f"AnsibleClient: Volume '{volume_name}' removed from remote copy group '{remote_copy_group_name}' successfully")
            return (True, True, f"Removed volume '{volume_name}' from Remote Copy Group '{remote_copy_group_name}' successfully.", result)
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Remove volume '{volume_name}' from remote copy group '{remote_copy_group_name}' failed: {e}")
            return (False, False, f"Remove volume from Remote Copy Group failed | {e}", {})

    def start_remote_copy_group(self, remote_copy_group_name, skip_initial_sync=False, target_name=None, starting_snapshots=None):
        """Orchestrate start remote copy group operation."""
        self.logger.info(f"AnsibleClient: Starting remote copy group '{remote_copy_group_name}'")
        try:
            payload = remote_copy_utils.preprocess_start_remote_copy_group(
                remote_copy_group_name,
                skip_initial_sync=skip_initial_sync,
                target_name=target_name,
                starting_snapshots=starting_snapshots
            )
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' not present")
                return (False, False, f"Remote Copy Group '{remote_copy_group_name}' not present", {})
            # Check already started -> we need a status call; reuse get_remote_copy_group
            group = self.remote_copy_workflow.get_remote_copy_group(remote_copy_group_name)
            # Determine started: all targets state ==3
            if all(target.get('state') == remote_copy_utils.RC_START_STATE for target in group.get('targets', [])):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' is already started")
                return (True, False, f"Remote Copy Group '{remote_copy_group_name}' is already started", {})
            result = self.remote_copy_workflow.start_remote_copy_group(remote_copy_group_name, payload)
            self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' started successfully")
            return (True, True, f"Remote Copy Group '{remote_copy_group_name}' started successfully.", result)
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Start remote copy group '{remote_copy_group_name}' failed: {e}")
            return (False, False, f"Start Remote Copy Group failed | {e}", {})

    def stop_remote_copy_group(self, remote_copy_group_name, no_snapshot=False, target_name=None):
        """Orchestrate stop remote copy group operation."""
        self.logger.info(f"AnsibleClient: Stopping remote copy group '{remote_copy_group_name}'")
        try:
            payload = remote_copy_utils.preprocess_stop_remote_copy_group(
                remote_copy_group_name,
                no_snapshot=no_snapshot,
                target_name=target_name
            )
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' not present")
                return (False, False, f"Remote Copy Group '{remote_copy_group_name}' not present", {})
            group = self.remote_copy_workflow.get_remote_copy_group(remote_copy_group_name)
            # Determine stopped: all targets state ==5
            if all(target.get('state') == remote_copy_utils.RC_STOP_STATE for target in group.get('targets', [])):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' is already stopped")
                return (True, False, f"Remote Copy Group '{remote_copy_group_name}' is already stopped", {})
            result = self.remote_copy_workflow.stop_remote_copy_group(remote_copy_group_name, payload)
            self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' stopped successfully")
            return (True, True, f"Remote Copy Group '{remote_copy_group_name}' stopped successfully.", result)
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Stop remote copy group '{remote_copy_group_name}' failed: {e}")
            return (False, False, f"Stop Remote Copy Group failed | {e}", {})

    def synchronize_remote_copy_group(self, remote_copy_group_name, no_resync_snapshot=False, target_name=None, full_sync=False):
        """Orchestrate synchronize remote copy group operation."""
        self.logger.info(f"AnsibleClient: Synchronizing remote copy group '{remote_copy_group_name}'")
        try:
            payload = remote_copy_utils.preprocess_synchronize_remote_copy_group(
                remote_copy_group_name,
                no_resync_snapshot=no_resync_snapshot,
                target_name=target_name,
                full_sync=full_sync
            )
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' not present")
                return (False, False, f"Remote Copy Group '{remote_copy_group_name}' not present", {})
            # No strict idempotency check (operation triggers sync task); we could check tasks but skip for now
            result = self.remote_copy_workflow.synchronize_remote_copy_group(remote_copy_group_name, payload)
            self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' synchronization started successfully")
            return (True, True, f"Remote Copy Group '{remote_copy_group_name}' synchronization started successfully.", result)
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Synchronize remote copy group '{remote_copy_group_name}' failed: {e}")
            return (False, False, f"Synchronize Remote Copy Group failed | {e}", {})

    def admit_remote_copy_links(self, target_name, source_port, target_port_wwn_or_ip):
        """Orchestrate admit remote copy links (validation + existence checks)."""
        self.logger.info(f"AnsibleClient: Admitting remote copy link {source_port}:{target_port_wwn_or_ip} for target '{target_name}'")
        try:
            # Reuse preprocessing
            remote_copy_utils.preprocess_remote_copy_links(
                target_name, source_port, target_port_wwn_or_ip)
            # Check source != target
            source_name = self.system_workflow.get_storage_system_info()['name']
            if target_name == source_name:
                self.logger.warning(f"AnsibleClient: Source and target cannot be same for remote copy link")
                return (False, False, f"Source and target cannot be same. Source and target both are {source_name}", {})
            # We do not have a link existence checker in new layer; proceed with admit
            if self.rcopy_link_exists(target_name, source_port, target_port_wwn_or_ip):
                self.logger.warning(f"AnsibleClient: Remote copy link {source_port}:{target_port_wwn_or_ip} already exists")
                return (True, False, f"Admit Remote copy link {source_port}:{target_port_wwn_or_ip} already exists", {})
            source_target_port_pair = source_port + ':' + target_port_wwn_or_ip
            resp = self.remote_copy_workflow.admit_remote_copy_links(target_name, source_target_port_pair)
            if resp != []:
                raise exceptions_v1.SSHException(f'Error admitting remote copy link: {resp}')
            self.logger.info(f"AnsibleClient: Remote copy link {source_port}:{target_port_wwn_or_ip} admitted successfully")
            return (True, True, f"Admit remote copy link {source_port}:{target_port_wwn_or_ip} successful.", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Admit remote copy link {source_port}:{target_port_wwn_or_ip} failed: {e}")
            return (False, False, f"Admit remote copy link failed | {e}", {})

    def dismiss_remote_copy_links(self, target_name, source_port, target_port_wwn_or_ip):
        """Orchestrate dismiss remote copy links."""
        self.logger.info(f"AnsibleClient: Dismissing remote copy link {source_port}:{target_port_wwn_or_ip} for target '{target_name}'")
        try:
            remote_copy_utils.preprocess_remote_copy_links(target_name, source_port, target_port_wwn_or_ip)
            source_name = self.system_workflow.get_storage_system_info()['name']
            if target_name == source_name:
                self.logger.warning(f"AnsibleClient: Source and target cannot be same for remote copy link")
                return (False, False, f"Source and target cannot be same. Source and target both are {source_name}", {})
            if not self.rcopy_link_exists(target_name, source_port, target_port_wwn_or_ip):
                self.logger.warning(f"AnsibleClient: Remote copy link {source_port}:{target_port_wwn_or_ip} does not exist")
                return (True, False, f"Remote copy link {source_port}:{target_port_wwn_or_ip} does not exist", {})
            source_target_port_pair = source_port + ':' + target_port_wwn_or_ip
            resp = self.remote_copy_workflow.dismiss_remote_copy_links(target_name, source_target_port_pair)
            if resp != []:
                raise exceptions_v1.SSHException(f'Error dismissing remote copy link: {resp}')
            self.logger.info(f"AnsibleClient: Remote copy link {source_port}:{target_port_wwn_or_ip} dismissed successfully")
            return (True, True, f"Dismiss remote copy link {source_port}:{target_port_wwn_or_ip} successful.", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Dismiss remote copy link {source_port}:{target_port_wwn_or_ip} failed: {e}")
            return (False, False, f"Dismiss remote copy link failed | {e}", {})

    def admit_remote_copy_target(self, remote_copy_group_name, target_name, target_mode, local_remote_volume_pair_list=None):
        """Orchestrate admit remote copy target operation."""
        self.logger.info(f"AnsibleClient: Admitting remote copy target '{target_name}' to group '{remote_copy_group_name}'")
        try:
            remote_copy_utils.preprocess_admit_remote_copy_target(remote_copy_group_name, target_name, target_mode, local_remote_volume_pair_list)
            source_name = self.system_workflow.get_storage_system_info()['name']
            if target_name == source_name:
                self.logger.warning(f"AnsibleClient: Source and target cannot be same for remote copy target")
                return (False, False, f"Source and target cannot be same. Source and target both are {source_name}", {})
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' not present")
                return (False, False, f"Remote Copy Group '{remote_copy_group_name}' not present", {})
            # Idempotency: if target already in group treat as no-change
            group = self.remote_copy_workflow.get_remote_copy_group(remote_copy_group_name)
            if any(target.get('targetName') == target_name for target in group.get('targets', [])):
                self.logger.warning(f"AnsibleClient: Remote copy target '{target_name}' already present in group '{remote_copy_group_name}'")
                return (True, False, f"Remote Copy target '{target_name}' already present in group '{remote_copy_group_name}'", {})
            source_target_volume_pairs = []
            # Append volume pairs if any
            if local_remote_volume_pair_list is not None:
                for volumePair in local_remote_volume_pair_list:
                    source_target_pair = \
                        volumePair.get('sourceVolumeName') + ':' + \
                        volumePair.get('targetVolumeName')
                    source_target_volume_pairs.append(source_target_pair)
            resp = self.remote_copy_workflow.admit_remote_copy_target(remote_copy_group_name, target_name, target_mode, source_target_volume_pairs)
            err_resp = self.check_response_for_admittarget(resp, target_name)
            if err_resp:
                raise exceptions_v1.SSHException(err_resp)
            self.logger.info(f"AnsibleClient: Remote copy target '{target_name}' admitted to group '{remote_copy_group_name}' successfully")
            return (True, True, f"Admit remote copy target {target_name} successful in remote copy group {remote_copy_group_name}.", resp)
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Admit remote copy target '{target_name}' to group '{remote_copy_group_name}' failed: {e}")
            return (False, False, f"Admit remote copy target failed | {e}", {})

    def dismiss_remote_copy_target(self, remote_copy_group_name, target_name):
        """Orchestrate dismiss remote copy target operation."""
        self.logger.info(f"AnsibleClient: Dismissing remote copy target '{target_name}' from group '{remote_copy_group_name}'")
        try:
            remote_copy_utils.preprocess_dismiss_remote_copy_target(remote_copy_group_name, target_name)
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' not present")
                return (False, False, f"Remote Copy Group '{remote_copy_group_name}' not present", {})
            group = self.remote_copy_workflow.get_remote_copy_group(remote_copy_group_name)
            if not any(target.get('targetName') == target_name for target in group.get('targets', [])):
                self.logger.warning(f"AnsibleClient: Remote copy target '{target_name}' already not present in group '{remote_copy_group_name}'")
                return (True, False, f"Remote copy target '{target_name}' already not present in group '{remote_copy_group_name}'", {})
            resp = self.remote_copy_workflow.dismiss_remote_copy_target(remote_copy_group_name, target_name)
            for message in resp:
                if "has been dismissed from group" in message:
                    self.logger.info(f"AnsibleClient: Remote copy target '{target_name}' dismissed from group '{remote_copy_group_name}' successfully")
                    return (True, True, f"Dismiss remote copy target {target_name} successful.", {})
            raise exceptions_v1.SSHException(resp)
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Dismiss remote copy target '{target_name}' from group '{remote_copy_group_name}' failed: {e}")
            return (False, False, f"Dismiss remote copy target failed | {e}", {})

    def remote_copy_group_status_check(self, remote_copy_group_name):
        """Retrieve remote copy group status with preprocessing and custom message semantics."""
        self.logger.info(f"AnsibleClient: Checking remote copy group '{remote_copy_group_name}' status")
        try:
            if not self.remote_copy_workflow.remote_copy_group_exists(remote_copy_group_name):
                self.logger.warning(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' is not present")
                return (True, False, f"Remote Copy Group '{remote_copy_group_name}' is not present", {})
            status = self.remote_copy_group_status(remote_copy_group_name)
            if not status:
                self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' status is not complete")
                return (True, False, f"Remote copy group {remote_copy_group_name} status is not in complete", { 'remote_copy_sync_status': status })
            self.logger.info(f"AnsibleClient: Remote copy group '{remote_copy_group_name}' status is complete")
            return (True, False, f"Remote copy group {remote_copy_group_name} status is complete", { 'remote_copy_sync_status': status })
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Could not get remote copy group '{remote_copy_group_name}' status: {e}")
            return (False, False, f"Could not get remote copy group status | {e}", {})

    def show_remote_copy_service(self):
        """Show remote copy service status."""
        self.logger.info("AnsibleClient: Checking remote copy service status")
        resp = self.remote_copy_workflow.show_remote_copy_service()
        for line in resp:
            if 'Status' in line and 'Started' in line:
                self.logger.info("AnsibleClient: Remote copy service is started")
                return True  # treat as already started
        self.logger.info("AnsibleClient: Remote copy service is not started")
        return False

    def rcopy_link_exists(self, target_name, source_port, target_port_wwn_or_ip):
        """Check if remote copy link exists."""
        self.logger.info(f"AnsibleClient: Checking if remote copy link {source_port}:{target_port_wwn_or_ip} exists for target '{target_name}'")
        response = self.remote_copy_workflow.get_rcopy_links()
        self.logger.debug(f"AnsibleClient: Remote copy links response: {response}")
        for item in response:
            self.logger.debug(f"AnsibleClient: Processing remote copy link item: {item}")
            #Changed the implementation to Split based on empty space instead of
            # comma(,) earlier noticed from 10.5.50 Alletra MP version response is separted
            # by space.
            if item.startswith(target_name):
                link_info = item.split(' ')
                if link_info[0] == target_name and \
                        link_info[1] == source_port and \
                        link_info[2] == target_port_wwn_or_ip:
                    self.logger.info(f"AnsibleClient: Remote copy link {source_port}:{target_port_wwn_or_ip} exists")
                    return True
        self.logger.info(f"AnsibleClient: Remote copy link {source_port}:{target_port_wwn_or_ip} does not exist")
        return False

    def start_remote_copy_service(self):
        """Start remote copy service via SSH (idempotent)."""
        self.logger.info(f"AnsibleClient: Starting remote copy service")
        try:
            if self.show_remote_copy_service():
                self.logger.warning(f"AnsibleClient: Remote copy service already started")
                return (True, False, "Remote copy service already started", {})
            resp = self.remote_copy_workflow.start_remote_copy_service()
            if resp != []:
                raise exceptions_v1.SSHException(resp)
            self.logger.info(f"AnsibleClient: Remote copy service started successfully")
            return (True, True, "Start remote copy service successful.", {})
        except Exception as e:
            self.logger.exception(f"AnsibleClient: Start remote copy service failed: {e}")
            return (False, False, f"Start remote copy service failed | {e}", {})

    def check_response_for_admittarget(self, resp, targetName):
        """Checks whether command response having valid output
        or not if output is invalid then return that response.
        """
        for r in resp:
            if 'error' in str.lower(r) or 'invalid' in str.lower(r) \
                    or 'must specify a mapping' in str.lower(r) \
                    or 'not exist' in str.lower(r) \
                    or 'no target' in str.lower(r) \
                    or 'group contains' in str.lower(r) \
                    or 'Target is already in this group.' in str(r) \
                    or 'could not locate an indicated volume.' in str(r) \
                    or 'Target system %s could not be contacted' % targetName \
                    in str(r) \
                    or 'Target %s could not get info on secondary target' \
                    % targetName in str(r) \
                    or 'Target %s is not up and ready' % targetName in str(r) \
                    or 'A group may have only a single synchronous target.' \
                    in str(r) or \
                    'cannot have groups with more than one ' \
                    'synchronization mode' \
                    in str.lower(r):
                return r

    def logout(self):
        """
        Logout and delete session tokens for both v1 and v3 session managers.
        
        This method ensures proper cleanup by deleting authentication tokens
        from both API versions used by the client. Attempts to delete both
        sessions and raises an exception if any deletion fails.
        
        Returns:
            tuple: (success, changed, message, data)
                - success (bool): True if logout succeeded for both versions
                - changed (bool): True if sessions were actually deleted
                - message (str): Descriptive message about the operation
                - data (dict): Empty dictionary
                
        Raises:
            Exception: If any session deletion fails after attempting both
        """
        try:
            self.logger.info("AnsibleClient: Logging out from both v1 and v3 sessions")
            v3_deleted = False
            v1_deleted = False
            errors = []
            
            # Delete v3 session
            try:
                if self.session_manager_v3.token:
                    self.session_manager_v3.delete_session()
                    v3_deleted = True
                    self.logger.info("V3 session token deleted successfully")
            except Exception as e:
                error_msg = f"Failed to delete v3 session: {str(e)}"
                self.logger.exception(error_msg)
                errors.append(error_msg)
            
            # Delete v1 session
            try:
                if self.session_manager_v1.token:
                    self.session_manager_v1.delete_session()
                    v1_deleted = True
                    self.logger.info("V1 session token deleted successfully")
            except Exception as e:
                error_msg = f"Failed to delete v1 session: {str(e)}"
                self.logger.exception(error_msg)
                errors.append(error_msg)
            
            # Raise exception if any deletion failed
            if errors:
                error_message = "; ".join(errors)
                self.logger.exception(f"Logout failed with errors: {error_message}")
                raise Exception(error_message)
            
            # Complete success
            changed = v3_deleted or v1_deleted
            if changed:
                message = "Logout successful - both v1 and v3 sessions deleted"
            else:
                message = "No active sessions to logout"
            return (True, changed, message, {})
                
        except Exception as e:
            self.logger.exception("Error during logout")
            return (False, False, f"Logout failed: {str(e)}", {})