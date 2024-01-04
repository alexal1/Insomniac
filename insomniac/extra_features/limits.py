from abc import ABC

from insomniac.actions_types import ScrapeAction, RemoveMassFollowerAction, LikeAction, FollowAction, \
    UnfollowAction, StoryWatchAction, CommentAction, DirectMessageAction, GetProfileAction, StartSessionAction
from insomniac.limits import LimitsManager, Limit, LimitType
from insomniac.utils import *


class ExtendedLimitsManager(LimitsManager):
    """This class manages the actions-limits of an insomniac-session"""

    def __init__(self):
        super().__init__()
        for clazz in get_extra_limits_classes():
            instance = clazz()
            self.limits[str(instance.LIMIT_TYPE)][instance.LIMIT_ID] = instance


class ExtraLimit(Limit, ABC):
    """An interface for extra-limit object"""


class TotalScrapeLimit(ExtraLimit):
    LIMIT_ID = "total_scrape_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "total_scrape_limit": {
            "help": "deprecated - use scrape_session_limit instead. "
                    "limit on total amount of profiles-scrapping during the session, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "scrape_session_limit": {
            "help": "limit on total amount of profiles-scrapping during the session, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    total_scrape_limit = None

    def set_limit_values(self, args):
        if args.total_scrape_limit is not None or args.scrape_session_limit is not None:
            self.total_scrape_limit = get_value(args.scrape_session_limit or args.total_scrape_limit, "Total scrape limit: {}", 100)

    def is_reached_for_action(self, action, session_state):
        if self.total_scrape_limit is None:
            return False

        if not type(action) == ScrapeAction:
            return False

        return sum(session_state.totalScraped.values()) >= self.total_scrape_limit

    def reset(self):
        self.total_scrape_limit = None

    def update_state(self, action):
        pass


class SourceScrapeLimit(ExtraLimit):
    LIMIT_ID = "scrape_count"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "scrape_count": {
            "help": "Deprecated - use 'scrape_limit_per_source' instead",
            "metavar": "40-60"
        }
    }

    scrape_count = None

    def set_limit_values(self, args):
        if args.scrape_count is not None:
            print(COLOR_REPORT + "You are using a deprecated limit. The limit new name is called "
                                 "'scrape_limit_per_source'. Using scrape_count this time. "
                                 "Please switch to that name on next runs." + COLOR_ENDC)
            self.scrape_count = get_value(args.scrape_count, "Scrape count limit: {}", 20)

    def is_reached_for_action(self, action, session_state):
        if self.scrape_count is None:
            return False

        if not type(action) == ScrapeAction:
            return False

        scraped_count = session_state.totalScraped.get(action.source_name)
        return scraped_count is not None and scraped_count >= self.scrape_count

    def reset(self):
        self.scrape_count = None

    def update_state(self, action):
        pass


class ScrapeLimitPerSource(ExtraLimit):
    LIMIT_ID = "scrape_limit_per_source"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "scrape_limit_per_source": {
            "help": "number of profiles-scrapping per each blogger/hashtag, disabled by default. "
                    "It can be a number (e.g. 70) or a range (e.g. 50-80)",
            "metavar": "40-60"
        }
    }

    scrape_limit_per_source = None

    def set_limit_values(self, args):
        if args.scrape_limit_per_source is not None:
            self.scrape_limit_per_source = get_value(args.scrape_limit_per_source, "Scrape limit per source: {}", 20)

    def is_reached_for_action(self, action, session_state):
        if self.scrape_limit_per_source is None:
            return False

        if not type(action) == ScrapeAction:
            return False

        scraped_count = session_state.totalScraped.get(action.source_name)
        return scraped_count is not None and scraped_count >= self.scrape_limit_per_source

    def reset(self):
        self.scrape_limit_per_source = None

    def update_state(self, action):
        pass


class RemoveMassFollowersLimit(ExtraLimit):
    LIMIT_ID = "remove_mass_followers_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {}

    remove_mass_followers_limit = None

    def set_limit_values(self, args):
        if args.remove_mass_followers is not None:
            self.remove_mass_followers_limit = int(args.remove_mass_followers)

    def is_reached_for_action(self, action, session_state):
        if self.remove_mass_followers_limit is None:
            return False

        if not type(action) == RemoveMassFollowerAction:
            return False

        return len(session_state.removedMassFollowers) >= self.remove_mass_followers_limit

    def reset(self):
        self.remove_mass_followers_limit = None

    def update_state(self, action):
        pass


class LikeTimedLimit(ExtraLimit):
    LIMIT_ID = "like_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "likes_hourly_limit": {
            "help": "limit on total amount of like-actions during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "likes_daily_limit": {
            "help": "limit on total amount of like-actions during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "likes_all_time_limit": {
            "help": "limit on total amount of like-actions from the account first usage by the bot,"
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    likes_hourly_limit = None
    likes_daily_limit = None
    likes_all_time_limit = None

    def set_limit_values(self, args):
        if args.likes_hourly_limit is not None:
            self.likes_hourly_limit = get_value(args.likes_hourly_limit, "Likes hourly-limit: {}", 50)

        if args.likes_daily_limit is not None:
            self.likes_daily_limit = get_value(args.likes_daily_limit, "Likes daily-limit: {}", 300)

        if args.likes_all_time_limit is not None:
            self.likes_all_time_limit = get_value(args.likes_all_time_limit, "Likes total-limit: {}", 5000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == LikeAction:
            return False

        if self.likes_hourly_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=LikeAction, hours=1) >= self.likes_hourly_limit:
                print_ui(COLOR_OKBLUE + f"Likes hourly-limit has been reached (total: {self.likes_hourly_limit})." + COLOR_ENDC)
                return True

        if self.likes_daily_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=LikeAction, hours=24) >= self.likes_daily_limit:
                print_ui(COLOR_OKBLUE + f"Likes daily-limit has been reached (total: {self.likes_daily_limit})." + COLOR_ENDC)
                return True

        if self.likes_all_time_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=LikeAction, hours=None) >= self.likes_all_time_limit:
                print_ui(COLOR_OKBLUE + f"Likes total-limit has been reached (total: {self.likes_all_time_limit})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.likes_hourly_limit = None
        self.likes_daily_limit = None
        self.likes_all_time_limit = None

    def update_state(self, action):
        pass


class FollowTimedLimit(ExtraLimit):
    LIMIT_ID = "follow_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "follow_hourly_limit": {
            "help": "limit on total amount of follow-actions during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "follow_daily_limit": {
            "help": "limit on total amount of follow-actions during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "follow_all_time_limit": {
            "help": "limit on total amount of follow-actions from the account first usage by the bot,"
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    follow_hourly_limit = None
    follow_daily_limit = None
    follow_all_time_limit = None

    def set_limit_values(self, args):
        if args.follow_hourly_limit is not None:
            self.follow_hourly_limit = get_value(args.follow_hourly_limit, "Follow hourly-limit: {}", 50)

        if args.follow_daily_limit is not None:
            self.follow_daily_limit = get_value(args.follow_daily_limit, "Follow daily-limit: {}", 300)

        if args.follow_all_time_limit is not None:
            self.follow_all_time_limit = get_value(args.follow_all_time_limit, "Follow total-limit: {}", 5000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == FollowAction:
            return False

        if self.follow_hourly_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=FollowAction, hours=1) >= self.follow_hourly_limit:
                print_ui(COLOR_OKBLUE + f"Follow hourly-limit has been reached (total: {self.follow_hourly_limit})." + COLOR_ENDC)
                return True

        if self.follow_daily_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=FollowAction, hours=24) >= self.follow_daily_limit:
                print_ui(COLOR_OKBLUE + f"Follow daily-limit has been reached (total: {self.follow_daily_limit})." + COLOR_ENDC)
                return True

        if self.follow_all_time_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=FollowAction, hours=None) >= self.follow_all_time_limit:
                print_ui(COLOR_OKBLUE + f"Follow total-limit has been reached (total: {self.follow_all_time_limit})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.follow_hourly_limit = None
        self.follow_daily_limit = None
        self.follow_all_time_limit = None

    def update_state(self, action):
        pass


class StoryWatchTimedLimit(ExtraLimit):
    LIMIT_ID = "story_watch_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "story_hourly_limit": {
            "help": "limit on total amount of story-watch-actions during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "story_daily_limit": {
            "help": "limit on total amount of story-watch-actions during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "story_all_time_limit": {
            "help": "limit on total amount of story-watch-actions from the account first usage by the bot,"
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    story_hourly_limit = None
    story_daily_limit = None
    story_all_time_limit = None

    def set_limit_values(self, args):
        if args.story_hourly_limit is not None:
            self.story_hourly_limit = get_value(args.story_hourly_limit, "Story-watch hourly-limit: {}", 50)

        if args.story_daily_limit is not None:
            self.story_daily_limit = get_value(args.story_daily_limit, "Story-watch daily-limit: {}", 300)

        if args.story_all_time_limit is not None:
            self.story_all_time_limit = get_value(args.story_all_time_limit, "Story-watch total-limit: {}", 5000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == StoryWatchAction:
            return False

        if self.story_hourly_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=StoryWatchAction, hours=1) >= self.story_hourly_limit:
                print_ui(COLOR_OKBLUE + f"Story-watch hourly-limit has been reached (total: {self.story_hourly_limit})." + COLOR_ENDC)
                return True

        if self.story_daily_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=StoryWatchAction, hours=24) >= self.story_daily_limit:
                print_ui(COLOR_OKBLUE + f"Story-watch daily-limit has been reached (total: {self.story_daily_limit})." + COLOR_ENDC)
                return True

        if self.story_all_time_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=StoryWatchAction, hours=None) >= self.story_all_time_limit:
                print_ui(COLOR_OKBLUE + f"Story-watch total-limit has been reached (total: {self.story_all_time_limit})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.story_hourly_limit = None
        self.story_daily_limit = None
        self.story_all_time_limit = None

    def update_state(self, action):
        pass


class CommentTimedLimit(ExtraLimit):
    LIMIT_ID = "comment_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "comment_hourly_limit": {
            "help": "limit on total amount of comment-actions during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "comment_daily_limit": {
            "help": "limit on total amount of comment-actions during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "comment_all_time_limit": {
            "help": "limit on total amount of comment-actions from the account first usage by the bot,"
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    comment_hourly_limit = None
    comment_daily_limit = None
    comment_all_time_limit = None

    def set_limit_values(self, args):
        if args.comment_hourly_limit is not None:
            self.comment_hourly_limit = get_value(args.comment_hourly_limit, "Comment hourly-limit: {}", 50)

        if args.comment_daily_limit is not None:
            self.comment_daily_limit = get_value(args.comment_daily_limit, "Comment daily-limit: {}", 300)

        if args.comment_all_time_limit is not None:
            self.comment_all_time_limit = get_value(args.comment_all_time_limit, "Comment total-limit: {}", 5000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == CommentAction:
            return False

        if self.comment_hourly_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=CommentAction, hours=1) >= self.comment_hourly_limit:
                print_ui(COLOR_OKBLUE + f"Comment hourly-limit has been reached (total: {self.comment_hourly_limit})." + COLOR_ENDC)
                return True

        if self.comment_daily_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=CommentAction, hours=24) >= self.comment_daily_limit:
                print_ui(COLOR_OKBLUE + f"Comment daily-limit has been reached (total: {self.comment_daily_limit})." + COLOR_ENDC)
                return True

        if self.comment_all_time_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=CommentAction, hours=None) >= self.comment_all_time_limit:
                print_ui(COLOR_OKBLUE + f"Comment total-limit has been reached (total: {self.comment_all_time_limit})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.comment_hourly_limit = None
        self.comment_daily_limit = None
        self.comment_all_time_limit = None

    def update_state(self, action):
        pass


class UnfollowTimedLimit(ExtraLimit):
    LIMIT_ID = "unfollow_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "unfollow_hourly_limit": {
            "help": "limit on total amount of unfollow-actions during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "unfollow_daily_limit": {
            "help": "limit on total amount of unfollow-actions during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "unfollow_all_time_limit": {
            "help": "limit on total amount of unfollow-actions from the account first usage by the bot,"
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    unfollow_hourly_limit = None
    unfollow_daily_limit = None
    unfollow_all_time_limit = None

    def set_limit_values(self, args):
        if args.unfollow_hourly_limit is not None:
            self.unfollow_hourly_limit = get_value(args.unfollow_hourly_limit, "Unfollow hourly-limit: {}", 50)

        if args.unfollow_daily_limit is not None:
            self.unfollow_daily_limit = get_value(args.unfollow_daily_limit, "Unfollow daily-limit: {}", 300)

        if args.unfollow_all_time_limit is not None:
            self.unfollow_all_time_limit = get_value(args.unfollow_all_time_limit, "Unfollow total-limit: {}", 5000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == UnfollowAction:
            return False

        if self.unfollow_hourly_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=UnfollowAction, hours=1) >= self.unfollow_hourly_limit:
                print_ui(COLOR_OKBLUE + f"Unfollow hourly-limit has been reached (total: {self.unfollow_hourly_limit})." + COLOR_ENDC)
                return True

        if self.unfollow_daily_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=UnfollowAction, hours=24) >= self.unfollow_daily_limit:
                print_ui(COLOR_OKBLUE + f"Unfollow daily-limit has been reached (total: {self.unfollow_daily_limit})." + COLOR_ENDC)
                return True

        if self.unfollow_all_time_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=UnfollowAction, hours=None) >= self.unfollow_all_time_limit:
                print_ui(COLOR_OKBLUE + f"Unfollow total-limit has been reached (total: {self.unfollow_all_time_limit})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.unfollow_hourly_limit = None
        self.unfollow_daily_limit = None
        self.unfollow_all_time_limit = None

    def update_state(self, action):
        pass


class DirectMessagesLimit(ExtraLimit):
    LIMIT_ID = "direct_messages_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "direct_messages_session_limit": {
            "help": "limit on total amount of DMs-actions during the current session, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    direct_messages_config_limit = None
    direct_messages_session_limit = None

    def set_limit_values(self, args):
        if args.dm_to_new_followers is not None:
            self.direct_messages_config_limit = get_value(args.dm_to_new_followers, "DM to {} new followers", 2)

        if args.direct_messages_session_limit is not None:
            self.direct_messages_session_limit = get_value(args.direct_messages_session_limit, "DM session limit: {}", 2)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == DirectMessageAction:
            return False

        if self.direct_messages_config_limit is not None:
            if session_state.totalDirectMessages >= self.direct_messages_config_limit:
                return True

        if self.direct_messages_session_limit is not None:
            if session_state.totalDirectMessages >= self.direct_messages_session_limit:
                return True

        return False

    def reset(self):
        self.direct_messages_limit = None

    def update_state(self, action):
        pass


class DirectMessagesTimedLimit(ExtraLimit):
    LIMIT_ID = "direct_messages_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "direct_messages_hourly_limit": {
            "help": "limit on total amount of direct_messages-actions during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "direct_messages_daily_limit": {
            "help": "limit on total amount of direct_messages-actions during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "direct_messages_all_time_limit": {
            "help": "limit on total amount of direct_messages-actions from the account first usage by the bot,"
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    direct_messages_hourly_limit = None
    direct_messages_daily_limit = None
    direct_messages_all_time_limit = None

    def set_limit_values(self, args):
        if args.direct_messages_hourly_limit is not None:
            self.direct_messages_hourly_limit = get_value(args.direct_messages_hourly_limit, "DMs hourly-limit: {}", 5)

        if args.direct_messages_daily_limit is not None:
            self.direct_messages_daily_limit = get_value(args.direct_messages_daily_limit, "DMs daily-limit: {}", 50)

        if args.direct_messages_all_time_limit is not None:
            self.direct_messages_all_time_limit = get_value(args.direct_messages_all_time_limit, "DMs total-limit: {}", 5000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == DirectMessageAction:
            return False

        if self.direct_messages_hourly_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=DirectMessageAction, hours=1) >= self.direct_messages_hourly_limit:
                print_ui(COLOR_OKBLUE + f"DMs hourly-limit has been reached (total: {self.direct_messages_hourly_limit})." + COLOR_ENDC)
                return True

        if self.direct_messages_daily_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=DirectMessageAction, hours=24) >= self.direct_messages_daily_limit:
                print_ui(COLOR_OKBLUE + f"DMs daily-limit has been reached (total: {self.direct_messages_daily_limit})." + COLOR_ENDC)
                return True

        if self.direct_messages_all_time_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=DirectMessageAction, hours=None) >= self.direct_messages_all_time_limit:
                print_ui(COLOR_OKBLUE + f"DMs total-limit has been reached (total: {self.direct_messages_all_time_limit})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.direct_messages_hourly_limit = None
        self.direct_messages_daily_limit = None
        self.direct_messages_all_time_limit = None

    def update_state(self, action):
        pass


class GetProfileTimedLimit(ExtraLimit):
    LIMIT_ID = "get_profile_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "get_profile_hourly_limit": {
            "help": "limit on total amount of get_profile-actions during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "get_profile_daily_limit": {
            "help": "limit on total amount of get_profile-actions during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "get_profile_all_time_limit": {
            "help": "limit on total amount of get_profile-actions from the account first usage by the bot,"
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    get_profile_hourly_limit = None
    get_profile_daily_limit = None
    get_profile_all_time_limit = None

    def set_limit_values(self, args):
        if args.get_profile_hourly_limit is not None:
            self.get_profile_hourly_limit = get_value(args.get_profile_hourly_limit, "Get-profile hourly-limit: {}", 50)

        if args.get_profile_daily_limit is not None:
            self.get_profile_daily_limit = get_value(args.get_profile_daily_limit, "Get-profile daily-limit: {}", 300)

        if args.get_profile_all_time_limit is not None:
            self.get_profile_all_time_limit = get_value(args.get_profile_all_time_limit, "Get-profile total-limit: {}", 5000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == GetProfileAction:
            return False

        if self.get_profile_hourly_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=GetProfileAction, hours=1) >= self.get_profile_hourly_limit:
                print_ui(COLOR_OKBLUE + f"Get-profile hourly-limit has been reached (total: {self.get_profile_hourly_limit})." + COLOR_ENDC)
                return True

        if self.get_profile_daily_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=GetProfileAction, hours=24) >= self.get_profile_daily_limit:
                print_ui(COLOR_OKBLUE + f"Get-profile daily-limit has been reached (total: {self.get_profile_daily_limit})." + COLOR_ENDC)
                return True

        if self.get_profile_all_time_limit is not None:
            if session_state.storage.get_actions_count_within_hours(action_type=GetProfileAction, hours=None) >= self.get_profile_all_time_limit:
                print_ui(COLOR_OKBLUE + f"Get-profile total-limit has been reached (total: {self.get_profile_all_time_limit})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.get_profile_hourly_limit = None
        self.get_profile_daily_limit = None
        self.get_profile_all_time_limit = None

    def update_state(self, action):
        pass


class SessionTimeTimedLimit(ExtraLimit):
    LIMIT_ID = "session_time_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "single_session_time_limit": {
            "help": "limit on total amount of session-time (minutes) during the current session, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "session_time_hourly_limit": {
            "help": "limit on total amount of session-time (minutes) during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "session_time_daily_limit": {
            "help": "limit on total amount of session-time (minutes) during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "session_time_all_time_limit": {
            "help": "limit on total amount of session-time (minutes) all time, disabled by default. "
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    single_session_time_limit = None
    session_time_hourly_limit = None
    session_time_daily_limit = None
    session_time_all_time_limit = None

    def set_limit_values(self, args):
        if args.single_session_time_limit is not None:
            self.single_session_time_limit = get_value(args.single_session_time_limit, "Current session-time limit: {}", 60)

        if args.session_time_hourly_limit is not None:
            self.session_time_hourly_limit = get_value(args.session_time_hourly_limit, "Session-time hourly-limit: {}", 60*4)

        if args.session_time_daily_limit is not None:
            self.session_time_daily_limit = get_value(args.session_time_daily_limit, "Session-time daily-limit: {}", 60*4*7)

        if args.session_time_all_time_limit is not None:
            self.session_time_all_time_limit = get_value(args.session_time_all_time_limit, "Session-time total-limit: {}", 60*4*7*365)

    def is_reached_for_action(self, action, session_state):
        # Apply this limit for every action (no action-type condition)

        # Current session time wont be fetched from database, so calculating manually
        curr_session_time_mins = 0
        if session_state.is_started():
            delta = datetime.now() - session_state.startTime
            curr_session_time_mins = int(delta.total_seconds() // 60)

        if self.single_session_time_limit is not None:
            if curr_session_time_mins >= self.single_session_time_limit:
                print_ui(COLOR_OKBLUE + f"Session time limit has been reached (total: {curr_session_time_mins})." + COLOR_ENDC)
                return True

        if self.session_time_hourly_limit is not None:
            last_hour_session_time_mins = int(session_state.storage.get_session_time_in_seconds_within_minutes(minutes=60) // 60) + curr_session_time_mins
            if last_hour_session_time_mins >= self.session_time_hourly_limit:
                print_ui(COLOR_OKBLUE + f"Session time hourly-limit has been reached (total: {last_hour_session_time_mins})." + COLOR_ENDC)
                return True

        if self.session_time_daily_limit is not None:
            last_day_session_time_mins = int(session_state.storage.get_session_time_in_seconds_within_minutes(minutes=60*24) // 60) + curr_session_time_mins
            if last_day_session_time_mins >= self.session_time_daily_limit:
                print_ui(COLOR_OKBLUE + f"Session time daily-limit has been reached (total: {last_day_session_time_mins})." + COLOR_ENDC)
                return True

        if self.session_time_all_time_limit is not None:
            all_time_session_time_mins = int(session_state.storage.get_session_time_in_seconds_within_minutes(minutes=None) // 60) + curr_session_time_mins
            if all_time_session_time_mins >= self.session_time_all_time_limit:
                print_ui(COLOR_OKBLUE + f"Session time total-limit has been reached (total: {all_time_session_time_mins})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.single_session_time_limit = None
        self.session_time_hourly_limit = None
        self.session_time_daily_limit = None
        self.session_time_all_time_limit = None

    def update_state(self, action):
        pass


class SessionCountTimedLimit(ExtraLimit):
    LIMIT_ID = "session_count_timed_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "session_count_hourly_limit": {
            "help": "limit on total amount of sessions during the last hour, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "session_count_daily_limit": {
            "help": "limit on total amount of sessions during the last 24 hours, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        },
        "session_count_all_time_limit": {
            "help": "limit on total amount of sessions from the account first usage by the bot,"
                    " disabled by default. It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    session_count_hourly_limit = None
    session_count_daily_limit = None
    session_count_all_time_limit = None

    def set_limit_values(self, args):
        if args.session_count_hourly_limit is not None:
            self.session_count_hourly_limit = get_value(args.session_count_hourly_limit, "Sessions-count hourly-limit: {}", 2)

        if args.session_count_daily_limit is not None:
            self.session_count_daily_limit = get_value(args.session_count_daily_limit, "Sessions-count daily-limit: {}", 5)

        if args.session_count_all_time_limit is not None:
            self.session_count_all_time_limit = get_value(args.session_count_all_time_limit, "Sessions-count total-limit: {}", 5000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == StartSessionAction:
            return False

        if self.session_count_hourly_limit is not None:
            if session_state.storage.get_sessions_count_within_hours(hours=1) >= self.session_count_hourly_limit:
                print_ui(COLOR_OKBLUE + f"Session-count hourly-limit has been reached (total: {self.session_count_hourly_limit})." + COLOR_ENDC)
                return True

        if self.session_count_daily_limit is not None:
            if session_state.storage.get_sessions_count_within_hours(hours=24) >= self.session_count_daily_limit:
                print_ui(COLOR_OKBLUE + f"Session-count daily-limit has been reached (total: {self.session_count_daily_limit})." + COLOR_ENDC)
                return True

        if self.session_count_all_time_limit is not None:
            if session_state.storage.get_sessions_count_within_hours(hours=None) >= self.session_count_all_time_limit:
                print_ui(COLOR_OKBLUE + f"Session-count total-limit has been reached (total: {self.session_count_all_time_limit})." + COLOR_ENDC)
                return True

        return False

    def reset(self):
        self.session_count_hourly_limit = None
        self.session_count_daily_limit = None
        self.session_count_all_time_limit = None

    def update_state(self, action):
        pass


def get_extra_limits_classes():
    return ExtraLimit.__subclasses__()
