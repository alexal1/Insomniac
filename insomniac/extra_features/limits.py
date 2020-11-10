from abc import ABC

from insomniac.actions_types import ScrapeAction, GetProfileAction
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
            "help": "limit on total amount of profiles-scrapping during the session, disabled by default. "
                    "It can be a number (e.g. 100) or a range (e.g. 90-120)",
            "metavar": "150"
        }
    }

    total_scrape_limit = None

    def set_limit(self, args):
        if args.total_scrape_limit is not None:
            self.total_scrape_limit = get_value(args.interactions_count, "Total scrape limit: {}", 100)

    def is_reached_for_action(self, action, session_state):
        if self.total_scrape_limit is None:
            return False

        if not type(action) == ScrapeAction:
            return False

        return sum(session_state.totalScraped.values()) >= self.total_scrape_limit

    def reset(self):
        pass

    def update_state(self, action):
        pass


class TotalGetProfileLimit(ExtraLimit):
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
            self.total_get_profile_limit = get_value(args.total_get_profile_limit, "Total get-profile limit: {}", 100)

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


class SourceScrapeLimit(ExtraLimit):
    LIMIT_ID = "scrape_count"
    LIMIT_TYPE = LimitType.SOURCE
    LIMIT_ARGS = {
        "scrape_count": {
            "help": "number of profiles-scrapping per each blogger/hashtag, disabled by default. "
                    "It can be a number (e.g. 70) or a range (e.g. 50-80)",
            "metavar": "40-60"
        }
    }

    scrape_count = None

    def set_limit(self, args):
        if args.scrape_count is not None:
            self.scrape_count = get_value(args.scrape_count, "Scrape count limit: {}", 20)

    def is_reached_for_action(self, action, session_state):
        if self.scrape_count is None:
            return False

        if not type(action) == ScrapeAction:
            return False

        scraped_count = session_state.totalScraped.get(action.source)
        return scraped_count is not None and scraped_count >= self.scrape_count

    def reset(self):
        pass

    def update_state(self, action):
        pass


def get_extra_limits_classes():
    return ExtraLimit.__subclasses__()
