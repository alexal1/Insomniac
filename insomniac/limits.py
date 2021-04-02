from abc import ABC
from enum import unique, Enum

from insomniac.action_runners.actions_runners_manager import ActionState
from insomniac.actions_types import LikeAction, InteractAction, FollowAction, UnfollowAction, StoryWatchAction, \
    GetProfileAction, CommentAction
from insomniac.utils import *


@unique
class LimitType(Enum):
    SESSION = 0
    SOURCE = 1


class LimitsManager(object):
    """This class manages the actions-limits of an insomniac-session"""

    limits = {
        str(LimitType.SOURCE): {},
        str(LimitType.SESSION): {}
    }

    def __init__(self):
        for clazz in get_core_limits_classes():
            instance = clazz()
            self.limits[str(instance.LIMIT_TYPE)][instance.LIMIT_ID] = instance

    def get_limits_args(self):
        limit_args = {}

        for limits_type, limits in self.limits.items():
            for limit_id, limit in limits.items():
                for arg, info in limit.LIMIT_ARGS.items():
                    limit_args.update({arg: info})

        return limit_args

    def set_limits(self, args):
        for limits_type, limits in self.limits.items():
            for limit_id, limit in limits.items():
                limit.set_limit(args)

    def update_state(self, action):
        for limits_type, limits in self.limits.items():
            for limit_id, limit in limits.items():
                limit.update_state(action)

    def is_limit_reached_for_action(self, action, session_state):
        """
        :return: three values: whether limit was reached,
        LIMIT_ID of source limit if the reached limit is LimitType.SOURCE or None otherwise,
        LIMIT_ID of session limit if the reached limit is LimitType.SESSION or None otherwise
        """

        reached_source_limit = None
        reached_session_limit = None
        is_limit_reached = False

        for limit_id, limit in self.limits[str(LimitType.SOURCE)].items():
            if limit.is_reached_for_action(action, session_state):
                reached_source_limit = limit.LIMIT_ID
                is_limit_reached = True
                break

        for limit_id, limit in self.limits[str(LimitType.SESSION)].items():
            if limit.is_reached_for_action(action, session_state):
                reached_session_limit = limit.LIMIT_ID
                is_limit_reached = True
                break

        return is_limit_reached, reached_source_limit, reached_session_limit


class Limit(object):
    """An interface for limit object"""

    LIMIT_ID = "OVERRIDE"
    LIMIT_TYPE = "OVERRIDE"
    LIMIT_ARGS = {"OVERRIDE": "OVERRIDE"}

    def set_limit(self, args):
        raise NotImplementedError()

    def update_state(self, action):
        raise NotImplementedError()

    def is_reached_for_action(self, action, session_state):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()


class CoreLimit(Limit, ABC):
    """An interface for extra-limit object"""


class TotalLikesLimit(CoreLimit):
    LIMIT_ID = "total_likes_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "total_likes_limit": {
            "help": "limit on total amount of likes during the session, 300 by default. "
                    "It can be a number presenting specific limit (e.g. 300) or a range (e.g. 100-120)",
            "metavar": "300",
            "default": "1000"
        }
    }

    total_likes_limit = 1000

    def set_limit(self, args):
        if args.total_likes_limit is not None:
            self.total_likes_limit = get_value(args.total_likes_limit, "Total likes limit: {}", 1000)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == LikeAction:
            return False

        return session_state.totalLikes >= self.total_likes_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class TotalInteractionsLimit(CoreLimit):
    LIMIT_ID = "total_interactions_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "total_interactions_limit": {
            "help": "number of total interactions (successful & unsuccessful) per session, disabled by default. "
                    "It can be a number (e.g. 70) or a range (e.g. 60-80)",
            "metavar": '60-80'
        }
    }

    total_interactions_limit = None

    def set_limit(self, args):
        if args.total_interactions_limit is not None:
            self.total_interactions_limit = get_value(args.total_interactions_limit, "Total interactions limit: {}", 1000)

    def is_reached_for_action(self, action, session_state):
        if self.total_interactions_limit is None:
            return False

        if not type(action) == InteractAction:
            return False

        return sum(session_state.totalInteractions.values()) >= self.total_interactions_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class TotalSuccessfulInteractionsLimit(CoreLimit):
    LIMIT_ID = "total_successful_interactions_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "total_successful_interactions_limit": {
            "help": "number of total successful interactions per session, disabled by default. "
                    "It can be a number (e.g. 70) or a range (e.g. 60-80)",
            "metavar": '60-80'
        }
    }

    total_successful_interactions_limit = None

    def set_limit(self, args):
        if args.total_successful_interactions_limit is not None:
            self.total_successful_interactions_limit = get_value(args.total_successful_interactions_limit,
                                                                 "Total successful-interactions limit: {}", 1000)

    def is_reached_for_action(self, action, session_state):
        if self.total_successful_interactions_limit is None:
            return False

        if not type(action) == InteractAction:
            return False

        return sum(session_state.successfulInteractions.values()) >= self.total_successful_interactions_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class TotalFollowLimit(CoreLimit):
    LIMIT_ID = "total_follow_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "total_follow_limit": {
            "help": "limit on total amount of follows during the session, disabled by default. "
                    "It can be a number (e.g. 27) or a range (e.g. 20-30)",
            "metavar": "50"
        }
    }

    total_follow_limit = None

    def set_limit(self, args):
        if args.total_follow_limit is not None:
            self.total_follow_limit = get_value(args.total_follow_limit, "Total follow limit: {}", 70)

    def is_reached_for_action(self, action, session_state):
        if self.total_follow_limit is None:
            return False
        
        if not type(action) == FollowAction:
            return False

        return sum(session_state.totalFollowed.values()) >= self.total_follow_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class TotalStoryWatchLimit(CoreLimit):
    LIMIT_ID = "total_story_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "total_story_limit": {
            "help": "limit on total amount of stories watches during the session, disabled by default. "
                    "It can be a number (e.g. 27) or a range (e.g. 20-30)",
            "metavar": "300",
        }
    }

    total_story_limit = None

    def set_limit(self, args):
        if args.total_story_limit is not None:
            self.total_story_limit = get_value(args.total_story_limit, "Total story-watches limit: {}", 1000)

    def is_reached_for_action(self, action, session_state):
        if self.total_story_limit is None:
            return False
        
        if not type(action) == StoryWatchAction:
            return False

        return session_state.totalStoriesWatched >= self.total_story_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class TotalCommentsLimit(CoreLimit):
    LIMIT_ID = "total_comments_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "total_comments_limit": {
            "help": "limit on total amount of comments during the session, 50 by default. "
                    "It can be a number presenting specific limit (e.g. 300) or a range (e.g. 100-120)",
            "metavar": "300",
            "default": "50"
        }
    }

    total_comments_limit = 50

    def set_limit(self, args):
        if args.total_comments_limit is not None:
            self.total_comments_limit = get_value(args.total_comments_limit, "Total comments limit: {}", 50)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == CommentAction:
            return False

        return session_state.totalComments >= self.total_comments_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class SourceInteractionsLimit(CoreLimit):
    LIMIT_ID = "interactions_count"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "interactions_count": {
            "help": "Deprecated - use 'successful_interactions_limit_per_source' instead",
            "metavar": "40"
        }
    }

    interactions_count = 70

    def set_limit(self, args):
        if args.interactions_count is not None:
            print(COLOR_REPORT + "You are using a deprecated limit. The limit new name is called "
                                 "'successful_interactions_limit_per_source'. Using interactions_count this time. "
                                 "Please switch to that name on next runs." + COLOR_ENDC)
            self.interactions_count = get_value(args.interactions_count, "Interactions count: {}", 70)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == InteractAction:
            return False

        successful_interactions_count = session_state.successfulInteractions.get(action.source_name)

        return successful_interactions_count and successful_interactions_count >= self.interactions_count

    def reset(self):
        pass

    def update_state(self, action):
        pass


class SuccessfulInteractionsLimitPerSource(CoreLimit):
    LIMIT_ID = "successful_interactions_limit_per_source"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "successful_interactions_limit_per_source": {
            "help": "number of successful-interactions per each blogger/hashtag, 70 by default. "
                    "It can be a number (e.g. 70) or a range (e.g. 60-80)",
            "metavar": "40",
            "default": "70"
        }
    }

    successful_interactions_limit_per_source = 70

    def set_limit(self, args):
        if args.successful_interactions_limit_per_source is not None:
            self.successful_interactions_limit_per_source = get_value(args.successful_interactions_limit_per_source,
                                                                      "Successful interactions limit per source: {}", 70)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == InteractAction:
            return False

        successful_interactions_count = session_state.successfulInteractions.get(action.source_name)

        return successful_interactions_count and successful_interactions_count >= self.successful_interactions_limit_per_source

    def reset(self):
        pass

    def update_state(self, action):
        pass


class InteractionsLimitPerSource(CoreLimit):
    LIMIT_ID = "interactions_limit_per_source"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "interactions_limit_per_source": {
            "help": "number of interactions (successful & non-successful) per each blogger/hashtag, 140 by default. "
                    "It can be a number (e.g. 140) or a range (e.g. 60-80)",
            "metavar": "40",
            "default": "140"
        }
    }

    interactions_limit_per_source = 140

    def set_limit(self, args):
        if args.interactions_limit_per_source is not None:
            self.interactions_limit_per_source = get_value(args.interactions_limit_per_source,
                                                           "Interactions limit per source: {}", 140)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == InteractAction:
            return False

        interactions_count = session_state.totalInteractions.get(action.source_name)

        return interactions_count and interactions_count >= self.interactions_limit_per_source

    def reset(self):
        pass

    def update_state(self, action):
        pass


class SourceFollowLimit(CoreLimit):
    LIMIT_ID = "follow_limit"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "follow_limit": {
            "help": "Deprecated - use 'follow_limit_per_source' instead",
            "metavar": "7-8",
        }
    }

    follow_limit = None

    def set_limit(self, args):
        if args.follow_limit is not None:
            print(COLOR_REPORT + "You are using a deprecated limit. The limit new name is called "
                                 "'follow_limit_per_source'. Using 'follow_limit' this time. "
                                 "Please switch to that name on next runs." + COLOR_ENDC)
            self.follow_limit = get_value(args.follow_limit, "Follow limit: {}", 10)

    def is_reached_for_action(self, action, session_state):
        if self.follow_limit is None:
            return False

        if not type(action) == FollowAction:
            return False

        followed_count = session_state.totalFollowed.get(action.source_name)
        return followed_count is not None and followed_count >= self.follow_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class FollowLimitPerSource(CoreLimit):
    LIMIT_ID = "follow_limit_per_source"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "follow_limit_per_source": {
            "help": "limit on amount of follows during interaction with each one user's followers, "
                    "disabled by default. It can be a number (e.g. 10) or a range (e.g. 6-9)",
            "metavar": "7-8",
        }
    }

    follow_limit_per_source = None

    def set_limit(self, args):
        if args.follow_limit_per_source is not None:
            self.follow_limit_per_source = get_value(args.follow_limit_per_source, "Follow limit: {}", 10)

    def is_reached_for_action(self, action, session_state):
        if self.follow_limit_per_source is None:
            return False

        if not type(action) == FollowAction:
            return False

        followed_count = session_state.totalFollowed.get(action.source_name)
        return followed_count is not None and followed_count >= self.follow_limit_per_source

    def reset(self):
        pass

    def update_state(self, action):
        pass


class UnfollowingLimit(CoreLimit):
    LIMIT_ID = "unfollowing_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {}

    unfollow_limit = None

    def set_limit(self, args):
        if args.unfollow is not None:
            self.unfollow_limit = get_value(args.unfollow, "Unfollow: {}", 100)

    def is_reached_for_action(self, action, session_state):
        if self.unfollow_limit is None:
            return False

        if not type(action) == UnfollowAction:
            return False

        return session_state.totalUnfollowed >= self.unfollow_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class MinFollowing(CoreLimit):
    LIMIT_ID = "min_following"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "min_following": {
            "help": 'minimum amount of followings, after reaching this amount unfollow stops',
            "metavar": '100',
            "default": "0"
        }
    }

    min_following_limit = 0

    def set_limit(self, args):
        self.min_following_limit = int(args.min_following)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == UnfollowAction:
            return False

        initial_following = session_state.my_following_count
        unfollowed_count = session_state.totalUnfollowed

        return initial_following - unfollowed_count <= self.min_following_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class MaxFollowing(CoreLimit):
    LIMIT_ID = "max_following"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "max_following": {
            "help": 'maximum amount of followings, after reaching this amount follow stops. disabled by default',
            "metavar": '100'
        }
    }

    max_following_limit = None

    def set_limit(self, args):
        if args.max_following is not None:
            self.max_following_limit = int(args.max_following)

    def is_reached_for_action(self, action, session_state):
        if self.max_following_limit is None:
            return False

        if not type(action) == FollowAction:
            return False

        initial_following = session_state.my_following_count
        followed_count = sum(session_state.totalFollowed.values())

        return initial_following + followed_count >= self.max_following_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class TotalGetProfileLimit(CoreLimit):
    LIMIT_ID = "total_get_profile_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "total_get_profile_limit": {
            "help": "limit on total amount of get-profile actions during the session, disabled by default. "
                    "It can be a number (e.g. 600) or a range (e.g. 500-700)",
            "metavar": "1500"
        }
    }

    total_get_profile_limit = None

    def set_limit(self, args):
        if args.total_get_profile_limit is not None:
            self.total_get_profile_limit = get_value(args.total_get_profile_limit, "Total get-profile limit: {}", 1000)

    def is_reached_for_action(self, action, session_state):
        if self.total_get_profile_limit is None:
            return False

        if not type(action) == GetProfileAction:
            return False

        return session_state.totalGetProfile >= self.total_get_profile_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class SessionTimeMaxLengthLimit(CoreLimit):
    LIMIT_ID = "session_length_in_mins_limit"
    LIMIT_TYPE = LimitType.SESSION
    LIMIT_ARGS = {
        "session_length_in_mins_limit": {
            "help": "limit the session length by time (minutes), disabled by default. "
                    "It can be a number (e.g. 60) or a range (e.g. 40-70)",
            "metavar": "50-60"
        }
    }

    session_length_in_mins_limit = None

    def set_limit(self, args):
        if args.session_length_in_mins_limit is not None:
            self.session_length_in_mins_limit = get_value(args.session_length_in_mins_limit, "Session max-length (minutes): {}", 60)

    def is_reached_for_action(self, action, session_state):
        if self.session_length_in_mins_limit is None:
            return False

        # Apply this limit for every action (no action-type condition)

        delta = datetime.now() - session_state.startTime
        mins_delta = delta.seconds // 60

        return mins_delta > self.session_length_in_mins_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


def get_core_limits_classes():
    return CoreLimit.__subclasses__()


def process_limits(is_limit_reached, reached_session_limit, reached_source_limit, action_status, limit_display_name):
    if is_limit_reached:
        # Reached session limit, stop the action
        if reached_session_limit is not None:
            print(COLOR_OKBLUE + "{0} session-limit {1} has been reached. Stopping activity."
                  .format(limit_display_name, reached_session_limit) + COLOR_ENDC)
            action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)
        else:
            print(COLOR_OKBLUE + "{0} source-limit {1} has been reached. Moving to next source."
                  .format(limit_display_name, reached_source_limit) + COLOR_ENDC)
            action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)

        return False

    return True
