from insomniac.action_runners import *
from insomniac.actions_impl import FollowingsSortOrder
from insomniac.safely_runner import run_safely
from insomniac.utils import *


class UnfollowActionRunner(CoreActionsRunner):
    ACTION_ID = "unfollow"
    ACTION_ARGS = {
        "unfollow": {
            "help": 'unfollow at most given number of users. Only users followed by this script will '
                    'be unfollowed. The order is from oldest to newest followings. '
                    'It can be a number (e.g. 100) or a range (e.g. 100-200)',
            "metavar": '100-200'
        },
        "unfollow_followed_by_anyone": {
            'help': 'By default, only profiles that been followed by the bot will be unfollowed. Set this parameter '
                    'if you want to unfollow any profile (even if not been followed by the bot)',
            'action': 'store_true',
            'default': None
        },
        "unfollow_non_followers": {
            'help': 'unfollow only profiles that are not following you',
            'action': 'store_true',
            'default': None
        },
        "following_sort_order": {
            "help": 'sort the following-list when unfollowing users from the list. Can be one of values: '
                    'default / latest / earliest. By default sorting by earliest',
            "metavar": 'latest',
            "default": 'earliest'
        },
        "whitelist_profiles": {
            "nargs": '+',
            "help": 'list of profiles you dont want to unfollow',
        }
    }

    unfollow_followed_by_anyone = False
    unfollow_non_followers = False
    followings_sort_order = FollowingsSortOrder.EARLIEST

    def is_action_selected(self, args):
        return args.unfollow is not None

    def reset_params(self):
        self.unfollow_followed_by_anyone = False
        self.unfollow_non_followers = False
        self.followings_sort_order = FollowingsSortOrder.EARLIEST

    def set_params(self, args):
        self.reset_params()

        if args.unfollow_followed_by_anyone is not None:
            self.unfollow_followed_by_anyone = True

        if args.unfollow_non_followers is not None:
            self.unfollow_non_followers = True

        if args.following_sort_order is not None:
            if args.following_sort_order == 'default':
                self.followings_sort_order = FollowingsSortOrder.DEFAULT
            elif args.following_sort_order == 'latest':
                self.followings_sort_order = FollowingsSortOrder.LATEST
            else:
                self.followings_sort_order = FollowingsSortOrder.EARLIEST

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        from insomniac.action_runners.unfollow.action_unfollow import unfollow, get_unfollow_restriction

        unfollow_restriction = get_unfollow_restriction(self.unfollow_followed_by_anyone, self.unfollow_non_followers)

        self.action_status = ActionStatus(ActionState.PRE_RUN)

        @run_safely(device_wrapper=device_wrapper)
        def job():
            self.action_status.set(ActionState.RUNNING)
            unfollow(device=device_wrapper.get(),
                     on_action=on_action,
                     storage=storage,
                     unfollow_restriction=unfollow_restriction,
                     sort_order=self.followings_sort_order,
                     session_state=session_state,
                     is_limit_reached=is_limit_reached,
                     action_status=self.action_status)
            print("Unfollowed " + str(session_state.totalUnfollowed) + " " + unfollow_restriction.value + ", finish.")
            self.action_status.set(ActionState.DONE)

        while not self.action_status.get() == ActionState.DONE:
            job()
