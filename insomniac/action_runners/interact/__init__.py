from insomniac.action_runners import *
from insomniac.actions_types import TargetType
from insomniac.safely_runner import run_safely
from insomniac.utils import *


class InteractBySourceActionRunner(CoreActionsRunner):
    ACTION_ID = "interact"
    ACTION_ARGS = {
        "likes_count": {
            "help": "number of likes for each interacted user, 2 by default. "
                    "It can be a number (e.g. 2) or a range (e.g. 2-4)",
            'metavar': '2-4',
            "default": '2'
        },
        "likes_percentage": {
            "help": "likes given percentage of interacted users, 100 by default",
            "metavar": '50',
            "default": '100'
        },
        "follow_percentage": {
            "help": "follow given percentage of interacted users, 0 by default",
            "metavar": '50',
            "default": '0'
        },
        "interact": {
            "nargs": '+',
            "help": 'list of hashtags, usernames, or places. Usernames should start with \"@\" symbol. Places should '
                    'start with \"P-\" symbols. You can specify the way of interaction after a \"-\" sign: '
                    '@natgeo-followers, @natgeo-following, amazingtrips-top-likers, amazingtrips-recent-likers, '
                    'P-Paris-top-likers, P-Paris-recent-likers',
            "default": [],
            "metavar": ('amazingtrips-top-likers', '@natgeo-followers')
        },
        "interaction_users_amount": {
            "help": 'add this argument to select an amount of sources from the interact-list '
                    '(sources are randomized). It can be a number (e.g. 4) or a range (e.g. 3-8)',
            'metavar': '3-8'
        },
        "stories_count": {
            "help": 'number of stories to watch for each user, disabled by default. '
                    'It can be a number (e.g. 2) or a range (e.g. 2-4)',
            'metavar': '3-8'
        },
        "comment_percentage": {
            "help": "comment given percentage of interacted users, 0 by default",
            "metavar": '50',
            "default": '0'
        },
        "comments_list": {
            "nargs": '+',
            "help": 'list of comments you wish to comment on posts during interaction',
            "default": [],
            "metavar": ('WOW!', 'What a picture!')
        },
        "blacklist_profiles": {
            "nargs": '+',
            "help": 'list of profiles you wish to not interact with / scrape',
        }
    }

    likes_count = '2'
    follow_percentage = 0
    like_percentage = 100
    interact = []
    stories_count = '0'
    comment_percentage = 0
    comments_list = []

    def is_action_selected(self, args):
        return args.interact is not None and len(args.interact) > 0

    def reset_params(self):
        self.likes_count = '2'
        self.follow_percentage = 0
        self.like_percentage = 100
        self.interact = []
        self.stories_count = '0'
        self.comment_percentage = 0
        self.comments_list = []

    def set_params(self, args):
        self.reset_params()

        if args.likes_count is not None:
            self.likes_count = args.likes_count

        if args.stories_count is not None:
            self.stories_count = args.stories_count

        if args.interact is not None:
            self.interact = args.interact.copy()

            def is_source_hashtag(source):
                return source[0] != '@' and not source.startswith("P-")

            self.interact = [source if not is_source_hashtag(source) else ('#' + source) for source in self.interact]

        if args.follow_percentage is not None:
            self.follow_percentage = int(args.follow_percentage)

        if args.likes_percentage is not None:
            self.like_percentage = int(args.likes_percentage)

        if args.comment_percentage is not None:
            self.comment_percentage = int(args.comment_percentage)

        if args.comments_list is not None:
            self.comments_list = args.comments_list

        if args.interaction_users_amount is not None:
            if len(self.interact) > 0:
                users_amount = get_value(args.interaction_users_amount, "Interaction user amount {}", 100)

                if users_amount >= len(self.interact):
                    print("interaction-users-amount parameter is equal or higher then the users-interact list. "
                          "Choosing all list for interaction.")
                else:
                    amount_to_remove = len(self.interact) - users_amount
                    for i in range(0, amount_to_remove):
                        self.interact.remove(random.choice(self.interact))

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        from insomniac.action_runners.interact.action_handle_blogger import handle_blogger, extract_blogger_instructions
        from insomniac.action_runners.interact.action_handle_hashtag import handle_hashtag, extract_hashtag_instructions
        from insomniac.action_runners.interact.action_handle_place import handle_place, extract_place_instructions

        random.shuffle(self.interact)

        for source in self.interact:
            self.action_status = ActionStatus(ActionState.PRE_RUN)

            if source[0] == '@':
                is_myself = source[1:] == session_state.my_username
                print_timeless("")
                print(COLOR_BOLD + "Handle " + source + (is_myself and " (it\'s you)" or "") + COLOR_ENDC)
            elif source[0] == '#':
                print_timeless("")
                print(COLOR_BOLD + "Handle " + source + COLOR_ENDC)
            elif source.startswith("P-"):
                print_timeless("")
                print(COLOR_BOLD + "Handle " + source + COLOR_ENDC)

            @run_safely(device_wrapper=device_wrapper)
            def job():
                self.action_status.set(ActionState.RUNNING)
                if source[0] == '@':
                    source_name, instructions = extract_blogger_instructions(source)
                    handle_blogger(device_wrapper.get(),
                                   source_name[1:],  # drop "@"
                                   instructions,
                                   session_state,
                                   self.likes_count,
                                   self.stories_count,
                                   self.follow_percentage,
                                   self.like_percentage,
                                   self.comment_percentage,
                                   self.comments_list,
                                   storage,
                                   on_action,
                                   is_limit_reached,
                                   is_passed_filters,
                                   self.action_status)
                elif source[0] == '#':
                    source_name, instructions = extract_hashtag_instructions(source)
                    handle_hashtag(device_wrapper.get(),
                                   source_name[1:],  # drop "#"
                                   instructions,
                                   session_state,
                                   self.likes_count,
                                   self.stories_count,
                                   self.follow_percentage,
                                   self.like_percentage,
                                   self.comment_percentage,
                                   self.comments_list,
                                   storage,
                                   on_action,
                                   is_limit_reached,
                                   is_passed_filters,
                                   self.action_status)
                elif source.startswith("P-"):
                    source_name, instructions = extract_place_instructions(source[2:])
                    handle_place(device_wrapper.get(),
                                 source_name,
                                 instructions,
                                 session_state,
                                 self.likes_count,
                                 self.stories_count,
                                 self.follow_percentage,
                                 self.like_percentage,
                                 self.comment_percentage,
                                 self.comments_list,
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


class InteractByTargetsActionRunner(CoreActionsRunner):
    ACTION_ID = "interact_targets"
    ACTION_ARGS = {
        "interact_targets": {
            "help": "use this argument in order to interact with profiles from targets.txt",
            'metavar': 'True / False'
        },
        "targets_list": {
            "nargs": '+',
            "help": 'list of target-profiles you wish to interact with (in case you want to use a parameter '
                    'and not targets.txt file)',
            "default": [],
            "metavar": ('profile-A', 'profile-B')
        },
        "posts_urls_list": {
            "nargs": '+',
            "help": 'list of target-posts you wish to interact with (in case you want to use a parameter '
                    'and not targets.json file)',
            "default": [],
            "metavar": ('https://www.instagram.com/p/ID-a', 'https://www.instagram.com/p/ID-b')
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
        },
        "likes_percentage": {
            "help": "likes given percentage of interacted users, 100 by default",
            "metavar": '50',
            "default": '100'
        },
        "stories_count": {
            "help": 'number of stories to watch for each user, disabled by default. '
                    'It can be a number (e.g. 2) or a range (e.g. 2-4)',
            'metavar': '3-8'
        },
        "comment_percentage": {
            "help": "comment given percentage of interacted users, 0 by default",
            "metavar": '50',
            "default": '0'
        },
        "comments_list": {
            "nargs": '+',
            "help": 'list of comments you wish to comment on posts during interaction',
            "default": [],
            "metavar": ('WOW!', 'What a picture!')
        },
        "blacklist_profiles": {
            "nargs": '+',
            "help": 'list of profiles you wish to not interact with / scrape',
        }
    }

    likes_count = '2'
    follow_percentage = 0
    like_percentage = 100
    stories_count = '0'
    comment_percentage = 0
    comments_list = []

    def is_action_selected(self, args):
        return args.interact_targets is not None

    def reset_params(self):
        self.likes_count = '2'
        self.follow_percentage = 0
        self.like_percentage = 100
        self.stories_count = '0'
        self.comment_percentage = 0
        self.comments_list = []

    def set_params(self, args):
        self.reset_params()

        if args.likes_count is not None:
            self.likes_count = args.likes_count

        if args.stories_count is not None:
            self.stories_count = args.stories_count

        if args.follow_percentage is not None:
            self.follow_percentage = int(args.follow_percentage)

        if args.likes_percentage is not None:
            self.like_percentage = int(args.likes_percentage)

        if args.comment_percentage is not None:
            self.comment_percentage = int(args.comment_percentage)

        if args.comments_list is not None:
            self.comments_list = args.comments_list

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        from insomniac.action_runners.interact.action_handle_target import handle_target

        target, target_type = storage.get_target()
        while target is not None:
            self.action_status = ActionStatus(ActionState.PRE_RUN)

            print_timeless("")
            print(COLOR_BOLD + f"Handle {'@' if target_type == TargetType.USERNAME else ''}" + target + COLOR_ENDC)

            @run_safely(device_wrapper=device_wrapper)
            def job():
                self.action_status.set(ActionState.RUNNING)
                handle_target(device_wrapper.get(),
                              target,
                              target_type,
                              session_state,
                              self.likes_count,
                              self.stories_count,
                              self.follow_percentage,
                              self.like_percentage,
                              self.comment_percentage,
                              self.comments_list,
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

            target, target_type = storage.get_target()

        if target is None:
            print("There are no more new targets to interact with in the database (all been already interacted / filtered).")
            print("If you wish to continue interacting with targets, add new targets to the database using scrapping / targets.txt "
                  "or use the reinteract-after & refilter-after parameters in order to interact with the targets that are already loaded "
                  "in the database.")
