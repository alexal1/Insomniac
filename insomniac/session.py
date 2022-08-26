import json
from abc import ABC

import insomniac.__version__ as __version__
import insomniac.softban_indicator as softban_indicator
import insomniac.validations as insomniac_validations
from insomniac import network, HTTP_OK
from insomniac.action_get_my_profile_info import get_my_profile_info
from insomniac.action_runners.actions_runners_manager import CoreActionRunnersManager
from insomniac.device import DeviceWrapper
from insomniac.hardban_indicator import HardBanError
from insomniac.limits import LimitsManager
from insomniac.migration import migrate_from_json_to_sql, migrate_from_sql_to_peewee
from insomniac.navigation import close_instagram_and_system_dialogs, InstagramOpener
from insomniac.params import parse_arguments, refresh_args_by_conf_file, load_app_id
from insomniac.report import print_full_report
from insomniac.session_state import InsomniacSessionState
from insomniac.sessions import Sessions
from insomniac.sleeper import sleeper
from insomniac.softban_indicator import ActionBlockedError
from insomniac.storage import STORAGE_ARGS, InsomniacStorage, DatabaseMigrationFailedException
from insomniac.utils import *
from insomniac.views import UserSwitchFailedException, DialogView

sessions = Sessions()


def get_insomniac_session(starter_conf_file_path):
    return InsomniacSession(starter_conf_file_path)


class Session(ABC):
    SESSION_ARGS = {
        "device": {
            "help": 'device identifier. Should be used only when multiple devices are connected at once',
            "metavar": '2443de990e017ece'
        },
        "repeat": {
            "help": 'repeat the same session again after N minutes after completion, disabled by default. '
                    'It can be a number of minutes (e.g. 180) or a range (e.g. 120-180)',
            "metavar": '120-180'
        },
        "no_typing": {
            'help': 'disable "typing" feature (typing symbols one-by-one as a human)',
            'action': 'store_true'
        },
        "debug": {
            'help': 'add this flag to run insomniac in debug mode (more verbose logs)',
            'action': 'store_true'
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
        "speed": {
            'help': "manually specify the speed setting, from 1 (slowest) to 4 (fastest). "
                    "There's also 5 (superfast) but it's not recommended",
            'metavar': '1-5',
            'type': int,
            'choices': range(1, 6)
        },
        "no_speed_check": {
            'help': 'skip internet speed check at start',
            'action': 'store_true'
        },
        "no_ig_connection_check": {
            'help': 'skip Instagram connection check at start',
            'action': 'store_true'
        },
        "no_ig_version_check": {
            'help': 'skip Instagram version check at start',
            'action': 'store_true'
        }
    }

    device = None
    repeat = None
    next_config_file = None
    print_full_report_fn = print_full_report

    def __init__(self, starter_conf_file_path=None):
        self.starter_conf_file_path = starter_conf_file_path
        self.sessions = sessions

    def get_session_args(self):
        all_args = {}
        all_args.update(self.SESSION_ARGS)

        return all_args

    def reset_params(self):
        self.repeat = None
        self.next_config_file = None
        __version__.__debug_mode__ = False

    def set_session_args(self, args):
        self.reset_params()

        if args.repeat is not None:
            self.repeat = get_float_value(args.repeat, "Sleep time (min) before repeat: {:.2f}", 180.0)

        if args.debug is not None and bool(args.debug):
            __version__.__debug_mode__ = True

        if args.next_config_file is not None:
            self.next_config_file = args.next_config_file

    def parse_args(self):
        ok, args = parse_arguments(self.get_session_args(), self.starter_conf_file_path)
        if not ok:
            return None
        return args

    @staticmethod
    def print_session_params(args):
        if args.debug:
            print("All parameters:")
            for k, v in vars(args).items():
                print(f"{k}: {v} (value-type: {type(v)})")

    def repeat_session(self, args):
        print("Sleep for {:.2f} minutes".format(self.repeat))
        try:
            sleep(60 * self.repeat)
            return refresh_args_by_conf_file(args, self.next_config_file)
        except KeyboardInterrupt:
            self.print_full_report_fn(self.sessions)
            sys.exit(0)

    @staticmethod
    def update_session_speed(args):
        if args.speed is not None:
            sleeper.set_random_sleep_range(int(args.speed))
        elif not args.no_speed_check:
            print("Checking your Internet speed to adjust the script speed, please wait for a minute...")
            print("(use " + COLOR_BOLD + "--no-speed-check" + COLOR_ENDC + " to skip this check)")
            sleeper.update_random_sleep_range()

    @staticmethod
    def should_close_app_after_session(args, device_wrapper):
        if args.repeat is None:
            return True
        if not is_zero_value(args.repeat):
            return True
        return not Session.is_next_app_id_same(args, device_wrapper)

    @staticmethod
    def is_next_app_id_same(args, device_wrapper):
        if args.next_config_file is None:
            # No config file => we'll use same app_id
            return True
        return load_app_id(args.next_config_file) == device_wrapper.app_id

    @staticmethod
    def verify_instagram_version(args, installed_ig_version):
        if args.no_ig_version_check:
            return

        code, body, _ = network.get(f"https://insomniac-bot.com/get_latest_supported_ig_version/")
        if code == HTTP_OK and body is not None:
            json_config = json.loads(body)
            latest_supported_ig_version = json_config['message']
        else:
            return

        try:
            is_ok = versiontuple(installed_ig_version) <= versiontuple(latest_supported_ig_version)
        except ValueError:
            print_debug(COLOR_FAIL + "Cannot compare IG versions" + COLOR_ENDC)
            return

        if not is_ok:
            print_timeless("")
            print_timeless(COLOR_FAIL + f"IG version ({installed_ig_version}) is newer than "
                                        f"latest supported ({latest_supported_ig_version})." + COLOR_ENDC)
            if insomniac_globals.is_insomniac():
                print_timeless(COLOR_FAIL + "Please uninstall IG and download recommended apk from here:" + COLOR_ENDC)
                print_timeless(
                    COLOR_FAIL + COLOR_BOLD + "https://insomniac-bot.com/get_latest_supported_ig_apk/" + COLOR_ENDC)
                input(COLOR_FAIL + "Press ENTER to continue anyway..." + COLOR_ENDC)
            print_timeless("")

    def run(self):
        raise NotImplementedError


class InsomniacSession(Session):
    INSOMNIAC_SESSION_ARGS = {
        "wait_for_device": {
            'help': 'keep waiting for ADB-device to be ready for connection (if no device-id is provided using '
                    '--device flag, will wait for any available device)',
            'action': 'store_true',
            "default": False
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
        "old": {
            'help': 'add this flag to use an old version of uiautomator. Use it only if you experience '
                    'problems with the default version',
            'action': 'store_true'
        },
        "dont_indicate_softban": {
            "help": "by default Insomniac tries to indicate if there is a softban on your acoount. Set this flag in "
                    "order to ignore those softban indicators",
            'action': 'store_true',
            "default": False
        },
        "dont_validate_profile_existence": {
            "help": "by default, when interacting with targets, Insomniac tries to indicate if the instagram-profile "
                    "you are trying to interact-with truly exists. Set this flag in order to ignore those "
                    "existence-indicators",
            'action': 'store_true',
            "default": False
        },
        "username": {
            "help": 'if you have configured multiple Instagram accounts in your app, use this parameter in order to '
                    'switch into a specific one. Not trying to switch account by default. '
                    'If the account does not exist - the session won\'t start',
            "metavar": 'my_account_name',
            "default": None
        }
    }

    username = None

    def __init__(self, starter_conf_file_path=None):
        super().__init__(starter_conf_file_path)

        self.storage = None
        self.session_state = None
        self.actions_mgr = CoreActionRunnersManager()
        self.limits_mgr = LimitsManager()

    def get_session_args(self):
        all_args = super().get_session_args()
        all_args.update(self.INSOMNIAC_SESSION_ARGS)
        all_args.update(STORAGE_ARGS)
        all_args.update(self.actions_mgr.get_actions_args())
        all_args.update(self.limits_mgr.get_limits_args())

        return all_args

    def reset_params(self):
        super().reset_params()
        self.username = None
        softban_indicator.should_indicate_softban = True
        insomniac_validations.should_validate_profile_existence = True

    def set_session_args(self, args):
        super().set_session_args(args)

        if args.dont_indicate_softban:
            softban_indicator.should_indicate_softban = False

        if args.dont_validate_profile_existence:
            insomniac_validations.should_validate_profile_existence = False

        if args.username is not None:
            self.username = args.username

    def get_device_wrapper(self, args):
        device_wrapper = DeviceWrapper(args.device, args.old, args.wait_for_device, args.app_id, args.app_name, args.no_typing)
        device = device_wrapper.get()
        if device is None:
            return None, None

        app_version = get_instagram_version(device_wrapper.device_id, device_wrapper.app_id)
        print("Instagram version: " + app_version)
        self.verify_instagram_version(args, app_version)

        return device_wrapper, app_version

    @staticmethod
    def create_instagram_opener(args, device):
        InstagramOpener.INSTANCE = InstagramOpener(device=device,
                                                   is_with_connection_check=(not args.no_ig_connection_check))

    def prepare_session_state(self, args, device_wrapper, app_version, save_profile_info=True):
        self.session_state = InsomniacSessionState()
        self.session_state.args = args.__dict__
        self.session_state.app_id = args.app_id
        self.session_state.app_version = app_version
        self.sessions.append(self.session_state)

        device = device_wrapper.get()
        device.wake_up()

        if __version__.__debug_mode__:
            device.start_screen_record()

        DialogView(device).close_update_dialog_if_visible()
        InstagramOpener.INSTANCE.open_instagram()
        if save_profile_info:
            self.session_state.my_username, \
                self.session_state.my_followers_count, \
                self.session_state.my_following_count = get_my_profile_info(device, self.username)

        return self.session_state

    def end_session(self, device_wrapper, with_app_closing=True):
        if with_app_closing:
            close_instagram_and_system_dialogs(device_wrapper.get())
        if __version__.__debug_mode__:
            device_wrapper.get().stop_screen_record()
        print_copyright()
        self.session_state.end_session()
        print_full_report(self.sessions)
        print_timeless("")

    def on_action_callback(self, action):
        self.session_state.add_action(action)
        self.limits_mgr.update_state(action)

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
            self.limits_mgr.set_limits(args)

            try:
                self.prepare_session_state(args, device_wrapper, app_version, save_profile_info=True)
                migrate_from_json_to_sql(self.session_state.my_username)
                migrate_from_sql_to_peewee(self.session_state.my_username)
                self.storage = InsomniacStorage(self.session_state.my_username, args)
                self.session_state.set_storage_layer(self.storage)
                self.session_state.start_session()

                action_runner.run(device_wrapper,
                                  self.storage,
                                  self.session_state,
                                  self.on_action_callback,
                                  self.limits_mgr.is_limit_reached_for_action)
            except (KeyboardInterrupt, UserSwitchFailedException, DatabaseMigrationFailedException):
                self.end_session(device_wrapper)
                return
            except (ActionBlockedError, HardBanError) as ex:
                if type(ex) is ActionBlockedError:
                    self.storage.log_softban()

                if type(ex) is HardBanError and args.app_name is not None:
                    InsomniacStorage.log_hardban(args.app_name)

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
                    save_crash(device_wrapper.get(), ex)

            self.end_session(device_wrapper, with_app_closing=self.should_close_app_after_session(args, device_wrapper))
            if self.repeat is not None:
                if not self.repeat_session(args):
                    break
            else:
                break
