import random
import sys

import colorama

from insomniac.__version__ import __debug_mode__
from insomniac.action_get_my_profile_info import get_my_profile_info
from insomniac.actions_runners import ActionRunnersManager
from insomniac.device import DeviceWrapper
from insomniac.limits import LimitsManager
from insomniac.params import parse_arguments, refresh_args_by_conf_file
from insomniac.persistent_list import PersistentList
from insomniac.report import print_full_report
from insomniac.session_state import SessionStateEncoder, SessionState
from insomniac.storage import Storage
from insomniac.utils import *

sessions = PersistentList("sessions", SessionStateEncoder)


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
        "old": {
            'help': 'add this flag to use an old version of uiautomator. Use it only if you experience '
                    'problems with the default version',
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
        all_args.update(self.actions_mgr.get_actions_args())
        all_args.update(self.limits_mgr.get_limits_args())

        return all_args

    def set_session_args(self, args):
        if args.repeat is not None:
            self.repeat = get_value(args.repeat, "Sleep time (min) before repeat: {}", 180)

    def parse_args_and_get_device_wrapper(self):
        ok, args = parse_arguments(self.get_session_args())
        if not ok:
            return None, None

        device_wrapper = DeviceWrapper(args.device, args.old)
        device = device_wrapper.get()
        if device is None:
            return None, None

        print("Instagram version: " + get_instagram_version())

        return args, device_wrapper

    def start_session(self, args, device_wrapper):
        self.session_state = SessionState()
        self.session_state.args = args.__dict__
        self.sessions.append(self.session_state)

        print_timeless(COLOR_REPORT + "\n-------- START: " + str(self.session_state.startTime) + " --------" + COLOR_ENDC)
        open_instagram(self.device)
        self.session_state.my_username, \
            self.session_state.my_followers_count, \
            self.session_state.my_following_count = get_my_profile_info(device_wrapper.get())

        return self.session_state

    def end_session(self, device_wrapper):
        close_instagram(device_wrapper.device_id)
        print_copyright()
        self.session_state.finishTime = datetime.now()
        print_timeless(COLOR_REPORT + "-------- FINISH: " + str(self.session_state.finishTime) + " --------" + COLOR_ENDC)

    def repeat_session(self, args):
        print_full_report(self.sessions)
        print_timeless("")
        self.sessions.persist(directory=self.session_state.my_username)
        print("Sleep for {} minutes".format(self.repeat))
        try:
            sleep(60 * self.repeat)
            refresh_args_by_conf_file(args)
        except KeyboardInterrupt:
            print_full_report(self.sessions)
            self.sessions.persist(directory=self.session_state.my_username)
            sys.exit(0)

    def on_action_callback(self, action):
        self.session_state.add_action(action)
        self.limits_mgr.update_state(action)

    def run(self):
        args, device_wrapper = self.parse_args_and_get_device_wrapper()

        while True:
            if args is None or device_wrapper is None:
                return

            self.set_session_args(args)

            action_runner = self.actions_mgr.select_action_runner(args)

            if action_runner is None:
                return

            action_runner.set_params(args)
            self.limits_mgr.set_limits(args)

            try:
                self.start_session(args, device_wrapper)
                self.storage = Storage(self.session_state.my_username, args)

                action_runner.run(device_wrapper,
                                  self.storage,
                                  self.session_state,
                                  self.on_action_callback,
                                  self.limits_mgr.is_limit_reached_for_action)

                self.end_session(device_wrapper)
            except Exception as ex:
                if __debug_mode__:
                    raise ex
                else:
                    print_timeless(COLOR_FAIL + f"\nCaught an exception:\n{ex}" + COLOR_ENDC)
                    save_crash(device_wrapper.get())

            if self.repeat is not None:
                self.repeat_session(args)
            else:
                break

        print_full_report(self.sessions)
        self.sessions.persist(directory=self.session_state.my_username)
