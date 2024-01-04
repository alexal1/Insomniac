from typing import Optional

from insomniac.session_state import SessionState
from insomniac.extra_features.storage import InsomniacManagementStorage
from insomniac.extra_features.management_actions_types import *


class ManagementSessionState(SessionState):
    storage: Optional[InsomniacManagementStorage] = None
    totalClonesCreation = []
    totalClonesInstallation = []
    totalClonesDeletion = []
    totalAppDataCleanups = []
    totalRegisteredAccounts = []

    def __init__(self):
        super().__init__()
        self.totalClonesCreation = []
        self.totalClonesInstallation = []
        self.totalClonesDeletion = []
        self.totalAppDataCleanups = []
        self.totalRegisteredAccounts = []

    def start_session_impl(self):
        session_id = self.storage.start_session(args=self.args, app_id='', app_version='',
                                                followers_count=0, following_count=0)
        
        if session_id is not None:
            self.id = session_id

    def add_action(self, action):
        if type(action) == CloneCreationAction:
            self.totalClonesCreation.append(action.user)
            self.storage.log_clone_creation_action(self.id, action.user, action.appcloner_host_device)

        if type(action) == CloneInstallationAction:
            self.totalClonesInstallation.append(action.user)
            self.storage.log_clone_installation_action(self.id, action.user, action.target_device,
                                                       action.profile_status)

        if type(action) == CloneRemovalAction:
            self.totalClonesDeletion.append(action.user)
            self.storage.log_clone_removal_action(self.id, action.user, action.target_device)

        if type(action) == AppDataCleanupAction:
            self.totalAppDataCleanups.append(action.user)
            self.storage.log_app_data_cleanup_action(self.id, action.user, action.target_device)

        if type(action) == ProfileRegistrationAction:
            self.totalRegisteredAccounts.append(action.user)
            self.storage.log_profile_registration_action(self.id, action.user, action.target_device)
