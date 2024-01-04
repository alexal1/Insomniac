import insomniac.__version__ as __version__
from insomniac import get_arg_value
from insomniac.actions_types import StartSessionAction
from insomniac.extra_features.action_warmup import warmup
from insomniac.extra_features.actions_impl import airplane_mode_on_off
from insomniac.extra_features.actions_runners import ExtendedActionRunnersManager
from insomniac.extra_features.filters import FiltersManager
from insomniac.extra_features.limits import ExtendedLimitsManager
from insomniac.extra_features.management_actions_runners import ManagementActionRunnersManager, \
    RegisterAccountsActionRunner
from insomniac.extra_features.report import print_full_management_report
from insomniac.extra_features.report_sender import send_report
from insomniac.extra_features.session_state import ManagementSessionState
from insomniac.extra_features.storage import MANAGEMENT_STORAGE_ARGS, InsomniacManagementStorage
from insomniac.extra_features.utils import install_aapt_if_needed
from insomniac.extra_features.utils import is_at_working_hour
from insomniac.globals import is_ui_process, is_session_allowed_callback
from insomniac.hardban_indicator import HardBanError
from insomniac.migration import migrate_from_json_to_sql, migrate_from_sql_to_peewee
from insomniac.safely_runner import run_safely
from insomniac.session import InsomniacSession, Session
from insomniac.softban_indicator import ActionBlockedError
from insomniac.storage import InsomniacStorage, DatabaseMigrationFailedException
from insomniac.utils import *
from insomniac.views import UserSwitchFailedException

MANAGEMENT_SESSION_ARG_NAME = 'management'


def get_insomniac_extended_features_session(starter_conf_file_path):
    is_management_session = get_arg_value(MANAGEMENT_SESSION_ARG_NAME, starter_conf_file_path) \
                            or get_arg_value(RegisterAccountsActionRunner.ACTION_ID, None)
    if is_management_session:
        return InsomniacManagementSession(starter_conf_file_path)

    return ExtendedInsomniacSession(starter_conf_file_path)


class ExtendedInsomniacSession(InsomniacSession):
    EXTENDED_INSOMNIAC_SESSION_ARGS = {
        "working_hours": {
            "help": 'set working hours to the script, disabled by default. '
                    'It can be a number presenting specific hour (e.g. 13) or a range (e.g. 9-21). '
                    'Notice that right value must be higher than the left value.',
            "metavar": '9-21'
        },
        "working_hours_without_sleep": {
            "help": "if you use flow, you maybe dont want to wait for working-hours on a specific session, "
                    "because the following session in the flow might be in the working hours and you dont "
                    "want to stop the flow. If that's the case, use this parameter.",
            "metavar": '9-21'
        },
        "pre_session_script": {
            "help": 'use this parameter if you want to run a predefined script when session starts',
            "metavar": '/path/to/my/script.sh or .bat',
            "default": None
        },
        "post_session_script": {
            "help": 'use this parameter if you want to run a predefined script when session ends',
            "metavar": '/path/to/my/script.sh or .bat',
            "default": None
        },
        "fetch_profiles_from_net": {
            "help": "add this flag to fetch profiles from the internet instead of opening each user's profile on a "
                    "device",
            "action": 'store_true',
            "default": False
        },
        "airplane_mode_on_off": {
            "action": 'store_true',
            "default": False
        },
        "warmup_time_before_session": {
            "help": 'set warmup length in minutes, disabled by default. '
                    'It can be a number (e.g. 2) or a range (e.g. 1-3).',
            "metavar": '9-21',
            "default": None
        },
        "send_stats": {
            "help": 'add this flag to send your statistics to the Telegram bot @your_insomniac_bot '
                    '(anonymous, only action counts)',
            "action": 'store_true',
            "default": False
        }
    }

    working_hours = None
    working_hours_without_sleep = False
    pre_session_script = None
    post_session_script = None
    fetch_profiles_from_net = False
    airplane_mode_on_off = False
    warmup_time_before_session = None
    should_try_warmup_and_airplane_toggle = True
    send_stats = False

    def __init__(self, starter_conf_file_path=None):
        super().__init__(starter_conf_file_path)

        self.filters_mgr = FiltersManager(self.on_action_callback)
        self.actions_mgr = ExtendedActionRunnersManager()
        self.limits_mgr = ExtendedLimitsManager()

    def get_session_args(self):
        all_args = super().get_session_args()
        all_args.update(self.EXTENDED_INSOMNIAC_SESSION_ARGS)
        all_args.update(self.filters_mgr.get_filters_args())
        all_args.update(self.actions_mgr.get_actions_args())
        all_args.update(self.limits_mgr.get_limits_args())

        return all_args

    def reset_params(self):
        super().reset_params()
        self.working_hours = None
        self.working_hours_without_sleep = None
        self.pre_session_script = None
        self.post_session_script = None
        self.fetch_profiles_from_net = False
        self.airplane_mode_on_off = False
        self.warmup_time_before_session = None
        self.send_stats = False

    def set_session_args(self, args):
        super().set_session_args(args)
        self.working_hours = args.working_hours
        self.working_hours_without_sleep = args.working_hours_without_sleep
        self.pre_session_script = args.pre_session_script
        self.post_session_script = args.post_session_script
        self.fetch_profiles_from_net = args.fetch_profiles_from_net
        self.airplane_mode_on_off = args.airplane_mode_on_off
        self.warmup_time_before_session = args.warmup_time_before_session
        if args.send_stats is not None:
            self.send_stats = args.send_stats

    def wait_for_working_hours(self) -> bool:
        """
        @return True if can start session after this call, False if switch to next session required
        """
        if self.working_hours is not None:
            should_sleep = True
            can_continue, time_till_next_execution_seconds = is_at_working_hour(self.working_hours)
        else:
            should_sleep = False
            can_continue, time_till_next_execution_seconds = is_at_working_hour(self.working_hours_without_sleep)

        if not can_continue:
            if should_sleep:
                print("Going to sleep until working time ({0} minutes)...".format(int(time_till_next_execution_seconds / 60)))
                sleep(time_till_next_execution_seconds)
            else:
                print("Proceeding to next config instead of sleeping until working-hours...")
                return False
        return True

    def prepare_session_state(self, args, device_wrapper, app_version, save_my_profile_info=True):
        if self.pre_session_script is not None:
            try:
                cmd = self.pre_session_script
                cmd = f'{cmd} --device_id {device_wrapper.device_id} --app_id {device_wrapper.app_id}'

                print("Running pre-session script.")
                print(f"Going to run command {cmd}.")

                cmd_res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")
                err = cmd_res.stderr.strip()
                if err:
                    print(COLOR_FAIL + f"Got an error while running pre-session script - {err}." + COLOR_ENDC)
                else:
                    print("Pre-session script output:")
                    print(cmd_res.stdout)
                    print("Pre-session script executed successfully.")
            except Exception as ex:
                print(COLOR_FAIL + f"Got an error while running pre-session script - {str(ex)}." + COLOR_ENDC)
                print(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)

            print("Continue to session-starting.")

        if self.should_try_warmup_and_airplane_toggle and self.airplane_mode_on_off:
            airplane_mode_on_off(device_wrapper)

        super().prepare_session_state(args, device_wrapper, app_version, save_my_profile_info)

    def end_session(self, device_wrapper, with_app_closing=True):
        super().end_session(device_wrapper, with_app_closing)
        send_report(is_bot_enabled=self.send_stats)

        if self.post_session_script is not None:
            try:
                cmd = self.post_session_script
                cmd = f'{cmd} --device_id {device_wrapper.device_id} --app_id {device_wrapper.app_id}'

                print("Running post-session script.")
                print(f"Going to run command {cmd}.")

                cmd_res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")
                err = cmd_res.stderr.strip()
                if err:
                    print(COLOR_FAIL + f"Got an error while running post-session script - {err}." + COLOR_ENDC)
                else:
                    print("Post-session script output:")
                    print(cmd_res.stdout)
                    print("Post-session script executed successfully.")
            except Exception as ex:
                print(COLOR_FAIL + f"Got an error while running post-session script - {str(ex)}." + COLOR_ENDC)
                print(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)

    def run(self):
        args = self.parse_args()
        if args is None:
            return

        while True:
            self.print_session_params(args)

            self.update_session_speed(args)

            device_wrapper, app_version = self.get_device_wrapper(args)
            if device_wrapper is None:
                return

            self.create_instagram_opener(args, device=device_wrapper.get())

            self.set_session_args(args)

            action_runner = self.actions_mgr.select_action_runner(args)

            if action_runner is None:
                return

            action_runner.reset_params()
            action_runner.set_params(args)
            install_aapt_if_needed(args.device)

            self.limits_mgr.set_limits(args)
            self.filters_mgr.set_filters(args)
            self.filters_mgr.set_fetch_profiles_from_net(self.fetch_profiles_from_net)

            if self.working_hours is not None or self.working_hours_without_sleep is not None:
                can_start_session = self.wait_for_working_hours()
                if not can_start_session:
                    if self.repeat is not None and self.repeat_session(args):
                        continue
                    else:
                        return

            try:
                self.prepare_session_state(args, device_wrapper, app_version)
                migrate_from_json_to_sql(self.session_state.my_username)
                migrate_from_sql_to_peewee(self.session_state.my_username)
                self.storage = InsomniacStorage(self.session_state.my_username, args)
                self.session_state.set_storage_layer(self.storage)

                # When using UI app, we want to check whether this session is allowed
                # (e.g. may be blocked when using mother-child method and mother account doesn't exist)
                is_session_allowed = True if insomniac_globals.is_insomniac() \
                    else is_session_allowed_callback(insomniac_globals.task_id, device_wrapper.get())
                if not is_session_allowed:
                    print(COLOR_OKBLUE + "The session is not allowed by the UI app. Finishing." + COLOR_ENDC)

                is_session_limits_reached = self.limits_mgr.is_limit_reached_for_action(
                    action=StartSessionAction(),
                    session_state=self.session_state
                )[0]
                if is_session_allowed and not is_session_limits_reached:
                    self.session_state.start_session()

                    if self.should_try_warmup_and_airplane_toggle and self.warmup_time_before_session is not None:
                        @run_safely(device_wrapper=device_wrapper)
                        def warmup_job():
                            warmup(device_wrapper.get(), self.warmup_time_before_session, self.on_action_callback)

                        self.session_state.start_warmap()
                        warmup_job()  # try only once even if crashed
                        self.session_state.end_warmap()

                    action_runner.run(device_wrapper,
                                      self.storage,
                                      self.session_state,
                                      self.on_action_callback,
                                      self.limits_mgr.is_limit_reached_for_action,
                                      self.filters_mgr.check_filters)
            except (KeyboardInterrupt, UserSwitchFailedException, DatabaseMigrationFailedException):
                self.end_session(device_wrapper)
                return
            except (ActionBlockedError, HardBanError) as ex:
                if type(ex) is ActionBlockedError:
                    self.storage.log_softban()
                    if insomniac_globals.softban_detected_callback is not None and self.username:
                        insomniac_globals.softban_detected_callback(self.username)

                if type(ex) is HardBanError:
                    if args.app_name is not None:
                        InsomniacStorage.log_hardban(args.app_name)
                    elif is_ui_process and args.username is not None:
                        # In UI app we always use only 1 account per app, so "username" parameter is the current user
                        InsomniacStorage.log_hardban(args.username)

                    if insomniac_globals.hardban_detected_callback is not None and self.username:
                        insomniac_globals.hardban_detected_callback(self.username)

                print_timeless("")
                print(COLOR_FAIL + describe_exception(ex, with_stacktrace=False) + COLOR_ENDC)
                save_crash(device_wrapper.get())
                if self.next_config_file is None:
                    self.end_session(device_wrapper)
                    return
            except Exception as ex:
                if __version__.__debug_mode__:
                    raise ex
                else:
                    print(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)
                    save_crash(device_wrapper.get())

            is_next_app_same_id = self.is_next_app_id_same(args, device_wrapper)
            self.should_try_warmup_and_airplane_toggle = not is_next_app_same_id
            self.end_session(device_wrapper, with_app_closing=self.should_close_app_after_session(args, device_wrapper))
            if self.repeat is not None:
                if not self.repeat_session(args):
                    break
            else:
                break


class InsomniacManagementSession(Session):
    INSOMNIAC_MANAGEMENT_SESSION_ARGS = {

    }

    print_full_report_fn = print_full_management_report

    def __init__(self, starter_conf_file_path=None):
        super().__init__(starter_conf_file_path)

        self.storage = None
        self.session_state = None
        self.actions_mgr = ManagementActionRunnersManager()

    def get_session_args(self):
        all_args = super().get_session_args()
        all_args.update(self.INSOMNIAC_MANAGEMENT_SESSION_ARGS)
        all_args.update(MANAGEMENT_STORAGE_ARGS)
        all_args.update(self.actions_mgr.get_actions_args())

        return all_args

    def reset_params(self):
        super().reset_params()

    def set_session_args(self, args):
        super().set_session_args(args)

    def prepare_session_state(self, args):
        self.session_state = ManagementSessionState()
        self.session_state.args = args.__dict__
        self.sessions.append(self.session_state)
        return self.session_state

    def on_action_callback(self, action):
        self.session_state.add_action(action)

    def end_session(self):
        print_copyright()
        self.session_state.end_session()
        print_full_management_report(self.sessions)
        print_timeless("")

    def run(self):
        args = self.parse_args()
        if args is None:
            return

        while True:
            self.print_session_params(args)

            self.update_session_speed(args)

            self.set_session_args(args)

            action_runner = self.actions_mgr.select_action_runner(args)

            if action_runner is None:
                return

            action_runner.reset_params()
            action_runner.set_params(args)
            install_aapt_if_needed(args.device)

            try:
                self.prepare_session_state(args)
                self.storage = InsomniacManagementStorage(args)
                self.session_state.set_storage_layer(self.storage)

                self.session_state.start_session()

                action_runner.run(self.storage,
                                  self.session_state,
                                  self.on_action_callback)
            except KeyboardInterrupt:
                self.end_session()
                return
            except Exception as ex:
                if __version__.__debug_mode__:
                    raise ex
                else:
                    print(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)

            self.end_session()
            if self.repeat is not None:
                if not self.repeat_session(args):
                    break
            else:
                break
