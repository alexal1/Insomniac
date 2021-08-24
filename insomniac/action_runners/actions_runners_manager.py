from abc import ABC

from insomniac.action_runners import *
from insomniac.utils import *


class ActionRunnersManager(ABC):
    def __init__(self):
        self.action_runners = {}

    def get_actions_args(self):
        actions_args = {}

        for key, action_runner in self.action_runners.items():
            for arg, info in action_runner.ACTION_ARGS.items():
                actions_args.update({arg: info})

        return actions_args

    def select_action_runner(self, args):
        selected_action_runners = []

        for action_runner in self.action_runners.values():
            if action_runner.is_action_selected(args):
                selected_action_runners.append(action_runner)

        if len(selected_action_runners) == 0:
            print_timeless(COLOR_FAIL + "You have to specify one of the actions: --interact, --unfollow" + COLOR_ENDC)
            return None

        if len(selected_action_runners) > 1:
            print_timeless(COLOR_FAIL + "Executing two or more actions is not supported yet." + COLOR_ENDC)
            return None

        print(COLOR_BOLD +
              "Executing \"{0}\" action.".format(selected_action_runners[0].ACTION_ID) +
              COLOR_ENDC)

        return selected_action_runners[0]


class CoreActionRunnersManager(ActionRunnersManager):
    def __init__(self):
        super().__init__()

        for clazz in get_core_action_runners_classes():
            instance = clazz()
            self.action_runners[instance.ACTION_ID] = instance
