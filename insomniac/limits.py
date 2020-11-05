from abc import ABC
from enum import unique, Enum

from insomniac.actions_types import LikeAction, InteractAction, FollowAction
from insomniac.utils import get_value, COLOR_WARNING, COLOR_ENDC


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
        reached_source_limit = None
        reached_session_limit = None
        is_limit_reached = False

        for limit_id, limit in self.limits[str(LimitType.SOURCE)].items():
            if limit.is_reached_for_action(action, session_state):
                reached_source_limit = limit.LIMIT_ID
                is_limit_reached = True
                print(COLOR_WARNING + "Reached source-limit {} for action type {} ".format(reached_source_limit, type(action).__name__) + COLOR_ENDC)
                break

        for limit_id, limit in self.limits[str(LimitType.SESSION)].items():
            if limit.is_reached_for_action(action, session_state):
                reached_session_limit = limit.LIMIT_ID
                is_limit_reached = True
                print(COLOR_WARNING + "Reached session-limit {} for action type {} ".format(reached_session_limit, type(action).__name__) + COLOR_ENDC)
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
            "help": "number of total interactions per session, disabled by default. "
                    "It can be a number (e.g. 70) or a range (e.g. 60-80). "
                    "Only successful interactions count",
            "metavar": '60-80'
        }
    }

    total_interactions_limit = None

    is_reached = False

    def set_limit(self, args):
        if args.total_interactions_limit is not None:
            self.total_interactions_limit = get_value(args.total_interactions_limit, "Total interactions limit: {}", 1000)

    def is_reached_for_action(self, action, session_state):
        if self.total_interactions_limit is None:
            return False

        if not type(action) == InteractAction:
            return False

        return sum(session_state.successfulInteractions.values()) >= self.total_interactions_limit

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

    is_reached = False

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


class SourceInteractionsLimit(CoreLimit):
    LIMIT_ID = "interactions_count"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "interactions_count": {
            "help": "number of interactions per each blogger/hashtag, 70 by default. "
                    "It can be a number (e.g. 70) or a range (e.g. 60-80). "
                    "Only successful interactions count",
            "metavar": "40",
            "default": "70"
        }
    }

    interactions_count = 70

    def set_limit(self, args):
        if args.interactions_count is not None:
            self.interactions_count = get_value(args.interactions_count, "Interactions count: {}", 70)

    def is_reached_for_action(self, action, session_state):
        if not type(action) == InteractAction:
            return False

        successful_interactions_count = session_state.successfulInteractions.get(action.source)

        return successful_interactions_count and successful_interactions_count >= self.interactions_count

    def reset(self):
        pass

    def update_state(self, action):
        pass


class SourceFollowLimit(CoreLimit):
    LIMIT_ID = "follow_limit"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "follow_limit": {
            "help": "limit on amount of follows during interaction with each one user's followers, "
                    "disabled by default. It can be a number (e.g. 10) or a range (e.g. 6-9)",
            "metavar": "7-8",
        }
    }

    follow_limit = None

    def set_limit(self, args):
        if args.follow_limit is not None:
            self.follow_limit = get_value(args.interactions_count, "Follow limit: {}", 10)

    def is_reached_for_action(self, action, session_state):
        if self.follow_limit is None:
            return False

        if not type(action) == FollowAction:
            return False

        followed_count = session_state.totalFollowed.get(action.source)
        return followed_count is not None and followed_count >= self.follow_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


def get_core_limits_classes():
    return CoreLimit.__subclasses__()
