from insomniac.action_runners import *
from insomniac.actions_impl import FollowingsSortOrder, UnfollowSource
from insomniac.navigation import navigate
from insomniac.safely_runner import run_safely
from insomniac.utils import *
from insomniac.views import TabBarTabs


class UnfollowActionRunner(CoreActionsRunner):
    DEFAULT_UNFOLLOW_OLDER_THAN_DAYS = 7

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
        "unfollow_source": {
            'help': 'you can specify where to take the users to unfollow from. '
                    'Can be one of the values: profile / list / database / database-global-search. '
                    '"profile" means unfollowing your profile\'s followings. '
                    '"list" means unfollowing from the "unfollow.txt" file. '
                    '"database" means unfollowing from the database sorted by date of following (older go first). '
                    '"database-global-search" is the same as "database", but searches in global search. '
                    'By default "profile" is used',
            'metavar': 'list',
            'default': 'profile'
        },
        "unfollow_older_than_days": {
            'help': 'if using "--unfollow-source database", you can specify how long ago an account has to '
                    'be followed, to unfollow it now. Specify number of days. 7 days by default',
            'metavar': DEFAULT_UNFOLLOW_OLDER_THAN_DAYS,
            'default': DEFAULT_UNFOLLOW_OLDER_THAN_DAYS
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
    unfollow_source = UnfollowSource.PROFILE
    followings_sort_order = FollowingsSortOrder.EARLIEST
    unfollow_older_than_days = DEFAULT_UNFOLLOW_OLDER_THAN_DAYS

    def is_action_selected(self, args):
        return args.unfollow is not None

    def reset_params(self):
        self.unfollow_followed_by_anyone = False
        self.unfollow_non_followers = False
        self.unfollow_source = UnfollowSource.PROFILE
        self.followings_sort_order = FollowingsSortOrder.EARLIEST
        self.unfollow_older_than_days = self.DEFAULT_UNFOLLOW_OLDER_THAN_DAYS

    def set_params(self, args):
        if args.unfollow_followed_by_anyone is not None:
            self.unfollow_followed_by_anyone = True

        if args.unfollow_non_followers is not None:
            self.unfollow_non_followers = True

        if args.unfollow_source is not None:
            if args.unfollow_source == 'profile':
                self.unfollow_source = UnfollowSource.PROFILE
            elif args.unfollow_source == 'list':
                self.unfollow_source = UnfollowSource.LIST
            elif args.unfollow_source == 'database':
                self.unfollow_source = UnfollowSource.DATABASE
            elif args.unfollow_source == 'database-global-search':
                self.unfollow_source = UnfollowSource.DATABASE_GLOBAL_SEARCH
            else:
                print(COLOR_FAIL + f"Unexpected unfollow source: \"{args.unfollow_source}" + COLOR_ENDC)

        if args.following_sort_order is not None:
            if args.following_sort_order == 'default':
                self.followings_sort_order = FollowingsSortOrder.DEFAULT
            elif args.following_sort_order == 'latest':
                self.followings_sort_order = FollowingsSortOrder.LATEST
            else:
                self.followings_sort_order = FollowingsSortOrder.EARLIEST

        if args.unfollow_older_than_days is not None:
            self.unfollow_older_than_days = int(args.unfollow_older_than_days)

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        from insomniac.action_runners.unfollow.action_unfollow import unfollow, get_unfollow_restriction

        unfollow_restriction = get_unfollow_restriction(self.unfollow_followed_by_anyone, self.unfollow_non_followers)

        self.action_status = ActionStatus(ActionState.PRE_RUN)

        @run_safely(device_wrapper=device_wrapper)
        def job():
            self.action_status.set(ActionState.RUNNING)
            navigate(device_wrapper.get(), TabBarTabs.PROFILE)
            unfollow(device=device_wrapper.get(),
                     on_action=on_action,
                     storage=storage,
                     unfollow_restriction=unfollow_restriction,
                     unfollow_source=self.unfollow_source,
                     unfollow_older_than_days=self.unfollow_older_than_days,
                     sort_order=self.followings_sort_order,
                     session_state=session_state,
                     is_limit_reached=is_limit_reached,
                     action_status=self.action_status)
            print("Unfollowed " + str(session_state.totalUnfollowed) + " " + unfollow_restriction.value + ", finish.")
            self.action_status.set(ActionState.DONE)

        while not self.action_status.get() == ActionState.DONE:
            job()
