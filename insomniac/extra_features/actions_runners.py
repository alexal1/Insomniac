from abc import ABC

from insomniac.action_runners.actions_runners_manager import CoreActionRunnersManager, InsomniacActionsRunner, \
    ActionStatus, \
    ActionState
from insomniac.navigation import navigate
from insomniac.safely_runner import run_safely
from insomniac.utils import *
from insomniac.views import TabBarTabs


class ExtendedActionRunnersManager(CoreActionRunnersManager):
    def __init__(self):
        super().__init__()

        for clazz in get_extra_action_runners_classes():
            instance = clazz()
            self.action_runners[instance.ACTION_ID] = instance


class ExtraActionsRunner(InsomniacActionsRunner, ABC):
    """An interface for extra-actions-runner object"""


class ScrapeBySourcesActionRunner(ExtraActionsRunner):
    ACTION_ID = "scrape"
    ACTION_ARGS = {
        "scrape_for_account": {
            "nargs": '+',
            "help": "add this argument in order to just scrape targeted profiles for an account. "
                    "The scraped profiles names will be added to database at target account directory",
            "default": [],
            "metavar": 'your_profile'
        },
        "scrape": {
            "nargs": '+',
            "help": 'list of hashtags, usernames, or places. Usernames should start with \"@\" symbol. Places should '
                    'start with \"P-\" symbols. You can specify the way of interaction after a \"-\" sign: '
                    '@natgeo-followers, @natgeo-following, amazingtrips-top-likers, amazingtrips-recent-likers, '
                    'P-Paris-top-likers, P-Paris-recent-likers',
            "default": [],
            "metavar": ('hashtag-top-likers', '@username-followers')
        },
        "scrape_users_amount": {
            "help": 'add this argument to select an amount of sources from the scraping-list '
                    '(sources are randomized). It can be a number (e.g. 4) or a range (e.g. 3-8)',
            'metavar': '3-8'
        },
        "blacklist_profiles": {
            "nargs": '+',
            "help": 'list of profiles you wish to not interact with / scrape',
        }
    }

    scrape = []

    def is_action_selected(self, args):
        return args.scrape is not None and len(args.scrape) > 0 and args.scrape_for_account is not None

    def reset_params(self):
        self.scrape = []

    def set_params(self, args):
        if args.scrape is not None:
            self.scrape = args.scrape.copy()

            def is_source_hashtag(source):
                return source[0] != '@' and not source.startswith("P-")

            self.scrape = [source if not is_source_hashtag(source) else ('#' + source) for source in self.scrape]

        if args.scrape_users_amount is not None:
            if len(self.scrape) > 0:
                users_amount = get_value(args.scrape_users_amount, "Scrape user amount {}", 100)

                if users_amount >= len(self.scrape):
                    print("scrape-users-amount parameter is equal or higher then the users-scrape list. "
                          "Choosing all list for scrapping.")
                else:
                    amount_to_remove = len(self.scrape) - users_amount
                    for i in range(0, amount_to_remove):
                        self.scrape.remove(random.choice(self.scrape))

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        from insomniac.extra_features.action_handle_blogger_scrape import handle_blogger_scrape
        from insomniac.extra_features.action_handle_hashtag_scrape import handle_hashtag_scrape
        from insomniac.extra_features.action_handle_place_scrape import handle_place_scrape
        from insomniac.action_runners.interact.action_handle_blogger import extract_blogger_instructions
        from insomniac.action_runners.interact.action_handle_hashtag import extract_hashtag_instructions
        from insomniac.action_runners.interact.action_handle_place import extract_place_instructions

        random.shuffle(self.scrape)
        current_scrape_index = 0

        while current_scrape_index < len(self.scrape):
            self.action_status = ActionStatus(ActionState.PRE_RUN)

            @run_safely(device_wrapper=device_wrapper)
            def job():
                source = self.scrape[current_scrape_index]
                self.action_status.set(ActionState.RUNNING)
                navigate(device_wrapper.get(), TabBarTabs.PROFILE)
                if source[0] == '@':
                    is_myself = source[1:] == session_state.my_username
                    print_timeless("")
                    print(COLOR_BOLD + "Handle " + source + (is_myself and " (it\'s you)" or "") + COLOR_ENDC)

                    source_name, instructions = extract_blogger_instructions(source)
                    handle_blogger_scrape(device_wrapper.get(),
                                          source_name[1:],  # drop "@"
                                          instructions,
                                          session_state,
                                          storage,
                                          on_action,
                                          is_limit_reached,
                                          is_passed_filters,
                                          self.action_status)
                elif source[0] == '#':
                    print_timeless("")
                    print(COLOR_BOLD + "Handle " + source + COLOR_ENDC)

                    source_name, instructions = extract_hashtag_instructions(source)
                    handle_hashtag_scrape(device_wrapper.get(),
                                          source_name[1:],  # drop "#"
                                          instructions,
                                          session_state,
                                          storage,
                                          on_action,
                                          is_limit_reached,
                                          is_passed_filters,
                                          self.action_status)
                elif source.startswith("P-"):
                    print_timeless("")
                    print(COLOR_BOLD + "Handle " + source + COLOR_ENDC)

                    source_name, instructions = extract_place_instructions(source[2:])
                    handle_place_scrape(device_wrapper.get(),
                                        source_name,
                                        instructions,
                                        session_state,
                                        storage,
                                        on_action,
                                        is_limit_reached,
                                        is_passed_filters,
                                        self.action_status)

                self.action_status.set(ActionState.DONE)

            while (not self.action_status.get() == ActionState.DONE) and current_scrape_index < len(self.scrape):
                job()
                current_scrape_index += 1
                if self.action_status.get_limit() == ActionState.SOURCE_LIMIT_REACHED or \
                        self.action_status.get_limit() == ActionState.SESSION_LIMIT_REACHED:
                    break

            if self.action_status.get_limit() == ActionState.SOURCE_LIMIT_REACHED:
                continue

            if self.action_status.get_limit() == ActionState.SESSION_LIMIT_REACHED:
                break


class RemoveMassFollowersActionRunner(ExtraActionsRunner):
    ACTION_ID = "remove_mass_followers"
    ACTION_ARGS = {
        "remove_mass_followers": {
            "help": 'Remove given number of mass followers from the list of your followers. "Mass followers" '
                    'are those who has more than N followings, where N can be set via --max-following. '
                    'It can be a number (e.g. 4) or a range (e.g. 3-8)',
            "metavar": '10-20'
        },
        "mass_follower_min_following": {
            "help": 'Should be used together with --remove-mass-followers. Specifies max number of '
                    'followings for any your follower, 1000 by default',
            "metavar": '1000',
            "default": "1000"
        }
    }

    remove_mass_followers = 0
    mass_follower_min_following = 1000

    def is_action_selected(self, args):
        return args.remove_mass_followers is not None

    def reset_params(self):
        self.remove_mass_followers = 0
        self.mass_follower_min_following = 1000

    def set_params(self, args):
        if args.remove_mass_followers is not None:
            self.remove_mass_followers = get_value(args.remove_mass_followers, "Removing {} mass followers", 10)

        if args.mass_follower_min_following is not None:
            self.mass_follower_min_following = int(args.mass_follower_min_following)

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        from insomniac.extra_features.action_remove_mass_followers import remove_mass_followers
        self.action_status = ActionStatus(ActionState.PRE_RUN)

        @run_safely(device_wrapper=device_wrapper)
        def job():
            self.action_status.set(ActionState.RUNNING)
            navigate(device_wrapper.get(), TabBarTabs.PROFILE)
            remove_mass_followers(device_wrapper.get(),
                                  storage,
                                  is_limit_reached,
                                  session_state,
                                  self.action_status,
                                  self.mass_follower_min_following,
                                  on_action)
            self.action_status.set(ActionState.DONE)

        while not self.action_status.get() == ActionState.DONE:
            job()
            if self.action_status.get_limit() == ActionState.SOURCE_LIMIT_REACHED or \
                    self.action_status.get_limit() == ActionState.SESSION_LIMIT_REACHED:
                break


class DMActionRunner(ExtraActionsRunner):
    DEFAULT_MAX_OLD_FOLLOWERS_IN_A_ROW = 30
    ACTION_ID = "direct_messages"
    ACTION_ARGS = {
        "dm_list": {
            "nargs": '+',
            "default": [],
            "help": "List of messages to pick a random one to send. Spintax supported"
        },
        "dm_to_new_followers": {
            "default": None,
            "metavar": "1-10",
            "help": "Send direct messages to the given amount of new followers"
        },
        "dm_to_followed_by_bot_only": {
            'action': 'store_true',
            'default': False,
            "help": "If true, messages will be sent only to users whom we are following"
        },
        "dm_max_old_followers_in_a_row": {
            "help": 'Stop looking for new followers if seeing this amount of old followers in a row',
            "metavar": f'{DEFAULT_MAX_OLD_FOLLOWERS_IN_A_ROW}',
            "default": f'{DEFAULT_MAX_OLD_FOLLOWERS_IN_A_ROW}'
        }
    }

    dm_list = []
    dm_to_followed_by_bot_only = False
    dm_max_old_followers_in_a_row = DEFAULT_MAX_OLD_FOLLOWERS_IN_A_ROW

    def is_action_selected(self, args):
        return args.dm_to_new_followers is not None and len(args.dm_list) > 0

    def reset_params(self):
        self.dm_list = []
        self.dm_to_followed_by_bot_only = False
        self.dm_max_old_followers_in_a_row = self.DEFAULT_MAX_OLD_FOLLOWERS_IN_A_ROW

    def set_params(self, args):
        self.dm_list = args.dm_list
        self.dm_to_followed_by_bot_only = args.dm_to_followed_by_bot_only
        self.dm_max_old_followers_in_a_row = \
            int(args.dm_max_old_followers_in_a_row) if args.dm_max_old_followers_in_a_row \
            else self.DEFAULT_MAX_OLD_FOLLOWERS_IN_A_ROW

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        from insomniac.extra_features.action_dm import send_dms_to_new_followers
        self.action_status = ActionStatus(ActionState.PRE_RUN)

        @run_safely(device_wrapper=device_wrapper)
        def job():
            self.action_status.set(ActionState.RUNNING)
            navigate(device_wrapper.get(), TabBarTabs.PROFILE)
            send_dms_to_new_followers(device_wrapper.get(),
                                      on_action,
                                      storage,
                                      is_limit_reached,
                                      session_state,
                                      self.action_status,
                                      self.dm_list,
                                      self.dm_to_followed_by_bot_only,
                                      self.dm_max_old_followers_in_a_row)
            self.action_status.set(ActionState.DONE)

        while not self.action_status.get() == ActionState.DONE:
            job()
            if self.action_status.get_limit() == ActionState.SOURCE_LIMIT_REACHED or \
                    self.action_status.get_limit() == ActionState.SESSION_LIMIT_REACHED:
                break


def get_extra_action_runners_classes():
    return ExtraActionsRunner.__subclasses__()
