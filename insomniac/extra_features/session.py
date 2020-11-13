from insomniac.__version__ import __debug_mode__
from insomniac.extra_features.actions_runners import ExtendedActionRunnersManager
from insomniac.extra_features.filters import FiltersManager
from insomniac.extra_features.limits import ExtendedLimitsManager
from insomniac.extra_features.utils import is_at_working_hour
from insomniac.report import print_full_report
from insomniac.session import InsomniacSession
from insomniac.storage import Storage
from insomniac.utils import *


class ExtendedInsomniacSession(InsomniacSession):
    EXTENDED_SESSION_ARGS = {
        "working-hours": {
            "help": 'set working hours to the script, disabled by default. '
                    'It can be a number presenting specific hour (e.g. 13) or a range (e.g. 9-21). '
                    'Notice that right value must be higher than the left value.',
            "metavar": '9-21'
        }
    }

    working_hours = None

    def __init__(self):
        super().__init__()

        self.filters_mgr = FiltersManager()
        self.actions_mgr = ExtendedActionRunnersManager()
        self.limits_mgr = ExtendedLimitsManager()

    def get_session_args(self):
        all_args = {}
        all_args.update(self.SESSION_ARGS)
        all_args.update(self.EXTENDED_SESSION_ARGS)
        all_args.update(self.filters_mgr.get_filters_args())
        all_args.update(self.actions_mgr.get_actions_args())
        all_args.update(self.limits_mgr.get_limits_args())

        return all_args

    def set_session_args(self, args):
        super().set_session_args(args)
        self.working_hours = args.working_hours

    def wait_for_working_hours(self):
        can_continue, time_till_next_execution_seconds = is_at_working_hour(self.working_hours)

        if not can_continue:
            print("Going to sleep until working time ({0} minutes)...".format(int(time_till_next_execution_seconds / 60)))
            sleep(time_till_next_execution_seconds)

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
            self.filters_mgr.set_filters(args)

            if self.working_hours is not None:
                self.wait_for_working_hours()

            try:
                self.start_session(args, device_wrapper)
                self.storage = Storage(self.session_state.my_username, args)

                action_runner.run(device_wrapper,
                                  self.storage,
                                  self.session_state,
                                  self.on_action_callback,
                                  self.limits_mgr.is_limit_reached_for_action,
                                  self.filters_mgr.check_filters)

                self.end_session(device_wrapper)
            except Exception as ex:
                if __debug_mode__:
                    raise ex
                else:
                    print_timeless(COLOR_FAIL + f"\nCaught an exception:\n{ex}" + COLOR_ENDC)

            if self.repeat is not None:
                self.repeat_session(args)
            else:
                break

        print_full_report(self.sessions)
        self.sessions.persist(directory=self.session_state.my_username)
