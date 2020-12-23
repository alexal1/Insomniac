import random
import sys

import colorama

import insomniac.__version__
from insomniac.__version__ import __debug_mode__
from insomniac.action_get_my_profile_info import get_my_profile_info
from insomniac.action_runners.actions_runners_manager import ActionRunnersManager
from insomniac.device import DeviceWrapper
from insomniac.limits import LimitsManager
from insomniac.migration import migrate_from_json_to_sql
from insomniac.params import parse_arguments, refresh_args_by_conf_file
from insomniac.report import print_full_report
from insomniac.session_state import SessionState
from insomniac.sessions import Sessions
from insomniac.sleeper import sleeper
from insomniac.softban_indicator import ActionBlockedError
from insomniac.storage import STORAGE_ARGS, Storage
from insomniac.utils import *

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
            "help": "by default, Insomniac tried to indicate if there is a softban on your acoount. set this flag in "
                    "order to ignore those soft-ban indicators",
            'action': 'store_true',
            "default": False
        },
        "debug": {
            'help': 'add this flag to insomniac in debug mode (more verbose logs)',
            'action': 'store_true'
        }
    }

    repeat = None
    device = None
    old = None

    def __init__(self):
        random.seed()
        colorama.init()

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

    def set_session_args(self, args):
        if args.repeat is not None:
            self.repeat = get_value(args.repeat, "Sleep time (min) before repeat: {}", 180)

        if args.debug is not None:
            insomniac.__version__.__debug_mode__ = True

        if args.dont_indicate_softban:
            insomniac.softban_indicator.should_indicate_softban = False

    def parse_args_and_get_device_wrapper(self):
        ok, args = parse_arguments(self.get_session_args())
        if not ok:
            return None, None, None

        device_wrapper = DeviceWrapper(args.device, args.old, args.wait_for_device, args.app_id)
        device = device_wrapper.get()
        if device is None:
            return None, None, None

        app_version = get_instagram_version(args.device, args.app_id)

        print("Instagram version: " + app_version)

        return args, device_wrapper, app_version

    def start_session(self, args, device_wrapper, app_version):
        self.session_state = SessionState()
        self.session_state.args = args.__dict__
        self.session_state.app_version = app_version
        self.sessions.append(self.session_state)

        device_wrapper.get().wake_up()

        print_timeless(COLOR_REPORT + "\n-------- START: " + str(self.session_state.startTime) + " --------" + COLOR_ENDC)

        open_instagram(args.device, args.app_id)
        sleeper.random_sleep()
        self.session_state.my_username, \
            self.session_state.my_followers_count, \
            self.session_state.my_following_count = get_my_profile_info(device_wrapper.get())

        return self.session_state

    def end_session(self, device_wrapper):
        close_instagram(device_wrapper.device_id, device_wrapper.app_id)
        print_copyright()
        self.session_state.finishTime = datetime.now()
        print_timeless(COLOR_REPORT + "-------- FINISH: " + str(self.session_state.finishTime) + " --------" + COLOR_ENDC)

        print_full_report(self.sessions)
        print_timeless("")
        self.sessions.persist(self.session_state.my_username)

    def repeat_session(self, args):
        print("Sleep for {} minutes".format(self.repeat))
        try:
            sleep(60 * self.repeat)
            refresh_args_by_conf_file(args)
        except KeyboardInterrupt:
            print_full_report(self.sessions)
            self.sessions.persist(self.session_state.my_username)
            sys.exit(0)

    def on_action_callback(self, action):
        self.session_state.add_action(action)
        self.limits_mgr.update_state(action)

    def run(self):
        args, device_wrapper, app_version = self.parse_args_and_get_device_wrapper()
        if args is None or device_wrapper is None:
            return

        if not args.no_speed_check:
            print("Checking your Internet speed to adjust the script speed, please wait for a minute...")
            print("(use " + COLOR_BOLD + "--no-speed-check" + COLOR_ENDC + " to skip this check)")
            sleeper.update_random_sleep_range()

        while True:
            self.set_session_args(args)

            action_runner = self.actions_mgr.select_action_runner(args)

            if action_runner is None:
                return

            action_runner.set_params(args)
            self.limits_mgr.set_limits(args)

            try:
                self.start_session(args, device_wrapper, app_version)
                migrate_from_json_to_sql(self.session_state.my_username)
                self.storage = Storage(self.session_state.my_username, args)

                action_runner.run(device_wrapper,
                                  self.storage,
                                  self.session_state,
                                  self.on_action_callback,
                                  self.limits_mgr.is_limit_reached_for_action)
            except KeyboardInterrupt:
                self.end_session(device_wrapper)
                return
            except ActionBlockedError as ex:
                print_timeless("")
                print_timeless(COLOR_FAIL + str(ex) + COLOR_ENDC)
                self.end_session(device_wrapper)
                return
            except Exception as ex:
                if __debug_mode__:
                    raise ex
                else:
                    print_timeless(COLOR_FAIL + f"\nCaught an exception:\n{ex}" + COLOR_ENDC)
                    save_crash(device_wrapper.get(), ex)
            
            self.end_session(device_wrapper)
            if self.repeat is not None:
                self.repeat_session(args)
            else:
                break
