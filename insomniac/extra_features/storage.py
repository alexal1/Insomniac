import insomniac.globals as insomniac_globals
from insomniac.db_models import CloneCreationAction, CloneInstallationAction, CloneRemovalAction, \
    AppDataCleanupAction, ProfileRegistrationAction, get_ig_profile_by_profile_name
from insomniac.storage import Storage, SessionPhase

MANAGEMENT_STORAGE_ARGS = {
}


class InsomniacManagementStorage(Storage):
    MANAGEMENT_PROFILE_NAME = "management-profile"

    def _reset_state(self):
        super()._reset_state()

    def __init__(self, args):
        super().__init__(self.MANAGEMENT_PROFILE_NAME)

    def log_clone_creation_action(self, session_id, username, appcloner_host_device_id):
        params = {'username': username, 'device': appcloner_host_device_id}
        self.profile.log_management_action(session_id=session_id, management_action_type=CloneCreationAction,
                                           management_action_params=params, phase=SessionPhase.TASK_LOGIC.value,
                                           task_id=insomniac_globals.task_id, execution_id=insomniac_globals.execution_id)

    def log_clone_installation_action(self, session_id, username, target_device, profile_status):
        params = {'username': username, 'device': target_device}
        self.profile.log_management_action(session_id=session_id, management_action_type=CloneInstallationAction,
                                           management_action_params=params, phase=SessionPhase.TASK_LOGIC.value,
                                           task_id=insomniac_globals.task_id,
                                           execution_id=insomniac_globals.execution_id)

        created_profile = get_ig_profile_by_profile_name(username)
        created_profile.update_profile_info(profile_status, 0, 0)

    def log_clone_removal_action(self, session_id, username, target_device):
        params = {'username': username, 'device': target_device}
        self.profile.log_management_action(session_id=session_id, management_action_type=CloneRemovalAction,
                                           management_action_params=params, phase=SessionPhase.TASK_LOGIC.value,
                                           task_id=insomniac_globals.task_id,
                                           execution_id=insomniac_globals.execution_id)

    def log_app_data_cleanup_action(self, session_id, username, target_device):
        params = {'username': username, 'device': target_device}
        self.profile.log_management_action(session_id=session_id, management_action_type=AppDataCleanupAction,
                                           management_action_params=params, phase=SessionPhase.TASK_LOGIC.value,
                                           task_id=insomniac_globals.task_id,
                                           execution_id=insomniac_globals.execution_id)

    def log_profile_registration_action(self, session_id, username, target_device):
        params = {'username': username, 'device': target_device}
        self.profile.log_management_action(session_id=session_id, management_action_type=ProfileRegistrationAction,
                                           management_action_params=params, phase=SessionPhase.TASK_LOGIC.value,
                                           task_id=insomniac_globals.task_id,
                                           execution_id=insomniac_globals.execution_id)
