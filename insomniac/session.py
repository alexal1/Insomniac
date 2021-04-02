import insomniac.__version__ as __version__
import insomniac.softban_indicator as softban_indicator
from insomniac.action_get_my_profile_info import get_my_profile_info
from insomniac.action_runners.actions_runners_manager import ActionRunnersManager
from insomniac.device import DeviceWrapper
from insomniac.limits import LimitsManager
from insomniac.migration import migrate_from_json_to_sql, migrate_from_sql_to_peewee
from insomniac.params import parse_arguments, refresh_args_by_conf_file
from insomniac.report import print_full_report
from insomniac.session_state import SessionState
from insomniac.sessions import Sessions
from insomniac.sleeper import sleeper
from insomniac.softban_indicator import ActionBlockedError
from insomniac.storage import STORAGE_ARGS, Storage, DatabaseMigrationFailedException
from insomniac.utils import *
from insomniac.views import UserSwitchFailedException

sessions = Sessions()


class InsomniacSession(object):
    SESSION_ARGS = {
        "repeat": {
            "help": 'repeat the same session again after N minutes after completion, disabled by default. '
                    'It can be a number of minutes (e.g. 180) or a range (e.g. 120-180)',
            "metavar": '120-180'
        },
        "device": {
            "help": 'device identifier. Should be used only when multiple devices are connected at once',
            "metavar": '2443de990e017ece'
        },
        "wait_for_device": {
            'help': 'keep waiting for ADB-device to be ready for connection (if no device-id is provided using '
                    '--device flag, will wait for any available device)',
            'action': 'store_true',
            "default": False
        },
        "no_speed_check": {
            'help': 'skip internet speed check at start',
            'action': 'store_true'
        },
        "no_typing": {
            'help': 'disable "typing" feature (typing symbols one-by-one as a human)',
            'action': 'store_true'
        },
        "old": {
            'help': 'add this flag to use an old version of uiautomator. Use it only if you experience '
                    'problems with the default version',
            'action': 'store_true'
        },
        "app_id": {
            "help": 'apk package identifier. Should be used only if you are using cloned-app. '
                    'Using \'com.instagram.android\' by default',
            "metavar": 'com.instagram.android',
            "default": 'com.instagram.android'
        },
        "dont_indicate_softban": {
            "help": "by default Insomniac tries to indicate if there is a softban on your acoount. Set this flag in "
                    "order to ignore those softban indicators",
            'action': 'store_true',
            "default": False
        },
        "debug": {
            'help': 'add this flag to run insomniac in debug mode (more verbose logs)',
            'action': 'store_true'
        },
        "username": {
            "help": 'if you have configured multiple Instagram accounts in your app, use this parameter in order to '
                    'switch into a specific one. Not trying to switch account by default. '
                    'If the account does not exist - the session won\'t start',
            "metavar": 'my_account_name',
            "default": None
        },
        "next_config_file": {
            "help": 'configuration that will be loaded after session is finished and the bot \"sleeps\" for time '
                    'specified by the \"--repeat\" argument. You can use this argument to run multiple Insomniac '
                    'sessions one by one with different parameters. E.g. different action (interact and then unfollow),'
                    ' or different \"--username\". By default uses the same config file as been loaded for the first '
                    'session. Note that you must use \"--repeat\" with this argument!',
            "metavar": 'CONFIG_FILE',
            "default": None
        },
    }

    repeat = None
    device = None
    old = None
    username = None
    next_config_file = None

    def __init__(self, starter_conf_file_path=None):
        self.starter_conf_file_path = starter_conf_file_path

        self.sessions = sessions
        self.storage = None
        self.session_state = None
        self.actions_mgr = ActionRunnersManager()
        self.limits_mgr = LimitsManager()

    def get_session_args(self):
        all_args = {}
        all_args.update(self.SESSION_ARGS)
        all_args.update(STORAGE_ARGS)
        all_args.update(self.actions_mgr.get_actions_args())
        all_args.update(self.limits_mgr.get_limits_args())

        return all_args

    def reset_params(self):
        self.repeat = None
        self.username = None
        self.next_config_file = None
        __version__.__debug_mode__ = False
        softban_indicator.should_indicate_softban = True

    def set_session_args(self, args):
        self.reset_params()

        if args.repeat is not None:
            self.repeat = get_value(args.repeat, "Sleep time (min) before repeat: {}", 180)

        if args.debug is not None and bool(args.debug):
            __version__.__debug_mode__ = True

        if args.dont_indicate_softban:
            softban_indicator.should_indicate_softban = False

        if args.username is not None:
            self.username = args.username

        if args.next_config_file is not None:
            self.next_config_file = args.next_config_file

    def parse_args(self):
        ok, args = parse_arguments(self.get_session_args(), self.starter_conf_file_path)
        if not ok:
            return None
        return args

    def get_device_wrapper(self, args):
        device_wrapper = DeviceWrapper(args.device, args.old, args.wait_for_device, args.app_id, args.no_typing)
        device = device_wrapper.get()
        if device is None:
            return None, None

        app_version = get_instagram_version(args.device, args.app_id)

        print("Instagram version: " + app_version)

        return device_wrapper, app_version

    def start_session(self, args, device_wrapper, app_version, save_profile_info=True):
        self.session_state = SessionState()
        self.session_state.args = args.__dict__
        self.session_state.app_id = args.app_id
        self.session_state.app_version = app_version
        self.sessions.append(self.session_state)

        device_wrapper.get().wake_up()

        print_timeless(COLOR_REPORT + "\n-------- START: " + str(self.session_state.startTime) + " --------" + COLOR_ENDC)

        close_instagram(device_wrapper.device_id, device_wrapper.app_id)
        sleeper.random_sleep()

        if __version__.__debug_mode__:
            device_wrapper.get().start_screen_record()
        open_instagram(args.device, args.app_id)
        sleeper.random_sleep()
        if save_profile_info:
            self.session_state.my_username, \
                self.session_state.my_followers_count, \
                self.session_state.my_following_count = get_my_profile_info(device_wrapper.get(), self.username)

        return self.session_state

    def end_session(self, device_wrapper):
        close_instagram(device_wrapper.device_id, device_wrapper.app_id)
        if __version__.__debug_mode__:
            device_wrapper.get().stop_screen_record()
        print_copyright()
        self.session_state.end_session()
        print_timeless(COLOR_REPORT + "-------- FINISH: " + str(self.session_state.finishTime) + " --------" + COLOR_ENDC)

        print_full_report(self.sessions)
        print_timeless("")

    def repeat_session(self, args):
        print("Sleep for {} minutes".format(self.repeat))
        try:
            sleep(60 * self.repeat)
            return refresh_args_by_conf_file(args, self.next_config_file)
        except KeyboardInterrupt:
            print_full_report(self.sessions)
            sys.exit(0)

    def on_action_callback(self, action):
        self.session_state.add_action(action)
        self.limits_mgr.update_state(action)

    def print_session_params(self, args):
        if args.debug:
            print("All parameters:")
            for k, v in vars(args).items():
                print(f"{k}: {v} (value-type: {type(v)})")

    def run(self):
        args = self.parse_args()
        if args is None:
            return

        while True:
            self.print_session_params(args)

            if not args.no_speed_check:
                print("Checking your Internet speed to adjust the script speed, please wait for a minute...")
                print("(use " + COLOR_BOLD + "--no-speed-check" + COLOR_ENDC + " to skip this check)")
                sleeper.update_random_sleep_range()

            device_wrapper, app_version = self.get_device_wrapper(args)
            if device_wrapper is None:
                return

            self.set_session_args(args)

            action_runner = self.actions_mgr.select_action_runner(args)

            if action_runner is None:
                return

            action_runner.set_params(args)
            self.limits_mgr.set_limits(args)

            try:
                self.start_session(args, device_wrapper, app_version, save_profile_info=True)
                migrate_from_json_to_sql(self.session_state.my_username)
                migrate_from_sql_to_peewee(self.session_state.my_username)
                self.storage = Storage(self.session_state.my_username, args)
                self.session_state.set_storage_layer(self.storage)

                action_runner.run(device_wrapper,
                                  self.storage,
                                  self.session_state,
                                  self.on_action_callback,
                                  self.limits_mgr.is_limit_reached_for_action)
            except (KeyboardInterrupt, UserSwitchFailedException, DatabaseMigrationFailedException):
                self.end_session(device_wrapper)
                return
            except ActionBlockedError as ex:
                print_timeless("")
                print_timeless(COLOR_FAIL + str(ex) + COLOR_ENDC)
                if self.next_config_file is None:
                    self.end_session(device_wrapper)
                    return
            except Exception as ex:
                if __version__.__debug_mode__:
                    raise ex
                else:
                    print_timeless(COLOR_FAIL + f"\nCaught an exception:\n{ex}" + COLOR_ENDC)
                    print(COLOR_FAIL + traceback.format_exc() + COLOR_ENDC)
                    save_crash(device_wrapper.get(), ex)

            self.end_session(device_wrapper)
            if self.repeat is not None:
                if not self.repeat_session(args):
                    break
            else:
                break
