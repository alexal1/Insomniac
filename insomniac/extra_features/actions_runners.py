import random
from abc import ABC

from insomniac.actions_runners import ActionRunnersManager, ActionsRunner, ActionStatus, ActionState
from insomniac.safely_runner import run_safely
from insomniac.utils import *


class ExtendedActionRunnersManager(ActionRunnersManager):
    def __init__(self):
        super().__init__()
        for clazz in get_extra_action_runners_classes():
            instance = clazz()
            self.action_runners[instance.ACTION_ID] = instance


class ExtraActionsRunner(ActionsRunner, ABC):
    """An interface for extra-actions-runner object"""


class InteractByTargetsActionRunner(ExtraActionsRunner):
    ACTION_ID = "interact_targets"
    ACTION_ARGS = {
        "interact_targets": {
            "help": "use this argument in order to interact with profiles from targets.json",
            'metavar': 'True / False'
        },
        "likes_count": {
            "help": "number of likes for each interacted user, 2 by default. "
                    "It can be a number (e.g. 2) or a range (e.g. 2-4)",
            'metavar': '2-4',
            "default": '2'
        },
        "follow_percentage": {
            "help": "follow given percentage of interacted users, 0 by default",
            "metavar": '50',
            "default": '0'
        }
    }

    likes_count = 2
    follow_percentage = 0

    def is_action_selected(self, args):
        return args.interact_targets is not None

    def set_params(self, args):
        if args.likes_count is not None:
            self.likes_count = args.likes_count

        if args.follow_percentage is not None:
            self.follow_percentage = int(args.follow_percentage)

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        from insomniac.extra_features.action_handle_target import handle_target

        for target in storage.targets:
            self.action_status = ActionStatus(ActionState.PRE_RUN)

            likes_count = get_value(self.likes_count, "Likes count: {}", 2)
            if likes_count > 12:
                print(COLOR_FAIL + "Max number of likes per user is 12" + COLOR_ENDC)
                likes_count = 12

            print_timeless("")
            print(COLOR_BOLD + "Handle @" + target + COLOR_ENDC)

            @run_safely(device_wrapper=device_wrapper)
            def job():
                self.action_status.set(ActionState.RUNNING)
                handle_target(device_wrapper.get(),
                              target,
                              session_state,
                              likes_count,
                              self.follow_percentage,
                              storage,
                              on_action,
                              is_limit_reached,
                              is_passed_filters,
                              self.action_status)

                self.action_status.set(ActionState.DONE)

            while not self.action_status.get() == ActionState.DONE:
                job()
                if self.action_status.get_limit() == ActionState.SOURCE_LIMIT_REACHED or \
                        self.action_status.get_limit() == ActionState.SESSION_LIMIT_REACHED:
                    break

            if self.action_status.get_limit() == ActionState.SOURCE_LIMIT_REACHED:
                continue

            if self.action_status.get_limit() == ActionState.SESSION_LIMIT_REACHED:
                break


class ScrapeBySourcesActionRunner(ExtraActionsRunner):
    ACTION_ID = "scrape"
    ACTION_ARGS = {
        "scrape_for_account": {
            "help": "add this argument in order to just scrape targeted profiles for an account. "
                    "The scraped profiles names will be added to targets.json file at target account directory",
            "metavar": 'your_profile'
        },
        "scrape": {
            "nargs": '+',
            "help": 'list of hashtags and usernames. Usernames should start with \"@\" symbol. '
                    'The script will scrape with hashtags\' posts likers and with users\' followers',
            "default": [],
            "metavar": ('hashtag', '@username')
        },
        "scrape_users_amount": {
            "help": 'add this argument to select an amount of users from the scraping-list '
                    '(users are randomized). It can be a number (e.g. 4) or a range (e.g. 3-8)',
            'metavar': '3-8'
        },
        "dump_profile_followers": {
            "help": 'add this argument in dump your profile followers as a part of a scrapping session into '
                    'followers.json file under your real account directory',
            'metavar': 'True / False'
        }
    }

    scrape_for_account = None
    scrape = []
    dump_profile_followers = False

    def is_action_selected(self, args):
        return args.scrape is not None and len(args.scrape) > 0 and args.scrape_for_account is not None

    def set_params(self, args):
        if args.scrape_for_account is not None:
            self.scrape_for_account = args.scrape_for_account

        if args.scrape is not None:
            self.scrape = args.scrape.copy()
            self.scrape = [source if source[0] == '@' else ('#' + source) for source in self.scrape]

        if args.dump_profile_followers is not None:
            self.dump_profile_followers = True

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

        random.shuffle(self.scrape)

        for source in self.scrape:
            self.action_status = ActionStatus(ActionState.PRE_RUN)

            if source[0] == '@':
                is_myself = source[1:] == session_state.my_username
                print_timeless("")
                print(COLOR_BOLD + "Handle " + source + (is_myself and " (it\'s you)" or "") + COLOR_ENDC)
            elif source[0] == '#':
                print_timeless("")
                print(COLOR_BOLD + "Handle " + source + COLOR_ENDC)

            @run_safely(device_wrapper=device_wrapper)
            def job():
                self.action_status.set(ActionState.RUNNING)
                if source[0] == '@':
                    handle_blogger_scrape(device_wrapper.get(),
                                          source[1:],  # drop "@"
                                          session_state,
                                          storage,
                                          on_action,
                                          is_limit_reached,
                                          is_passed_filters,
                                          self.action_status)
                elif source[0] == '#':
                    handle_hashtag_scrape(device_wrapper.get(),
                                          source[1:],  # drop "#"
                                          session_state,
                                          storage,
                                          on_action,
                                          is_limit_reached,
                                          is_passed_filters,
                                          self.action_status)

                self.action_status.set(ActionState.DONE)

            while not self.action_status.get() == ActionState.DONE:
                job()
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
        "max_following": {
            "help": 'Should be used together with --remove-mass-followers. Specifies max number of '
                    'followings for any your follower, 1000 by default',
            "metavar": '1000',
            "default": "1000"
        }
    }

    remove_mass_followers = 0
    max_following = 1000

    def is_action_selected(self, args):
        return args.remove_mass_followers is not None

    def set_params(self, args):
        if args.remove_mass_followers is not None:
            self.remove_mass_followers = get_value(args.remove_mass_followers, "Removing {} mass followers", 40)

        if args.max_following is not None:
            self.max_following = int(args.max_following)

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        pass


def get_extra_action_runners_classes():
    return ExtraActionsRunner.__subclasses__()
