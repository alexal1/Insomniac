import os
from abc import ABC

from insomniac.device import DeviceWrapper
from insomniac.utils import COLOR_FAIL, COLOR_ENDC
from insomniac.action_runners.actions_runners_manager import ActionRunnersManager, ActionsRunner, ActionStatus, \
    ActionState
from insomniac.safely_runner import run_registration_safely


class ManagementActionRunnersManager(ActionRunnersManager):
    def __init__(self):
        super().__init__()

        for clazz in get_management_action_runners_classes():
            instance = clazz()
            self.action_runners[instance.ACTION_ID] = instance


class ManagementActionsRunner(ActionsRunner, ABC):
    """An interface for extra-actions-runner object"""

    def run(self, storage, session_state, on_action):
        raise NotImplementedError()


class AppCloneCreationActionRunner(ManagementActionsRunner):
    ACTION_ID = "create_clones"
    ACTION_ARGS = {
        "create_clones": {
            "action": 'store_true',
            "default": False
        },
        "apk_store_path": {
            "help": 'directory path for apk store',
            "metavar": 'apks/'
        },
        "users_list": {
            "nargs": '+',
            "default": []
        }
    }

    appcloner_host_device = None
    apk_store_path = 'apks'
    users_list = []

    def is_action_selected(self, args):
        return args.create_clones and len(args.users_list) > 0

    def reset_params(self):
        self.appcloner_host_device = None
        self.apk_store_path = 'apks'
        self.users_list = []

    def set_params(self, args):
        if args.device is None:
            raise Exception('Parameter device must be provided in order to use clones creation flow')

        self.appcloner_host_device = args.device
        self.apk_store_path = args.apk_store_path if args.apk_store_path is not None else 'apks'
        self.users_list = args.users_list

    def run(self, storage, session_state, on_action):
        from insomniac.extra_features.action_manage_clones import create_clones

        try:
            os.makedirs(self.apk_store_path, exist_ok=True)
        except OSError:
            print(COLOR_FAIL + f"Failed to create directory {self.apk_store_path}" + COLOR_ENDC)
            raise

        self.action_status = ActionStatus(ActionState.PRE_RUN)

        def job():
            self.action_status.set(ActionState.RUNNING)
            create_clones(self.appcloner_host_device, self.users_list, self.apk_store_path, session_state, on_action)
            self.action_status.set(ActionState.DONE)

        while not self.action_status.get() == ActionState.DONE:
            job()


class AppCloneInstallActionRunner(ManagementActionsRunner):
    ACTION_ID = "install_clones"
    ACTION_ARGS = {
        "install_clones": {
            "action": 'store_true',
            "default": False
        },
        "apk_store_path": {
            "help": 'directory path for apk store',
            "metavar": './apks'
        },
        "users_passwords_list": {
            "nargs": '+',
            "default": []
        }
    }

    device_for_clones_installation = None
    apk_store_path = 'apks'
    users_passwords_list = []

    def is_action_selected(self, args):
        return args.install_clones and len(args.users_passwords_list) > 0

    def reset_params(self):
        self.device_for_clones_installation = None
        self.apk_store_path = 'apks'
        self.users_passwords_list = []

    def set_params(self, args):
        if args.device is None:
            raise Exception('Parameter device must be provided in order to use clones installation flow')

        self.device_for_clones_installation = args.device
        self.apk_store_path = args.apk_store_path if args.apk_store_path is not None else 'apks'
        self.users_passwords_list = args.users_passwords_list

    def run(self, storage, session_state, on_action):
        from insomniac.extra_features.action_manage_clones import install_clones

        if not os.path.exists(self.apk_store_path):
            raise Exception(f'APK Store directory {self.apk_store_path} does not exists')

        self.action_status = ActionStatus(ActionState.PRE_RUN)

        def job():
            self.action_status.set(ActionState.RUNNING)
            install_clones(self.device_for_clones_installation, self.users_passwords_list, self.apk_store_path, session_state, on_action)
            self.action_status.set(ActionState.DONE)

        while not self.action_status.get() == ActionState.DONE:
            job()


class AppCloneRemovalActionRunner(ManagementActionsRunner):
    ACTION_ID = "remove_clones"
    ACTION_ARGS = {
        "remove_clones": {
            "action": 'store_true',
            "default": False
        },
        "users_list": {
            "nargs": '+',
            "default": []
        }
    }

    device_for_clones_removal = None
    users_list = []

    def is_action_selected(self, args):
        return args.remove_clones and len(args.users_list) > 0

    def reset_params(self):
        self.device_for_clones_removal = None
        self.users_list = []

    def set_params(self, args):
        if args.device is None:
            raise Exception('Parameter device must be provided in order to use clones removal flow')

        self.device_for_clones_removal = args.device
        self.users_list = args.users_list

    def run(self, storage, session_state, on_action):
        from insomniac.extra_features.action_manage_clones import remove_clones

        self.action_status = ActionStatus(ActionState.PRE_RUN)

        def job():
            self.action_status.set(ActionState.RUNNING)
            remove_clones(self.device_for_clones_removal, self.users_list, session_state, on_action)
            self.action_status.set(ActionState.DONE)

        while not self.action_status.get() == ActionState.DONE:
            job()


class RegisterAccountsActionRunner(ManagementActionsRunner):
    ACTION_ID = "register"
    ACTION_ARGS = {
        "register": {
            "help": 'path to the file with the list of users to register',
            "metavar": 'users.txt'
        },
        "app_id": {
            "help": 'apk package identifier. Should be used only if you are using cloned-app. '
                    'Using \'com.instagram.android\' by default',
            "metavar": 'com.instagram.android',
            "default": 'com.instagram.android'
        },
        "app_name": {
            "default": None
        },
    }

    register = None
    device_wrapper = None

    def is_action_selected(self, args):
        return args.register is not None

    def reset_params(self):
        self.register = None
        self.device_wrapper = None

    def set_params(self, args):
        self.register = args.register
        self.device_wrapper = DeviceWrapper(device_id=args.device,
                                            old_uiautomator=False,
                                            wait_for_device=False,
                                            app_id=args.app_id,
                                            app_name=args.app_name,
                                            dont_set_typewriter=True)

    def run(self, storage, session_state, on_action):
        from insomniac.extra_features.action_register_accounts import register_accounts
        self.action_status = ActionStatus(ActionState.PRE_RUN)

        @run_registration_safely(device_wrapper=self.device_wrapper)
        def job():
            self.action_status.set(ActionState.RUNNING)
            register_accounts(self.device_wrapper, self.register, session_state, on_action)
            self.action_status.set(ActionState.DONE)

        while not self.action_status.get() == ActionState.DONE:
            job()


def get_management_action_runners_classes():
    return ManagementActionsRunner.__subclasses__()
